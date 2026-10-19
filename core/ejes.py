"""Construcción de los ejes de la página de inicio (ADR 0010).

Cada número que sale de acá es una `Cifra` que lleva los Datos de los que proviene y, si es
derivada, la fórmula con la que se calculó. Lo que no tiene datos va a `pendientes`, como texto.
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from core import lentes
from core.carga import Repositorio
from core.lentes import Vigencia
from core.modelos import Dato, Evento

UNIVERSIDADES_NACIONALES = 61


@dataclass(frozen=True)
class Cifra:
    clave: str
    etiqueta: str
    valor: Decimal
    unidad: str
    periodo: str
    fuentes: tuple[Dato, ...]
    calculo: str = ""
    aviso: str = ""  # p. ej. vigencia no confirmada de una grilla (ADR 0004)

    @property
    def tipo_fuente(self) -> str:
        tipos = {d.tipo_fuente.value for d in self.fuentes}
        return tipos.pop() if len(tipos) == 1 else "mixta"


@dataclass
class Eje:
    clave: str
    titulo: str
    pregunta: str
    cifras: list[Cifra] = field(default_factory=list)
    eventos: list[Evento] = field(default_factory=list)
    supuestos: list[str] = field(default_factory=list)
    pendientes: list[str] = field(default_factory=list)
    serie: list[dict] = field(default_factory=list)
    detalle: dict = field(default_factory=dict)  # datos para el artículo "De dónde sale cada dato"

    @property
    def ultima_revision(self) -> date | None:
        fechas = [d.consultado for c in self.cifras for d in c.fuentes] + [e.consultado for e in self.eventos]
        return max(fechas, default=None)

    def cifra(self, clave: str) -> Cifra:
        return next(c for c in self.cifras if c.clave == clave)


def _directa(clave: str, etiqueta: str, dato: Dato) -> Cifra:
    return Cifra(clave, etiqueta, dato.valor, dato.unidad, dato.periodo, (dato,))


def _suma(clave: str, etiqueta: str, datos: list[Dato]) -> Cifra:
    return Cifra(clave, etiqueta, sum(d.valor for d in datos), datos[0].unidad, datos[0].periodo, tuple(datos),
                 calculo=f"Suma de {len(datos)} registros")


def _cociente(clave: str, etiqueta: str, num: Cifra, den: Cifra) -> Cifra:
    return Cifra(clave, etiqueta, num.valor / den.valor * 100, "porcentaje", num.periodo, num.fuentes + den.fuentes,
                 calculo=f"{num.etiqueta} ÷ {den.etiqueta} × 100")


def eje_ejecucion(repo: Repositorio, anio: str = "2026") -> Eje:
    eje = Eje("ejecucion", "Transferencias", f"¿Cuánto del crédito {anio} llegó a las universidades?")

    def por_universidad(indicador: str) -> list[Dato]:
        return [d for d in repo.buscar(indicador=indicador, periodo=anio, actividad="")
                if d.dimensiones.get("universidad")]

    unr, sistema, no_asignado = {}, {}, {}
    for indicador in ("credito_asignado", "credito_vigente", "devengado"):
        filas = por_universidad(indicador)
        universidades = [d for d in filas if d.entidad in ("UNR", "OTRA_UNIVERSIDAD")]
        if len(universidades) != UNIVERSIDADES_NACIONALES:
            raise ValueError(f"{indicador} {anio}: se esperaban {UNIVERSIDADES_NACIONALES} universidades, "
                             f"hay {len(universidades)}")
        unr[indicador] = next(d for d in filas if d.entidad == "UNR")
        sistema[indicador] = universidades
        no_asignado[indicador] = next(d for d in filas if d.entidad == "CREDITO_NO_ASIGNADO")

    etiquetas = {"credito_asignado": "Crédito asignado (ley)", "credito_vigente": "Crédito vigente",
                 "devengado": "Devengado"}
    for indicador, etiqueta in etiquetas.items():
        eje.cifras.append(_directa(f"unr-{indicador}", f"UNR — {etiqueta}", unr[indicador]))
    eje.cifras.append(_cociente("unr-ejecucion", "UNR — Devengado sobre vigente",
                                eje.cifra("unr-devengado"), eje.cifra("unr-credito_vigente")))

    sis_vig = _suma("sistema-credito_vigente", "61 universidades — Crédito vigente", sistema["credito_vigente"])
    sis_dev = _suma("sistema-devengado", "61 universidades — Devengado", sistema["devengado"])
    eje.cifras += [sis_vig, sis_dev,
                   _cociente("sistema-ejecucion", "61 universidades — Devengado sobre vigente", sis_dev, sis_vig)]

    eje.cifras.append(_directa("no-asignado-credito_vigente",
                               "Crédito vigente no asignado a ninguna universidad", no_asignado["credito_vigente"]))
    eje.cifras.append(_directa("no-asignado-devengado",
                               "Devengado del crédito no asignado", no_asignado["devengado"]))

    corte = date.fromisoformat(unr["devengado"].dimensiones["fecha_corte"])
    dias_anio = (date(corte.year, 12, 31) - date(corte.year, 1, 1)).days + 1
    dia = corte.timetuple().tm_yday
    eje.cifras.append(Cifra("anio-transcurrido", f"Año transcurrido al {corte:%d/%m/%Y}",
                            Decimal(dia) / Decimal(dias_anio) * 100, "porcentaje", anio, (unr["devengado"],),
                            calculo=f"Día {dia} de {dias_anio} (fecha de corte del dato)"))

    eje.supuestos = [
        "Transferencias del Tesoro (Programa 26); no incluye recursos propios.",
        "El año transcurrido es una referencia: las transferencias no son parejas mes a mes.",
        "El crédito sin universidad asignada va aparte (ADR 0013).",
    ]
    eje.pendientes = ["Lo que exigen los arts. 3 y 4 de la Ley 27.795 (gastos de funcionamiento) frente a lo "
                      "transferido."]
    return eje


MESES_ABREV = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


MESES_LARGOS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
                "noviembre", "diciembre"]


def mes_legible(periodo: str) -> str:
    """Forma compacta, para ejes de gráficos y tooltips: «ago-2026»."""
    anio, mes = periodo.split("-")
    return f"{MESES_ABREV[int(mes) - 1]}-{anio}"


def mes_largo(periodo: str) -> str:
    """Forma para leer en un texto: «agosto de 2026»."""
    anio, mes = periodo.split("-")
    return f"{MESES_LARGOS[int(mes) - 1]} de {anio}"


def _aviso_vigencia(punto: lentes.Punto) -> str:
    if punto.vigencia == Vigencia.PROPIA:
        return ""
    mes, desde = mes_largo(punto.periodo), mes_largo(punto.fuentes[0].periodo)
    if punto.vigencia == Vigencia.CONFIRMADA:
        return f"Para {mes} rige la escala de {desde}: un documento confirma que no hubo cambios."
    return (f"La UNR todavía no publicó la escala de {mes}. Usamos la de {desde}, la última disponible; "
            f"si hubo un aumento en el medio, este número cambia.")


def _desde_resultado(clave: str, etiqueta: str, unidad: str, periodo: str, r: lentes.Resultado, calculo: str,
                     aviso: str = "") -> Cifra:
    return Cifra(clave, etiqueta, r.valor, unidad, periodo, r.fuentes, calculo, aviso)


def eje_salario(repo: Repositorio) -> Eje:
    eje = Eje("salario", "Salario docente", "¿Cuánto cobra un docente frente a lo que exige la ley?")
    grillas = repo.buscar(entidad="CARGO_TESTIGO", indicador="salario_basico")
    ipc = lentes.serie_por_periodo(repo.buscar(indicador="ipc_nivel_general"))
    confirmados = {m for e in repo.eventos_de("salario") for m in e.confirma_vigencia}
    ultimo_ipc = max(ipc)
    puntos = {p.periodo: p for p in lentes.serie_vigente(grillas, ultimo_ipc, confirmados)}
    mes, legible = ultimo_ipc, mes_largo(ultimo_ipc)
    pagado = puntos[mes]
    aviso = _aviso_vigencia(pagado)

    eje.cifras.append(_desde_resultado("brecha-art5", f"Aumento necesario para cumplir el art. 5 ({legible})",
                                       "porcentaje", mes, lentes.brecha_art5(puntos, ipc, mes),
                                       "(salario exigido ÷ básico pagado − 1) × 100", aviso))
    eje.cifras.append(Cifra("pagado", f"Básico pagado ({legible})", pagado.valor, "ARS corrientes", mes,
                            pagado.fuentes, aviso=aviso))
    eje.cifras.append(_desde_resultado("exigido", f"Salario que exige el art. 5 ({legible})", "ARS corrientes", mes,
                                       lentes.salario_art5(puntos, ipc, mes),
                                       "básico nov-2023 × IPC del mes ÷ IPC nov-2023"))
    base = puntos[lentes.MES_PREVIO_ART5]
    eje.cifras.append(Cifra("basico-nov2023", "Básico de noviembre de 2023", base.valor, "ARS corrientes",
                            lentes.MES_PREVIO_ART5, base.fuentes))
    eje.cifras.append(Cifra("aumento-basico", f"Aumento del básico, de noviembre de 2023 a {legible}",
                            (pagado.valor / base.valor - 1) * 100, "porcentaje", mes, pagado.fuentes + base.fuentes,
                            f"(básico {legible} ÷ básico nov-2023 − 1) × 100", aviso))
    eje.cifras.append(Cifra("aumento-ipc", f"Aumento de precios (IPC), de noviembre de 2023 a {legible}",
                            (ipc[mes].valor / ipc[lentes.MES_PREVIO_ART5].valor - 1) * 100, "porcentaje", mes,
                            (ipc[mes], ipc[lentes.MES_PREVIO_ART5]), f"(IPC {legible} ÷ IPC nov-2023 − 1) × 100"))
    eje.cifras.append(_desde_resultado("real-nov_2023", f"Salario real de {legible} frente a noviembre de 2023", "porcentaje",
                                       mes, lentes.variacion_real(puntos, ipc, mes, "nov_2023"),
                                       "(salario real del mes ÷ salario real de nov-2023 − 1) × 100", aviso))

    for p in puntos.values():
        exigido = (lentes.salario_art5(puntos, ipc, p.periodo).valor
                   if p.periodo >= lentes.MES_PREVIO_ART5 else None)
        eje.serie.append({"periodo": p.periodo, "pagado": p.valor, "exigido": exigido,
                          "vigencia": p.vigencia.value})

    sin_grilla = [p for p in puntos.values() if p.vigencia != Vigencia.PROPIA]
    ultima_grilla = max(grillas, key=lambda d: d.periodo)
    eje.detalle = {
        "desde": mes_largo(min(puntos)), "hasta_grilla": mes_largo(ultima_grilla.periodo),
        "meses_con_grilla": len(grillas),
        "sin_grilla": [(mes_largo(p.periodo), p.vigencia.value, mes_largo(p.fuentes[0].periodo))
                       for p in sin_grilla],
        "ultima_grilla": ultima_grilla, "ipc": ipc[mes], "ultimo_ipc": legible,
        "grillas_sin_ipc": [mes_largo(d.periodo) for d in grillas if d.periodo > mes],
    }
    eje.eventos = repo.eventos_de("salario")
    eje.supuestos = [
        "Profesor adjunto, dedicación exclusiva, sin antigüedad: salario básico.",
        "Lo que exige el art. 5: el básico de nov-2023 actualizado por IPC.",
        "Último mes con IPC publicado.",
    ]
    eje.pendientes = ["Instructivos de jul-2026 y ago-2026 (no publicados en el portal de la UNR)."]
    return eje


def eje_control(repo: Repositorio) -> Eje:
    eje = Eje("control", "Control", "¿Quién audita a la UNR?")
    eje.eventos = repo.eventos_de("control")
    eje.pendientes = ["Informe AGN 161/2022 (original).", "Informes individuales de la Unidad de Auditoría Interna."]
    return eje


def eje_graduacion(repo: Repositorio) -> Eje:
    eje = Eje("graduacion", "Graduación", "¿Cuántos estudian y se reciben?")
    for dato in sorted(repo.buscar(entidad="UNR", indicador="egresados"),
                       key=lambda d: (d.dimensiones.get("nivel", ""), d.periodo)):
        nivel = dato.dimensiones["nivel"]
        eje.cifras.append(_directa(f"egresados-{nivel}-{dato.periodo}".lower().replace(" ", "-"),
                                   f"Egresados {dato.periodo} — {nivel}", dato))
    for dato in repo.buscar(entidad="UNR", indicador="alumnos"):
        nivel = dato.dimensiones["nivel"]
        eje.cifras.append(_directa(f"alumnos-{nivel}-{dato.periodo}".lower().replace("/", "-"),
                                   f"Alumnos {dato.periodo} — {nivel}", dato))
    eje.supuestos = ["Valores absolutos: no hay tasa de egreso hasta tener ingresantes por cohorte (ADR 0009)."]
    eje.pendientes = ["Ingresantes de la UNR desde 2016, para la tasa de egreso con desfase n."]
    return eje


def eje_ley(repo: Repositorio) -> Eje:
    eje = Eje("ley", "Ley 27.795", "¿En qué estado está la ley de financiamiento universitario?")
    eje.eventos = repo.eventos_de("ley")
    eje.supuestos = []
    eje.pendientes = ["Lente por artículo (arts. 3, 4 y 5) para la UNR: requiere Presupuesto Abierto 2024-2025, "
                      "IPC y grillas salariales.",
                      "Texto de la ley y del Decreto 759/2025 desde el Boletín Oficial."]
    return eje


CONSTRUCTORES = {
    "salario": eje_salario,
    "ley": eje_ley,
    "ejecucion": eje_ejecucion,
    "control": eje_control,
    "graduacion": eje_graduacion,
}


def construir_eje(repo: Repositorio, clave: str) -> Eje:
    return CONSTRUCTORES[clave](repo)


def construir_ejes(repo: Repositorio) -> dict[str, Eje]:
    return {clave: construir(repo) for clave, construir in CONSTRUCTORES.items()}
