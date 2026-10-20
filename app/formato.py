"""Formato de números en castellano rioplatense (punto de miles, coma decimal)."""

import re
from decimal import ROUND_HALF_UP, Decimal

from core.ejes import Cifra, etiqueta_tipo

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def _agrupar(valor: Decimal, decimales: int) -> str:
    cuantizado = valor.quantize(Decimal(1).scaleb(-decimales), rounding=ROUND_HALF_UP)
    entero, _, fraccion = f"{abs(cuantizado):f}".partition(".")
    grupos = f"{int(entero):,}".replace(",", ".")
    signo = "−" if cuantizado < 0 else ""
    return f"{signo}{grupos},{fraccion}" if fraccion else f"{signo}{grupos}"


def numero(valor: Decimal, decimales: int = 0) -> str:
    return _agrupar(valor, decimales)


def pesos_corto(valor: Decimal) -> str:
    if abs(valor) >= 10**12:
        return f"$ {_agrupar(valor / 10**12, 2)} billones"
    if abs(valor) >= 10**9:
        return f"$ {_agrupar(valor / 10**6, 0)} millones"
    return f"$ {_agrupar(valor, 0)}"


def cifra_corta(c: Cifra) -> str:
    """Versión para lectura rápida. El valor exacto está siempre en la ficha."""
    if c.unidad == "porcentaje":
        return f"{_agrupar(c.valor, 1)} %"
    if c.unidad == "ARS corrientes":
        return pesos_corto(c.valor)
    return _agrupar(c.valor, 0)


def cifra_exacta(c: Cifra) -> str:
    if c.unidad == "porcentaje":
        return f"{_agrupar(c.valor, 4)} %"
    if c.unidad == "ARS corrientes":
        return f"$ {_agrupar(c.valor, 2)}"
    return _agrupar(c.valor, 0)


def composicion(c: Cifra, maximo: int = 12) -> list[tuple[str, Decimal]]:
    """(concepto, monto) de cada registro, cuando la cifra es exactamente su suma; si no, vacía.

    Sirve para que la ficha muestre de qué se compone un total (p. ej. la partida de los arts. 3 y 4)."""
    fuentes = c.fuentes
    if c.unidad != "ARS corrientes" or not 1 < len(fuentes) <= maximo or sum(d.valor for d in fuentes) != c.valor:
        return []
    return [(d.dimensiones["actividad"] if "actividad" in d.dimensiones else d.indicador, d.valor) for d in fuentes]


def origenes(c: Cifra) -> list[tuple[str, str, int | None]]:
    """(nombre corto, enlace, página) de cada documento distinto del que sale la cifra, para la vista breve.

    El nombre corto es el del documento hasta el primer «:» o «(»; el enlace, el sitio oficial si lo hay. Si dos
    documentos distintos comparten nombre corto (dos instructivos de la SPU), se agrega el período de cada uno."""
    vistos: dict[tuple[str, str], tuple[str, str, int | None, str]] = {}
    for d in c.fuentes:
        corto = re.split(r":| \(", d.documento, maxsplit=1)[0].strip()
        s = sitio(d.url)
        vistos.setdefault((corto, d.documento if not s else corto), (corto, s[1] if s else d.url, d.pagina, d.periodo))
    nombres = [corto for corto, *_ in vistos.values()]
    return [(f"{corto}, {fecha_evento(periodo)}" if nombres.count(corto) > 1 else corto, enlace, pagina)
            for corto, enlace, pagina, periodo in vistos.values()]


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


def tipo_evento(tipo: str) -> str:
    """Etiqueta legible del tipo de un Evento («judicial» → «Resolución judicial»; ADR 0037)."""
    return etiqueta_tipo(tipo)
