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


# --- Ley 27.795, arts. 3 y 4 (ADR 0020) ---------------------------------------

ACTIVIDADES_ARTS_3_4 = ("14", "15", "16", "25")  # funcionamiento, hospitales, ciencia y técnica, extensión
MES_PREVIO_ART3 = "2024-04"  # el art. 3 cuenta el IPC del 1-may-2024 al 31-dic-2024
MES_FINAL_ART3 = "2024-12"
MES_PARTIDA_ARTS_3_4 = "2024-09"  # primer mes en que el devengado del sistema queda estable (igual que agosto)
PARTIDAS_ARTS_3_4 = {
    "nivel_sep_2024": "monto mensual de septiembre de 2024",
    "promedio_2024": "promedio mensual de 2024",
}


def _de_actividades(devengado: list[Dato]) -> list[Dato]:
    return [d for d in devengado if d.dimensiones.get("actividad_id") in ACTIVIDADES_ARTS_3_4]


def partida_arts_3_4(devengado_2024: list[Dato], opcion: str) -> Resultado:
    """Monto mensual de partida: lo devengado en las actividades 14, 15, 16 y 25 (a una universidad o al sistema)."""
    datos = _de_actividades(devengado_2024)
    if opcion == "nivel_sep_2024":
        fuentes = tuple(d for d in datos if d.periodo == MES_PARTIDA_ARTS_3_4)
        valor = sum(d.valor for d in fuentes)
    elif opcion == "promedio_2024":
        fuentes = tuple(d for d in datos if d.periodo.startswith("2024-"))
        if {d.periodo for d in fuentes} != set(_meses("2024-01", "2024-12")):
            raise ValueError("El promedio de 2024 necesita los 12 meses")
        valor = sum(d.valor for d in fuentes) / 12
    else:
        raise ValueError(f"Partida desconocida: {opcion}")
    if not fuentes:
        raise ValueError(f"Sin devengado para la partida {opcion}")
    return Resultado(valor, fuentes, [f"Monto de partida: {PARTIDAS_ARTS_3_4[opcion]}, actividades 14, 15, 16 y 25."])


def factor_art3(ipc: dict[str, Dato]) -> Resultado:
    """IPC acumulado de mayo a diciembre de 2024, como factor (1,32 = +32 %)."""
    fin, previo = ipc[MES_FINAL_ART3], ipc[MES_PREVIO_ART3]
    return Resultado(fin.valor / previo.valor, (fin, previo), [
        "Art. 3: actualización al 1-ene-2025 por el IPC acumulado entre el 1-may-2024 y el 31-dic-2024 "
        "(IPC de diciembre de 2024 ÷ IPC de abril de 2024).",
    ])


def bimestres_art4(partida: Resultado, ipc: dict[str, Dato]) -> list[Resultado]:
    """Lo que correspondía en cada bimestre de 2025: la partida actualizada por el art. 3 y, al empezar cada
    bimestre, por el IPC acumulado desde diciembre de 2024 hasta el último mes del bimestre anterior."""
    f3 = factor_art3(ipc)
    bimestres = []
    for b in range(6):
        referencia = MES_FINAL_ART3 if b == 0 else f"2025-{2 * b:02d}"
        factor = f3.valor * ipc[referencia].valor / ipc[MES_FINAL_ART3].valor
        bimestres.append(Resultado(2 * partida.valor * factor,
                                   partida.fuentes + f3.fuentes + (ipc[referencia],)))
    return bimestres


def meses_art4(partida: Resultado, ipc: dict[str, Dato]) -> list[Resultado]:
    """Lo que correspondía en cada mes de 2025: la mitad de su bimestre (el monto es el mismo en los dos meses)."""
    return [Resultado(b.valor / 2, b.fuentes) for b in bimestres_art4(partida, ipc) for _ in range(2)]


def exigido_arts_3_4(partida: Resultado, ipc: dict[str, Dato]) -> Resultado:
    """Total que correspondía transferir en 2025 según los arts. 3 y 4."""
    bimestres = bimestres_art4(partida, ipc)
    fuentes = tuple({d.id: d for r in bimestres for d in r.fuentes}.values())
    return Resultado(sum(r.valor for r in bimestres), fuentes, partida.supuestos + factor_art3(ipc).supuestos + [
        "Art. 4: actualización bimestral por IPC durante 2025. Cada bimestre usa el IPC del último mes del "
        "bimestre anterior (enero-febrero, el de diciembre de 2024).",
        "Los aumentos otorgados durante 2025 se toman a cuenta: se compara contra todo lo devengado en el año.",
    ])


def transferido_arts_3_4(devengado: list[Dato], anio: str) -> Resultado:
    fuentes = tuple(d for d in _de_actividades(devengado) if d.periodo.startswith(f"{anio}-"))
    return Resultado(sum(d.valor for d in fuentes), fuentes, [
        f"Devengado {anio} de las actividades 14, 15, 16 y 25 (Presupuesto Abierto, todas las fuentes)."])
