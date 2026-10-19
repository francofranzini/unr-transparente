from decimal import Decimal

import pytest

from core.carga import cargar
from core.ejes import construir_ejes


@pytest.fixture(scope="module")
def ejes():
    return construir_ejes(cargar())


def test_unr_ejecucion_calculada_a_mano(ejes):
    eje = ejes["ejecucion"]
    assert eje.cifra("unr-credito_asignado").valor == Decimal("237298391675")
    assert eje.cifra("unr-devengado").valor == Decimal("208839493671")
    # 208.839.493.671 / 237.298.391.675 = 0,880071...
    assert eje.cifra("unr-ejecucion").valor.quantize(Decimal("0.0001")) == Decimal("88.0071")


def test_asignado_pa_coincide_con_anexo_de_la_ley():
    repo = cargar()
    assert repo.datos["unr-credito-2026-total"].valor == repo.datos[
        "pa2026-p26-universidad-nacional-de-rosario-credito-asignado"].valor


def test_credito_no_asignado_queda_fuera_de_los_cocientes(ejes):
    eje = ejes["ejecucion"]
    fuentes = eje.cifra("sistema-ejecucion").fuentes
    assert all(d.entidad != "CREDITO_NO_ASIGNADO" for d in fuentes)
    assert len(fuentes) == 61 * 2
    assert eje.cifra("no-asignado-devengado").valor == 0


def test_anio_transcurrido_al_16_de_octubre(ejes):
    # 16-oct-2026 es el día 289 de 365.
    valor = ejes["ejecucion"].cifra("anio-transcurrido").valor
    assert valor == Decimal(289) / Decimal(365) * 100


def test_toda_cifra_tiene_fuentes(ejes):
    for eje in ejes.values():
        for c in eje.cifras:
            assert c.fuentes, f"{eje.clave}/{c.clave} sin fuentes"


def test_graduacion_no_calcula_tasas(ejes):
    assert all(c.unidad == "personas" for c in ejes["graduacion"].cifras)
