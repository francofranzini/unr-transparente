"""Formato de números en castellano rioplatense (punto de miles, coma decimal)."""

from decimal import ROUND_HALF_UP, Decimal

from core.ejes import Cifra

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def _agrupar(valor: Decimal, decimales: int) -> str:
    cuantizado = valor.quantize(Decimal(1).scaleb(-decimales), rounding=ROUND_HALF_UP)
    entero, _, fraccion = f"{abs(cuantizado):f}".partition(".")
    grupos = f"{int(entero):,}".replace(",", ".")
    signo = "−" if cuantizado < 0 else ""
    return f"{signo}{grupos},{fraccion}" if fraccion else f"{signo}{grupos}"


def numero(valor: Decimal, decimales: int = 0) -> str:
    return _agrupar(valor, decimales)


def cifra_corta(c: Cifra) -> str:
    """Versión para lectura rápida. El valor exacto está siempre en la ficha."""
    if c.unidad == "porcentaje":
        return f"{_agrupar(c.valor, 1)} %"
    if c.unidad == "ARS corrientes":
        if abs(c.valor) >= 10**12:
            return f"$ {_agrupar(c.valor / 10**12, 2)} billones"
        if abs(c.valor) >= 10**9:
            return f"$ {_agrupar(c.valor / 10**6, 0)} millones"
        return f"$ {_agrupar(c.valor, 0)}"
    return _agrupar(c.valor, 0)


def cifra_exacta(c: Cifra) -> str:
    if c.unidad == "porcentaje":
        return f"{_agrupar(c.valor, 4)} %"
    if c.unidad == "ARS corrientes":
        return f"$ {_agrupar(c.valor, 2)}"
    return _agrupar(c.valor, 0)


def fecha_evento(fecha: str) -> str:
    partes = fecha.split("-")
    if len(partes) == 3:
        return f"{int(partes[2])} {MESES[int(partes[1]) - 1]} {partes[0]}"
    if len(partes) == 2:
        return f"{MESES[int(partes[1]) - 1]} {partes[0]}"
    return partes[0]


# Algunas fichas apuntan a un archivo de datos (un ZIP, un JSON): sirven para reproducir el número, no para que una
# persona verifique la fuente. Para esas, la ficha lleva primero al sitio oficial y deja la descarga como secundaria.
SITIOS = (
    ("https://dgsiaf-repo.mecon.gob.ar/repository/pa/", "Presupuesto Abierto (Ministerio de Economía)",
     "https://www.presupuestoabierto.gob.ar/sici/datos-abiertos"),
    ("https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26", "Índice de precios al consumidor (INDEC)",
     "https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31"),
)


def sitio(url: str) -> tuple[str, str] | None:
    """(nombre, url) del sitio oficial donde se publica un archivo de datos, o None si la URL ya es la página."""
    for prefijo, nombre, pagina in SITIOS:
        if url.startswith(prefijo):
            return nombre, pagina
    return None
