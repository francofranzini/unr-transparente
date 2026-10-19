"""Lentes: funciones puras sobre series de Datos. Cada resultado lleva la lista de supuestos aplicados.

Ver ADR 0004 (vigencia de grillas), 0011 (base salarial 2023) y 0014/0015 (Ley 27.795, art. 5).
"""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum

from core.modelos import Dato


class Vigencia(StrEnum):
    PROPIA = "propia"                      # el mes tiene su propia grilla
    CONFIRMADA = "confirmada"              # rige la anterior y un documento confirma que no hubo cambio
    NO_CONFIRMADA = "no_confirmada"        # rige la anterior, sin documento que lo confirme


@dataclass(frozen=True)
class Punto:
    periodo: str
    valor: Decimal
    fuentes: tuple[Dato, ...]
    vigencia: Vigencia = Vigencia.PROPIA


@dataclass
class Resultado:
    valor: Decimal
    fuentes: tuple[Dato, ...]
    supuestos: list[str] = field(default_factory=list)


def _meses(desde: str, hasta: str) -> list[str]:
    anio, mes = map(int, desde.split("-"))
    fin = tuple(map(int, hasta.split("-")))
    meses = []
    while (anio, mes) <= fin:
        meses.append(f"{anio}-{mes:02d}")
        anio, mes = (anio + 1, 1) if mes == 12 else (anio, mes + 1)
    return meses


def serie_por_periodo(datos: list[Dato]) -> dict[str, Dato]:
    serie = {}
    for dato in datos:
        if dato.periodo in serie:
            raise ValueError(f"Dos datos para {dato.periodo}: {serie[dato.periodo].id} y {dato.id}")
        serie[dato.periodo] = dato
    return serie


def serie_vigente(grillas: list[Dato], hasta: str, confirmados: set[str] = frozenset()) -> list[Punto]:
    """Extiende cada grilla hasta la siguiente (ADR 0004). No interpola."""
    por_mes = serie_por_periodo(grillas)
    puntos, vigente = [], None
    for mes in _meses(min(por_mes), hasta):
        if mes in por_mes:
            vigente = por_mes[mes]
            puntos.append(Punto(mes, vigente.valor, (vigente,)))
        else:
            estado = Vigencia.CONFIRMADA if mes in confirmados else Vigencia.NO_CONFIRMADA
            puntos.append(Punto(mes, vigente.valor, (vigente,), estado))
    return puntos


def deflactar(punto: Punto, ipc: dict[str, Dato]) -> Resultado:
    indice = ipc[punto.periodo]
    return Resultado(punto.valor / indice.valor, punto.fuentes + (indice,))


BASES_SALARIALES = {
    "promedio_2023": "promedio de 2023",
    "nov_2023": "noviembre de 2023",
    "dic_2023": "diciembre de 2023",
}


def salario_real_base(puntos: dict[str, Punto], ipc: dict[str, Dato], base: str) -> Resultado:
    """Salario real del período base, en pesos constantes del índice (ADR 0011)."""
    if base == "promedio_2023":
        reales = [deflactar(puntos[m], ipc) for m in _meses("2023-01", "2023-12")]
        valor = sum(r.valor for r in reales) / len(reales)
        fuentes = tuple(d for r in reales for d in r.fuentes)
        return Resultado(valor, fuentes, ["Base: promedio de los 12 salarios reales de 2023."])
    mes = {"nov_2023": "2023-11", "dic_2023": "2023-12"}[base]
    r = deflactar(puntos[mes], ipc)
    return Resultado(r.valor, r.fuentes, [f"Base: {BASES_SALARIALES[base]}."])


def variacion_real(puntos: dict[str, Punto], ipc: dict[str, Dato], mes: str, base: str) -> Resultado:
    """Variación porcentual del salario real del mes respecto de la base."""
    actual = deflactar(puntos[mes], ipc)
    referencia = salario_real_base(puntos, ipc, base)
    valor = (actual.valor / referencia.valor - 1) * 100
    supuestos = referencia.supuestos + [f"Salario real = básico ÷ IPC del mismo mes (INDEC, base dic-2016)."]
    return Resultado(valor, actual.fuentes + referencia.fuentes, supuestos)


# --- Ley 27.795, art. 5 ------------------------------------------------------

MES_PREVIO_ART5 = "2023-11"  # el art. 5 cuenta el IPC desde el 1-dic-2023: el salario de partida es el de nov-2023
FECHAS_CORTE_ART5 = {
    "2025-08-21": "sanción (21-ago-2025)",
    "2025-10-02": "confirmación del Congreso (2-oct-2025)",
    "2025-10-21": "publicación en el Boletín Oficial (21-oct-2025)",
}


def salario_art5(puntos: dict[str, Punto], ipc: dict[str, Dato], mes: str) -> Resultado:
    """Salario que correspondería en `mes`: el de nov-2023 actualizado por el IPC acumulado desde dic-2023."""
    partida = puntos[MES_PREVIO_ART5]
    factor = ipc[mes].valor / ipc[MES_PREVIO_ART5].valor
    return Resultado(partida.valor * factor, partida.fuentes + (ipc[mes], ipc[MES_PREVIO_ART5]), [
        "Ley 27.795, art. 5: aumento no inferior al IPC desde el 1-dic-2023 y, después, actualización mensual "
        "no inferior a la inflación.",
        "Salario de partida: el básico de nov-2023 (último vigente antes del 1-dic-2023).",
    ])


def brecha_art5(puntos: dict[str, Punto], ipc: dict[str, Dato], mes: str) -> Resultado:
    """Cuánto habría que aumentar el básico del mes para alcanzar lo que exige el art. 5, en %."""
    exigido = salario_art5(puntos, ipc, mes)
    pagado = puntos[mes]
    valor = (exigido.valor / pagado.valor - 1) * 100
    return Resultado(valor, pagado.fuentes + exigido.fuentes, exigido.supuestos)


def mes_de(fecha: str) -> str:
    return fecha[:7]
