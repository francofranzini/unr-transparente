"""Vigía de fuentes (ADR 0010 y 0032): revisa las fuentes de `data/fuentes.yaml` y avisa qué hay de nuevo.

Uso: .venv/bin/python scripts/vigia_fuentes.py [--eje ley] [--desde AAAA-MM-DD] [--salida informe.md]

No carga nada en data/: detecta y avisa. La carga sigue siendo manual y con ficha (principio 1).

Qué cuenta como novedad:
- `metodo: enlaces` (páginas sin fecha, p. ej. InfoLEG): un enlace que cumple `patron` (y `filtro`, si lo hay) y que
  no está citado en ningún evento de data/eventos/ ni en el `ignorar` de la fuente.
- `metodo: feed` (RSS con fecha): una entrada publicada desde la última revisión del eje (la fecha de su evento de
  `estado`, o `--desde`) que cumple `filtro` y no está citada ni ignorada.

Si hay novedades o fuentes que no respondieron, escribe el informe en Markdown (en `--salida` o en pantalla).
Sin novedades, no escribe el archivo: el workflow usa eso para decidir si avisa.
"""

import argparse
import html
import re
import sys
from dataclasses import dataclass
from datetime import date
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx
import yaml

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from core.carga import cargar  # noqa: E402

FUENTES = RAIZ / "data" / "fuentes.yaml"
METODOS = {"enlaces", "feed"}
CAMPOS = {"id", "eje", "nombre", "url", "metodo"}
URL_EN_TEXTO = re.compile(r"https?://[^\s\"'»)]+")
MAX_POR_FUENTE = 15


@dataclass(frozen=True)
class Novedad:
    titulo: str
    url: str
    fecha: str = ""


def normalizar_url(url: str) -> str:
    """Para comparar enlaces: sin `;jsessionid`, sin fragmento ni barra final, esquema y dominio en minúsculas."""
    url = html.unescape(url.strip()).rstrip(".,;")
    url = re.sub(r";jsessionid=[^?#]*", "", url, flags=re.I)
    partes = urlsplit(url)
    ruta = partes.path.rstrip("/") or "/"
    return urlunsplit(("https" if partes.scheme in ("http", "https") else partes.scheme, partes.netloc.lower(), ruta,
                       partes.query, ""))


def texto_plano(fragmento: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragmento)).split())


def normalizar_titulo(titulo: str) -> str:
    """Google Noticias agrega « - Medio» al final del título; se compara sin eso, sin mayúsculas ni comillas."""
    titulo = re.sub(r"\s+[-–—]\s+(?:(?!\s[-–—]\s).){2,60}$", "", html.unescape(titulo).strip())
    return " ".join(re.sub(r"[«»“”\"'.…]", "", titulo).lower().split())


def conocidos(directorio: Path | None = None) -> set[str]:
    """Todo enlace citado en un evento (ficha, noticias y los que aparecen en la nota) y los títulos de sus noticias."""
    repo = cargar(directorio) if directorio else cargar()
    urls, titulos = set(), set()
    for e in repo.eventos:
        urls.add(e.url)
        urls.update(n.url for n in e.noticias)
        urls.update(URL_EN_TEXTO.findall(e.nota))
        titulos.update(normalizar_titulo(n.titulo) for n in e.noticias)
    return {normalizar_url(u) for u in urls} | {f"titulo:{t}" for t in titulos}


def ultima_revision(eje: str, directorio: Path | None = None) -> date | None:
    """Fecha del evento de estado del eje: hasta ahí llegó la última revisión cargada."""
    repo = cargar(directorio) if directorio else cargar()
    estados = [e.fecha for e in repo.eventos_de(eje) if e.tipo == "estado" and len(e.fecha) == 10]
    return date.fromisoformat(max(estados)) if estados else None


def extraer_enlaces(pagina: str, base: str, patron: str, filtro: str = "", bloque: str = "") -> list[Novedad]:
    """Enlaces de una página. Con `bloque` (p. ej. "tr"), el título y el filtro usan el texto de cada fila."""
    trozos = [f"<{bloque}{t}" for t in re.split(rf"<{bloque}\b", pagina, flags=re.I)] if bloque else [pagina]
    vistos, salida = set(), []
    for trozo in trozos:
        texto_trozo = texto_plano(trozo)
        if bloque and filtro and not re.search(filtro, texto_trozo, re.I):
            continue
        for m in re.finditer(r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", trozo, re.I | re.S):
            href, ancla = m.group(1), texto_plano(m.group(2))
            if not re.search(patron, href):
                continue
            titulo = texto_trozo if bloque else ancla
            if not bloque and filtro and not re.search(filtro, ancla, re.I):
                continue
            url = urljoin(base, href)
            if normalizar_url(url) in vistos:
                continue
            vistos.add(normalizar_url(url))
            salida.append(Novedad(titulo[:300], url))
    return salida


def extraer_feed(xml: str, filtro: str = "", desde: date | None = None) -> list[Novedad]:
    """Entradas de un RSS. Se quedan las publicadas desde `desde` y cuyo título o descripción cumplen `filtro`."""
    salida = []
    for item in re.findall(r"<item\b.*?</item>", xml, re.S | re.I):
        def campo(nombre: str) -> str:
            m = re.search(rf"<{nombre}\b[^>]*>(.*?)</{nombre}>", item, re.S | re.I)
            return html.unescape(re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", m.group(1), flags=re.S)).strip() if m else ""

        titulo, enlace, descripcion, publicado = campo("title"), campo("link"), campo("description"), campo("pubDate")
        fecha = parsedate_to_datetime(publicado).date() if publicado else None
        if desde and fecha and fecha < desde:
            continue
        if filtro and not re.search(filtro, f"{titulo} {texto_plano(descripcion)}", re.I):
            continue
        salida.append(Novedad(texto_plano(titulo), enlace, fecha.isoformat() if fecha else ""))
    return salida


def leer_fuentes(eje: str = "", archivo: Path = FUENTES) -> list[dict]:
    fuentes = yaml.safe_load(archivo.read_text(encoding="utf-8")) or []
    for f in fuentes:
        faltan = CAMPOS - set(f)
        if faltan:
            raise ValueError(f"{archivo.name}: la fuente {f.get('id')} no tiene {sorted(faltan)}")
        if f["metodo"] not in METODOS:
            raise ValueError(f"{archivo.name}: {f['id']}: método desconocido {f['metodo']!r}")
        for clave in ("patron", "filtro"):
            if f.get(clave):
                re.compile(f[clave])
    return [f for f in fuentes if not eje or f["eje"] == eje]


def novedades_de(fuente: dict, contenido: str, conocidas: set[str], desde: date | None) -> list[Novedad]:
    if fuente["metodo"] == "enlaces":
        candidatas = extraer_enlaces(contenido, fuente["url"], fuente.get("patron", ""), fuente.get("filtro", ""),
                                     fuente.get("bloque", ""))
    else:
        candidatas = extraer_feed(contenido, fuente.get("filtro", ""), desde)
    descartar = conocidas | {normalizar_url(u) for u in fuente.get("ignorar", [])}
    return [n for n in candidatas
            if normalizar_url(n.url) not in descartar and f"titulo:{normalizar_titulo(n.titulo)}" not in descartar]


def informe(eje: str, desde: date | None, resultados: list[tuple[dict, list[Novedad]]], fallas: list[str]) -> str:
    lineas = [f"Revisión automática del {date.today():%d/%m/%Y}."]
    if desde:
        lineas.append(f"En los feeds se buscó lo publicado desde la última revisión cargada ({desde:%d/%m/%Y}).")
    lineas.append("")
    for fuente, novedades in resultados:
        if not novedades:
            continue
        lineas.append(f"### {fuente['nombre']}")
        for n in novedades[:MAX_POR_FUENTE]:
            lineas.append(f"- [ ] [{n.titulo}]({n.url})" + (f" · {n.fecha}" if n.fecha else ""))
        if len(novedades) > MAX_POR_FUENTE:
            lineas.append(f"- … y {len(novedades) - MAX_POR_FUENTE} más en {fuente['url']}")
        lineas.append("")
    if fallas:
        lineas.append("### Fuentes que no respondieron (revisar a mano)")
        lineas += [f"- {f}" for f in fallas] + [""]
    lineas += [
        "### Antes de cargar un hecho (ADR 0032)",
        "1. Buscar el original: Boletín Oficial, acta de votación de la cámara o texto de la resolución.",
        "2. Sin original: `tipo_fuente: secundaria`, con 2 o más medios de líneas editoriales distintas y la nota "
        "«Texto de la resolución: pendiente».",
        "3. Citas literales del documento, no de la prensa.",
        "4. Cargar el evento en `data/eventos/ley.yaml` (y su sello en `SELLOS_LEY`, sin cifras, si corresponde).",
        "5. Reemplazar el evento de `estado` con la fecha del día.",
        "6. Correr `scripts/validar_datos.py`, `pytest`, `scripts/verificar_titulos.py` y `scripts/archivar_fuentes.py`.",
        "7. Abrir un pull request para que lo revise otra persona.",
        "",
        "Si algo de esta lista no corresponde a un hecho de la cronología, agregar su enlace al `ignorar` de la fuente "
        "en `data/fuentes.yaml`.",
    ]
    return "\n".join(lineas)


def main() -> int:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--eje", default="ley")
    argumentos.add_argument("--desde", type=date.fromisoformat, help="por defecto, la fecha del evento de estado del eje")
    argumentos.add_argument("--salida", type=Path)
    opciones = argumentos.parse_args()

    desde = opciones.desde or ultima_revision(opciones.eje)
    conocidas = conocidos()
    resultados, fallas = [], []
    with httpx.Client(follow_redirects=True, timeout=30, headers={"User-Agent": "Mozilla/5.0 (vigia de fuentes)"}) as c:
        for fuente in leer_fuentes(opciones.eje):
            try:
                r = c.get(fuente["url"])
                r.raise_for_status()
            except httpx.HTTPError as e:
                fallas.append(f"{fuente['nombre']}: {e.__class__.__name__} ({fuente['url']})")
                continue
            resultados.append((fuente, novedades_de(fuente, r.text, conocidas, desde)))

    total = sum(len(n) for _, n in resultados)
    print(f"{opciones.eje}: {total} novedades en {len(resultados)} fuentes; {len(fallas)} sin respuesta.")
    if not total and not fallas:
        return 0
    texto = informe(opciones.eje, desde, resultados, fallas)
    if opciones.salida:
        opciones.salida.write_text(texto + "\n", encoding="utf-8")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
