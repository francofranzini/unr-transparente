"""Carga automática de novedades verificables de la Ley 27.795 (ADR 0036). Lo corre .github/workflows/vigia.yml.

Uso: .venv/bin/python scripts/actualizar_ley.py [--solo-revisar] [--salida informe.md]

Qué publica solo, en data/eventos/ley.yaml:
- Normas que InfoLEG vincula a la ley (fuentes con `carga: norma`): un hito `primaria` con el texto del registro.
- Votaciones del Senado sobre la ley (`carga: votacion`): un hito `primaria` con el resultado del acta oficial.
- Notas de prensa de los medios con feed (`carga: prensa`): se suman a «Cómo lo contaron» de un hito solo si el título
  se leyó de la página de la nota, la nota es de hasta 3 días después del hito y coincide con las claves de ese hito y de
  ningún otro (data/vigia/claves_ley.yaml).
Y actualiza la fecha de consulta de las fuentes (data/vigia/estado_ley.yaml), una vez por día.

Lo que no se puede verificar así (hechos nuevos que solo cuenta la prensa, notas que no coinciden con un hito, fuentes
que no responden) no se publica: va al informe, que el workflow deja en el issue «vigia-ley».
Después de correrlo hay que pasar scripts/validar_datos.py y pytest: si fallan, el workflow descarta los cambios.
"""

import argparse
import hashlib
import html
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urljoin

import httpx
import yaml

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
sys.path.insert(0, str(RAIZ))

import verificar_titulos  # noqa: E402
import vigia_fuentes as vigia  # noqa: E402
from core.carga import cargar  # noqa: E402

LEY = RAIZ / "data" / "eventos" / "ley.yaml"
CLAVES = RAIZ / "data" / "vigia" / "claves_ley.yaml"
ESTADO = RAIZ / "data" / "vigia" / "estado_ley.yaml"
ARGENTINA = timezone(timedelta(hours=-3))
VENTANA = timedelta(days=3)
FILTRO_PRENSA = r"financiamiento\s+(de\s+la\s+educaci[oó]n\s+)?universitari|27\.795|ley\s+de\s+financiamiento"
MESES = {m: i for i, m in enumerate(["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"], 1)}
q = lambda texto: json.dumps(texto, ensure_ascii=False)  # noqa: E731  (cadena YAML con comillas dobles)


@dataclass
class Resultado:
    hitos: list[str] = field(default_factory=list)        # ids de hitos nuevos
    noticias: list[str] = field(default_factory=list)     # «medio: título → hito»
    pendientes: list[str] = field(default_factory=list)   # para revisar a mano (no publicado)
    fallas: list[str] = field(default_factory=list)       # fuentes que no respondieron
    fecha_actualizada: bool = False

    @property
    def publicado(self) -> bool:
        return bool(self.hitos or self.noticias or self.fecha_actualizada)


# --- Lectura de fuentes oficiales ---------------------------------------------------------------------------------

@dataclass(frozen=True)
class Norma:
    numero: str
    dependencia: str
    fecha: str
    descripcion: str
    url: str


def leer_normas_infoleg(pagina: str, base: str) -> list[Norma]:
    """Filas de «Normas que modifican y/o complementan» de InfoLEG: número, dependencia, fecha y descripción."""
    normas = []
    for fila in re.findall(r"<tr\b.*?</tr>", pagina, re.S | re.I):
        celdas = re.findall(r"<td\b[^>]*>(.*?)</td>", fila, re.S | re.I)
        enlace = re.search(r'href="([^"]*verNorma\.do[^"]*\?id=\d+)"[^>]*>(.*?)</a>', fila, re.S | re.I)
        if len(celdas) < 3 or not enlace:
            continue
        numero = vigia.texto_plano(enlace.group(2))
        dependencia = vigia.texto_plano(celdas[0]).replace(numero, "", 1).strip()
        m = re.match(r"(\d{1,2})-([a-z]{3})-(\d{4})", vigia.texto_plano(celdas[1]).lower())
        if not m or m.group(2) not in MESES:
            continue
        fecha = f"{m.group(3)}-{MESES[m.group(2)]:02d}-{int(m.group(1)):02d}"
        normas.append(Norma(numero, dependencia, fecha, vigia.texto_plano(celdas[2]),
                            vigia.normalizar_url(urljoin(base, enlace.group(1)))))
    return normas


@dataclass(frozen=True)
class Votacion:
    acta: str
    titulo: str
    fecha: str
    mayoria: str
    resultado: str
    afirmativos: int
    negativos: int
    abstenciones: int
    ausentes: int
    url: str


def leer_acta_senado(pagina: str, url: str) -> Votacion | None:
    """Detalle de un acta de votación del Senado (senado.gob.ar/votaciones/detalleActa/N)."""
    texto = vigia.texto_plano(pagina)
    m = re.search(r"Acta Nro:\s*(\d+)\s+(.+?)\s+(\d{2})/(\d{2})/(\d{4})\s*-\s*\d{2}:\d{2}\s+(.+?)\s+(AFIRMATIVO|NEGATIVO)\b"
                  r".*?(\d+)\s+AFIRMATIVOS\s+(\d+)\s+NEGATIVOS\s+(\d+)\s+ABSTENCIONES\s+(\d+)\s+AUSENTES", texto, re.S)
    if not m:
        return None
    # El título termina donde empieza el expediente («O.D. 424/2025», «CD-20/25-CD»).
    titulo = re.split(r"\s(?:O\.D\.\s*\d+/\d+|[A-Z]{1,3}-\d+/\d+\S*)", m.group(2))[0].strip().rstrip(".")
    return Votacion(m.group(1), titulo, f"{m.group(5)}-{m.group(4)}-{m.group(3)}", m.group(6).strip().capitalize(),
                    m.group(7).lower(), *(int(m.group(i)) for i in range(8, 12)), url)


# --- Escritura en ley.yaml (texto, para conservar el formato y los comentarios) -----------------------------------

def bloque_evento(id_: str, fecha: str, tipo: str, titulo: str, documento: str, url: str, nota: str) -> str:
    return "\n".join([
        f"- id: {id_}", f'  fecha: "{fecha}"', f"  tipo: {tipo}", "  ejes: [ley]", f"  titulo: {q(titulo)}",
        "  tipo_fuente: primaria", f"  documento: {q(documento)}", f"  url: {url}",
        f"  consultado: {date.today().isoformat()}", f"  nota: {q(nota)}",
    ]) + "\n\n"


def agregar_evento(texto: str, bloque: str) -> str:
    """Antes del evento de estado, para que el archivo siga en orden y el estado quede al final."""
    i = texto.find("\n- id: estado-")
    return texto.rstrip("\n") + "\n\n" + bloque if i == -1 else texto[:i + 1] + bloque + texto[i + 1:]


def agregar_noticia(texto: str, evento_id: str, medio: str, titulo: str, url: str, fecha: str) -> str:
    inicio = texto.index(f"- id: {evento_id}\n")
    fin = texto.find("\n- id: ", inicio + 1)
    fin = len(texto) if fin == -1 else fin + 1
    bloque = texto[inicio:fin].rstrip("\n")
    if "\n  noticias:" not in bloque:
        bloque += "\n  noticias:"
    bloque += f"\n    - {{medio: {q(medio)}, titulo: {q(titulo)}, url: {q(url)}, fecha: {q(fecha)}}}"
    return texto[:inicio] + bloque + ("\n\n" if fin < len(texto) else "\n") + texto[fin:].lstrip("\n")


# --- Prensa: a qué hito corresponde una nota -----------------------------------------------------------------------

def hito_de_nota(titulo: str, fecha: date, hitos: list, claves: dict[str, str]) -> tuple[str | None, str]:
    """Devuelve (id del hito, motivo). Solo si la nota coincide con un único hito de los 3 días anteriores."""
    candidatos = [h for h in hitos if len(h.fecha) == 10 and
                  timedelta(0) <= fecha - date.fromisoformat(h.fecha) <= VENTANA]
    if not candidatos:
        return None, "no hay un hito cargado en los 3 días anteriores (¿hecho nuevo?)"
    coinciden = [h.id for h in candidatos if claves.get(h.id) and re.search(claves[h.id], titulo, re.I)]
    if len(coinciden) == 1:
        return coinciden[0], ""
    if not coinciden:
        return None, f"no coincide con las claves de {', '.join(h.id for h in candidatos)}"
    return None, f"coincide con más de un hito ({', '.join(coinciden)})"


def fecha_argentina(publicado: str) -> date | None:
    """Fecha local de una publicación: acepta la de un RSS («Tue, 20 Oct 2026 10:00:00 GMT») y la ISO de un sitemap."""
    try:
        momento = parsedate_to_datetime(publicado)
    except (TypeError, ValueError):
        try:
            momento = datetime.fromisoformat(publicado.replace("Z", "+00:00"))
        except ValueError:
            return None
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=ARGENTINA)
    return momento.astimezone(ARGENTINA).date()


def _campo(bloque: str, nombre: str) -> str:
    m = re.search(rf"<{nombre}\b[^>]*>(.*?)</{nombre}>", bloque, re.S | re.I)
    return html.unescape(re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", m.group(1), flags=re.S)).strip() if m else ""


def entradas_feed(xml: str) -> list[tuple[str, str, str]]:
    """(título, enlace, fecha de publicación) de cada entrada de un RSS o de un mapa de noticias (news sitemap)."""
    if re.search(r"<urlset\b", xml):
        return [(vigia.texto_plano(_campo(u, "news:title")), _campo(u, "loc"), _campo(u, "news:publication_date"))
                for u in re.findall(r"<url\b.*?</url>", xml, re.S | re.I)]
    return [(vigia.texto_plano(_campo(i, "title")), _campo(i, "link"), _campo(i, "pubDate"))
            for i in re.findall(r"<item\b.*?</item>", xml, re.S | re.I)]


# --- Estado del vigía ----------------------------------------------------------------------------------------------

def leer_estado() -> dict:
    return yaml.safe_load(ESTADO.read_text(encoding="utf-8")) or {} if ESTADO.exists() else {}


def escribir_estado(estado: dict) -> None:
    ESTADO.write_text("# Lo escribe scripts/actualizar_ley.py (ADR 0036): última consulta de las fuentes y claves de los "
                      "hitos cargados solos.\n" + yaml.safe_dump(estado, allow_unicode=True, sort_keys=False, width=200),
                      encoding="utf-8")


# --- Corrida -------------------------------------------------------------------------------------------------------

def actualizar(cliente: httpx.Client, solo_revisar: bool = False) -> Resultado:
    resultado = Resultado()
    texto = LEY.read_text(encoding="utf-8")
    repo = cargar()
    eventos = repo.eventos_de("ley")
    hitos = [e for e in eventos if e.tipo != "estado"]
    conocidos = vigia.conocidos()
    estado = leer_estado()
    claves = {**(yaml.safe_load(CLAVES.read_text(encoding="utf-8")) or {}), **estado.get("claves", {})}
    ultima = estado.get("consultado") or max((e.fecha for e in eventos if e.tipo == "estado"), default=None)
    desde = (date.fromisoformat(str(ultima)) if ultima else date.today()) - timedelta(days=1)
    ids = {e.id for e in repo.eventos}
    avisados = set(estado.get("avisados", []))

    def pendiente(enlace: str, texto_aviso: str) -> None:
        """Cada cosa se avisa una sola vez en el issue, aunque el workflow corra cada 3 horas."""
        clave = hashlib.sha1((vigia.normalizar_url(enlace) if enlace else texto_aviso).encode()).hexdigest()[:16]
        if clave in avisados:
            return
        avisados.add(clave)
        resultado.pendientes.append(texto_aviso)

    for fuente in vigia.leer_fuentes("ley"):
        carga = fuente.get("carga", "aviso")
        try:
            r = cliente.get(fuente["url"])
            r.raise_for_status()
        except httpx.HTTPError as e:
            resultado.fallas.append(f"{fuente['nombre']}: {e.__class__.__name__}")
            continue
        contenido = r.content.decode(r.encoding or "utf-8", errors="replace") if carga == "norma" else r.text
        ignorar = {vigia.normalizar_url(u) for u in fuente.get("ignorar", [])}

        if carga == "norma":
            for norma in leer_normas_infoleg(contenido, fuente["url"]):
                if norma.url in conocidos | ignorar:
                    continue
                id_ = "ley-27795-" + re.sub(r"[^a-z0-9]+", "-", norma.numero.lower()).strip("-")
                if id_ in ids:
                    continue
                titulo = f"{norma.numero} ({norma.dependencia.title()}): {norma.descripcion.capitalize()}"
                texto = agregar_evento(texto, bloque_evento(
                    id_, norma.fecha, "norma", titulo, f"InfoLEG — {norma.numero}", norma.url,
                    f"Cargado automáticamente desde InfoLEG (normas vinculadas a la Ley 27.795). Texto del registro: «{norma.descripcion}»."))
                estado.setdefault("claves", {})[id_] = re.escape(norma.numero.split()[-1])
                ids.add(id_)
                resultado.hitos.append(f"{id_} · {titulo}")

        elif carga == "votacion":
            for candidata in vigia.novedades_de(fuente, contenido, conocidos, None):
                try:
                    detalle = cliente.get(candidata.url)
                    detalle.raise_for_status()
                except httpx.HTTPError as e:
                    resultado.fallas.append(f"Acta {candidata.url}: {e.__class__.__name__}")
                    continue
                v = leer_acta_senado(detalle.text, candidata.url)
                if v is None:
                    pendiente(candidata.url, f"Acta del Senado sin formato reconocido: {candidata.url}")
                    continue
                id_ = f"ley-27795-senado-acta-{v.fecha[:4]}-{v.acta}"
                if id_ in ids:
                    continue
                titulo = f"Senado: {v.titulo} — resultado {v.resultado}"
                nota = (f"Mayoría requerida: {v.mayoria.lower()}. {v.afirmativos} votos afirmativos, {v.negativos} negativos, "
                        f"{v.abstenciones} abstenciones y {v.ausentes} ausentes. Cargado automáticamente desde el acta oficial.")
                texto = agregar_evento(texto, bloque_evento(id_, v.fecha, "legislativo", titulo,
                                                            f"Senado de la Nación — Acta de votación N.º {v.acta}", v.url, nota))
                estado.setdefault("claves", {})[id_] = "Senado"
                ids.add(id_)
                resultado.hitos.append(f"{id_} · {titulo}")

        elif carga == "prensa":
            medio = fuente["medio"]
            for titulo_feed, enlace, publicado in entradas_feed(contenido):
                fecha = fecha_argentina(publicado)
                if not enlace or not fecha or fecha < desde:
                    continue
                if not re.search(FILTRO_PRENSA, titulo_feed, re.I):
                    continue
                url = vigia.normalizar_url(enlace)
                if url in conocidos or f"titulo:{vigia.normalizar_titulo(titulo_feed)}" in conocidos:
                    continue
                titulo = verificar_titulos.og_title(cliente, enlace)
                if not titulo:
                    pendiente(enlace, f"{medio}: no se pudo leer el título de la página · {enlace}")
                    continue
                hito, motivo = hito_de_nota(titulo, fecha, hitos, claves)
                if hito is None:
                    pendiente(enlace, f"{medio} ({fecha:%d/%m}): [{titulo}]({enlace}) — {motivo}")
                    continue
                if any(n.medio == medio for n in next(h for h in hitos if h.id == hito).noticias):
                    continue
                texto = agregar_noticia(texto, hito, medio, titulo, enlace, fecha.isoformat())
                conocidos.add(url)
                resultado.noticias.append(f"{medio}: {titulo} → {hito}")

        else:  # aviso: solo informe
            for n in vigia.novedades_de(fuente, contenido, conocidos, desde):
                pendiente(n.url, f"{fuente['nombre']}: [{n.titulo}]({n.url})" + (f" · {n.fecha}" if n.fecha else ""))

    estado["avisados"] = sorted(avisados)[-5000:]  # huellas cortas de lo ya avisado
    hoy = date.today().isoformat()
    if str(estado.get("consultado")) != hoy:
        estado["consultado"] = hoy
        resultado.fecha_actualizada = True
    if not solo_revisar:
        LEY.write_text(texto, encoding="utf-8")
        escribir_estado(estado)
    return resultado


def informe(r: Resultado) -> str:
    lineas = [f"Corrida del {datetime.now(ARGENTINA):%d/%m/%Y %H:%M} (hora de Argentina).", ""]
    if r.hitos or r.noticias:
        lineas.append("### Publicado automáticamente")
        lineas += [f"- Hito nuevo: {h}" for h in r.hitos] + [f"- Nota sumada: {n}" for n in r.noticias] + [""]
    if r.pendientes:
        lineas.append("### Para revisar a mano (no publicado)")
        lineas += [f"- [ ] {p}" for p in r.pendientes] + [""]
    if r.fallas:
        lineas.append("### Fuentes que no respondieron")
        lineas += [f"- {f}" for f in r.fallas] + [""]
    lineas.append("Procedimiento para cargar un hecho a mano: ADR 0035. Lo publicado solo: ADR 0036.")
    return "\n".join(lineas)


def main() -> int:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--solo-revisar", action="store_true", help="no escribe nada; solo informa")
    argumentos.add_argument("--salida", type=Path, help="informe en Markdown, si hay algo para avisar")
    opciones = argumentos.parse_args()
    with httpx.Client(follow_redirects=True, timeout=30, headers={"User-Agent": "Mozilla/5.0 (vigia de fuentes)"}) as c:
        r = actualizar(c, opciones.solo_revisar)
    print(f"Hitos nuevos: {len(r.hitos)} · notas sumadas: {len(r.noticias)} · para revisar: {len(r.pendientes)} · "
          f"fuentes sin respuesta: {len(r.fallas)} · fecha de consulta {'actualizada' if r.fecha_actualizada else 'sin cambios'}.")
    if r.hitos or r.noticias or r.pendientes or r.fallas:
        texto = informe(r)
        if opciones.salida:
            opciones.salida.write_text(texto + "\n", encoding="utf-8")
        else:
            print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
