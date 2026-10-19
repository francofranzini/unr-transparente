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
