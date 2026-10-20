from datetime import date
from decimal import Decimal

import pytest

from core import lentes
from core.carga import cargar
from core.lentes import Vigencia
from core.modelos import Dato


def _dato(periodo: str, valor: str, indicador: str = "salario_basico") -> Dato:
    return Dato(id=f"x-{indicador.replace('_', '-')}-{periodo}", valor=Decimal(valor), unidad="ARS corrientes",
                entidad="CARGO_TESTIGO", indicador=indicador, periodo=periodo, tipo_fuente="primaria",
                documento="Doc", url="https://ejemplo.org", consultado=date(2026, 10, 19))


def test_vigencia_extiende_sin_interpolar():
    serie = lentes.serie_vigente([_dato("2023-01", "100"), _dato("2023-03", "130")], "2023-04")
    assert [(p.periodo, p.valor, p.vigencia) for p in serie] == [
        ("2023-01", Decimal("100"), Vigencia.PROPIA),
        ("2023-02", Decimal("100"), Vigencia.NO_CONFIRMADA),
        ("2023-03", Decimal("130"), Vigencia.PROPIA),
        ("2023-04", Decimal("130"), Vigencia.NO_CONFIRMADA),
    ]


def test_vigencia_confirmada_por_documento():
    serie = lentes.serie_vigente([_dato("2023-01", "100"), _dato("2023-03", "130")], "2023-03", {"2023-02"})
    assert serie[1].vigencia == Vigencia.CONFIRMADA


def test_variacion_real_a_mano():
    # Salario 100 con IPC 100 en nov-2023; salario 150 con IPC 200 después: 150/200 = 0,75 → −25 %.
    grillas = [_dato("2023-11", "100"), _dato("2024-01", "150")]
    ipc = lentes.serie_por_periodo([_dato("2023-11", "100", "ipc"), _dato("2024-01", "200", "ipc")])
    puntos = {p.periodo: p for p in lentes.serie_vigente(grillas, "2024-01")}
    ipc["2023-12"] = _dato("2023-12", "150", "ipc")
    assert lentes.variacion_real(puntos, ipc, "2024-01", "nov_2023").valor == Decimal("-25")


def test_brecha_art5_a_mano():
    # Exigido = 100 × 200/100 = 200; pagado 150 → hay que subir 200/150 − 1 = 33,33… %.
    grillas = [_dato("2023-11", "100"), _dato("2024-01", "150")]
    ipc = lentes.serie_por_periodo([_dato("2023-11", "100", "ipc"), _dato("2024-01", "200", "ipc")])
    puntos = {p.periodo: p for p in lentes.serie_vigente(grillas, "2024-01")}
    assert lentes.salario_art5(puntos, ipc, "2024-01").valor == Decimal("200")
    assert lentes.brecha_art5(puntos, ipc, "2024-01").valor.quantize(Decimal("0.01")) == Decimal("33.33")


@pytest.fixture(scope="module")
def reales():
    repo = cargar()
    ipc = lentes.serie_por_periodo(repo.buscar(indicador="ipc_nivel_general"))
    grillas = repo.buscar(entidad="CARGO_TESTIGO", indicador="salario_basico")
    return {p.periodo: p for p in lentes.serie_vigente(grillas, "2026-08", {"2024-01"})}, ipc


def test_brecha_art5_agosto_2026_reproduce_reclamo_gremial(reales):
    # 465.140,81 × 12.276,766 / 2.816,0628 = 2.027.804,52; 2.027.804,52 / 1.520.087,32 − 1 = 33,40 %.
    puntos, ipc = reales
    assert lentes.salario_art5(puntos, ipc, "2026-08").valor.quantize(Decimal("0.01")) == Decimal("2027804.52")
    assert lentes.brecha_art5(puntos, ipc, "2026-08").valor.quantize(Decimal("0.01")) == Decimal("33.40")


def test_diciembre_2023_inflacion_mensual(reales):
    # ADR 0011: 3.533,1922 / 2.816,0628 − 1 = 25,47 %.
    _, ipc = reales
    variacion = (ipc["2023-12"].valor / ipc["2023-11"].valor - 1) * 100
    assert variacion.quantize(Decimal("0.01")) == Decimal("25.47")


def test_julio_y_agosto_2026_sin_grilla_propia(reales):
    puntos, _ = reales
    assert puntos["2026-07"].vigencia == Vigencia.NO_CONFIRMADA
    assert puntos["2026-08"].valor == puntos["2026-06"].valor
    assert puntos["2024-01"].vigencia == Vigencia.CONFIRMADA


# --- Ley 27.795, arts. 3 y 4 ---------------------------------------------------

def _devengado(periodo: str, valor: str, actividad: str = "14") -> Dato:
    return Dato(id=f"x-dev-act{actividad}-{periodo}", valor=Decimal(valor), unidad="ARS corrientes", entidad="UNR",
                indicador="devengado", periodo=periodo, tipo_fuente="primaria", documento="Doc",
                url="https://ejemplo.org", consultado=date(2026, 10, 19), dimensiones={"actividad_id": actividad})


def _ipc_arts_3_4() -> dict[str, Dato]:
    valores = {"2024-04": "100", "2024-12": "150", "2025-02": "165", "2025-04": "180", "2025-06": "195",
               "2025-08": "210", "2025-10": "225"}
    return {p: _dato(p, v, "ipc") for p, v in valores.items()}


def test_partida_nivel_septiembre_suma_actividades_y_excluye_salarios():
    devengado = [_devengado("2024-09", "90", "14"), _devengado("2024-09", "6", "15"), _devengado("2024-09", "4", "16"),
                 _devengado("2024-09", "5000", "12"), _devengado("2024-08", "999", "14")]
    assert lentes.partida_arts_3_4(devengado, "nivel_sep_2024").valor == Decimal("100")


def test_partida_promedio_2024_exige_los_doce_meses():
    # 6 meses de 50 y 6 de 150: 1.200 / 12 = 100.
    devengado = [_devengado(m, "50" if i < 6 else "150") for i, m in enumerate(lentes._meses("2024-01", "2024-12"))]
    assert lentes.partida_arts_3_4(devengado, "promedio_2024").valor == Decimal("100")
    with pytest.raises(ValueError):
        lentes.partida_arts_3_4(devengado[:11], "promedio_2024")


def test_factor_art3_a_mano():
    # IPC 150 en dic-2024 sobre 100 en abr-2024: +50 %.
    assert lentes.factor_art3(_ipc_arts_3_4()).valor == Decimal("1.5")


def test_exigido_arts_3_4_a_mano():
    # Partida 100 por mes. Factores por bimestre: 1,5 · 1,5×165/150 = 1,65 · 1,8 · 1,95 · 2,1 · 2,25.
    # Suma de factores = 11,25; por 2 meses y por 100: 2.250.
    partida = lentes.partida_arts_3_4([_devengado("2024-09", "100")], "nivel_sep_2024")
    bimestres = lentes.bimestres_art4(partida, _ipc_arts_3_4())
    assert [r.valor for r in bimestres] == [Decimal(v) for v in ("300", "330", "360", "390", "420", "450")]
    exigido = lentes.exigido_arts_3_4(partida, _ipc_arts_3_4())
    assert exigido.valor == Decimal("2250")
    assert len({d.id for d in exigido.fuentes}) == len(exigido.fuentes)
    assert any("Art. 4" in s for s in exigido.supuestos)


def test_transferido_arts_3_4_solo_el_anio_y_las_actividades():
    devengado = [_devengado("2025-01", "700", "14"), _devengado("2025-12", "800", "25"),
                 _devengado("2025-03", "9000", "13"), _devengado("2024-12", "999", "14")]
    assert lentes.transferido_arts_3_4(devengado, "2025").valor == Decimal("1500")


def test_meses_art4_reparten_cada_bimestre_en_dos():
    # Mismos factores que el caso anterior: 150, 150, 165, 165, ..., 225, 225; suman 2.250.
    partida = lentes.partida_arts_3_4([_devengado("2024-09", "100")], "nivel_sep_2024")
    meses = lentes.meses_art4(partida, _ipc_arts_3_4())
    assert [r.valor for r in meses[:4]] == [Decimal("150"), Decimal("150"), Decimal("165"), Decimal("165")]
    assert len(meses) == 12 and sum(r.valor for r in meses) == Decimal("2250")
