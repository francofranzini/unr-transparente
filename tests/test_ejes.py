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


def test_arts_3_4_del_sistema(ejes):
    eje = ejes["ejecucion"]
    # Devengado 2025 de las actividades 14, 15 y 16, sumado para todas las universidades: 410.017 millones.
    assert eje.cifra("arts34-transferido").valor.quantize(Decimal("1E6")) == Decimal("410017E6")
    # Septiembre de 2024, mismo monto que agosto: 33.991 millones por mes.
    assert eje.cifra("arts34-partida").valor.quantize(Decimal("1E6")) == Decimal("33991E6")
    # IPC dic-2024 / abr-2024 = 7.694,0075 / 5.830,2271 = 1,319675...
    assert eje.cifra("arts34-ipc-art3").valor.quantize(Decimal("0.01")) == Decimal("31.97")
    assert eje.cifra("arts34-brecha").valor.quantize(Decimal("0.1")) == Decimal("47.8")
    assert eje.cifra("arts34-brecha-b").valor.quantize(Decimal("0.1")) == Decimal("27.1")
    total_bimestres = sum(eje.cifra(f"arts34-exigido-bim{i}").valor for i in range(1, 7))
    assert total_bimestres == eje.cifra("arts34-exigido").valor
    # «Universidades sin Discriminar» no tuvo devengado en estas actividades: no hay nada que sumar aparte.
    assert eje.cifra("arts34-sin-asignar").valor == 0


def test_arts_3_4_de_la_unr_como_detalle(ejes):
    eje = ejes["ejecucion"]
    # Devengado 2025, actividades 14 + 15 + 16 (sin 25): 15.134,8 + 302,5 + 295,2 millones.
    assert eje.cifra("unr-arts34-transferido").valor == Decimal("15732525648")
    # Septiembre de 2024 (igual de julio a noviembre): 1.482,58 + 24,62 + 21,81 millones.
    assert eje.cifra("unr-arts34-partida").valor == Decimal("1529018216")
    # Partida × 2 × 1,319675 × (1 + IPC feb/dic + abr/dic + jun/dic + ago/dic + oct/dic) = 27.267 millones.
    assert eje.cifra("unr-arts34-exigido").valor.quantize(Decimal("1E6")) == Decimal("27267E6")
    assert eje.cifra("unr-arts34-brecha").valor.quantize(Decimal("0.1")) == Decimal("73.3")


def test_acumulado_mensual_cierra_en_el_total_anual(ejes):
    eje = ejes["ejecucion"]
    for prefijo in ("arts34-", "unr-arts34-"):
        centavo = Decimal("0.01")  # el reparto por mes divide por 2: se compara al centavo
        assert (eje.cifra(f"{prefijo}acum-exigido-12").valor.quantize(centavo)
                == eje.cifra(f"{prefijo}exigido").valor.quantize(centavo))
        assert eje.cifra(f"{prefijo}acum-transferido-12").valor == eje.cifra(f"{prefijo}transferido").valor
        assert len(eje.detalle["acumulado"][prefijo]) == 12


def test_calendario_del_sueldo(ejes):
    eje = ejes["salario"]
    # Nov-2023 es la base: alcanza para los 30 días.
    assert eje.cifra("dias-2023-11").valor == 30
    # Ago-2026: salario real −25,0 % → 30 × 0,7498 = 22,49 → 22 días completos, 8 sin cubrir.
    assert eje.cifra("dias-2026-08").valor == 22 and eje.cifra("faltan-2026-08").valor == 8
    assert "22,49" in eje.cifra("dias-2026-08").calculo
    cal = eje.detalle["calendario"]
    assert cal[0]["periodo"] == "2023-11" and cal[-1]["periodo"] == eje.cifra("pagado").periodo
    # Los meses sin escala publicada llevan el aviso de vigencia.
    assert eje.cifra("dias-2026-08").aviso


def test_el_art5_exige_solo_desde_noviembre_de_2025(ejes):
    # «Este aumento se hará efectivo al mes siguiente de la publicación» (BO 21-oct-2025).
    eje = ejes["salario"]
    serie = {p["periodo"]: p for p in eje.serie}
    assert serie["2025-10"]["exigido"] is None and serie["2025-10"]["referencia"] is not None
    assert serie["2025-11"]["exigido"] == serie["2025-11"]["referencia"]
    rige = {c["periodo"]: c["rige"] for c in eje.detalle["calendario"]}
    assert not rige["2025-10"] and rige["2025-11"] and rige["2026-08"]


def test_anio_en_curso_con_referencia_y_sin_exigido(ejes):
    eje = ejes["ejecucion"]
    # Enero a septiembre de 2026 (octubre está en curso): la referencia no es un monto de la ley.
    assert eje.detalle["ventana_actual"] == "enero a septiembre de 2026"
    assert "La ley no lo pide" in eje.cifra("arts34-ref-2026").calculo
    assert eje.cifra("arts34-relacion-2026").valor.quantize(Decimal("0.1")) == Decimal("-34.7")
    assert eje.cifra("unr-arts34-relacion-2026").valor.quantize(Decimal("0.1")) == Decimal("-52.0")
    assert not [c for c in eje.cifras if c.clave.startswith("arts34-exigido-2026")]
