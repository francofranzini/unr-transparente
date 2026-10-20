"""Reglas de verificación de la cronología de la Ley 27.795 (ADR 0032).

Se aplican solo al eje ley: un hecho nuevo entra por el documento, y si no hay documento, por dos medios.
"""

from datetime import date, timedelta

import pytest

from core.carga import cargar

EVENTOS = cargar().eventos_de("ley")
HITOS = [e for e in EVENTOS if e.tipo != "estado"]
# Una nota puede salir el día anterior a la fecha formal del hecho (p. ej., una sesión que termina de madrugada).
MARGEN = timedelta(days=1)


@pytest.mark.parametrize("evento", [e for e in HITOS if e.tipo_fuente.value == "secundaria"], ids=lambda e: e.id)
def test_hecho_secundario_tiene_dos_medios_distintos(evento):
    medios = {n.medio for n in evento.noticias}
    assert len(medios) >= 2, f"{evento.id}: sin documento original hacen falta al menos dos medios; hay {sorted(medios)}"


@pytest.mark.parametrize("evento", HITOS, ids=lambda e: e.id)
def test_cada_noticia_tiene_fecha(evento):
    assert [n.medio for n in evento.noticias if not n.fecha] == []


@pytest.mark.parametrize("evento", HITOS, ids=lambda e: e.id)
def test_ninguna_noticia_es_anterior_al_hecho(evento):
    # Detecta notas cargadas en el hito equivocado.
    inicio = date.fromisoformat(evento.fecha) - MARGEN
    anteriores = [f"{n.medio} ({n.fecha})" for n in evento.noticias if n.fecha and date.fromisoformat(n.fecha) < inicio]
    assert anteriores == [], f"{evento.id} ({evento.fecha}): notas anteriores al hecho"


def test_un_solo_estado_y_el_atraso_se_muestra():
    # El resumen lo escribe una persona; los hechos pueden cargarse solos después (ADR 0033). Si el resumen quedó atrás,
    # la página tiene que decirlo (se verifica en test_app.py).
    estados = [e for e in EVENTOS if e.tipo == "estado"]
    assert len(estados) == 1, "«Dónde está hoy» sale de un único evento de estado: reemplazarlo, no sumar otro"
