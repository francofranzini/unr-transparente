import re

import pytest
from fastapi.testclient import TestClient

from app.main import PAGINAS, app

# Control mínimo del principio 2. No reemplaza la revisión humana de los textos.
VALORATIVOS = ["brutal", "histórico", "historico", "motosierra", "ajuste", "recorte", "derroche", "desfinanci",
               "escandal", "récord", "drástic", "drastic", "catastróf", "excelente", "pésim"]
RUTAS = ["/"] + [f"/{p}" for p in PAGINAS]


@pytest.fixture(scope="module")
def cliente():
    return TestClient(app)


@pytest.mark.parametrize("ruta", RUTAS)
def test_paginas_responden(cliente, ruta):
    assert cliente.get(ruta).status_code == 200


def test_portada_enlaza_a_cada_eje(cliente):
    texto = cliente.get("/").text
    for pagina in PAGINAS:
        assert f'href="/{pagina}"' in texto


def test_portada_destaca_la_brecha_del_art5(cliente):
    assert "33,4 %" in cliente.get("/").text


def test_pagina_inexistente_da_404(cliente):
    assert cliente.get("/no-existe").status_code == 404


@pytest.mark.parametrize("ruta", RUTAS)
def test_cada_numero_abre_su_ficha(cliente, ruta):
    for enlace in set(re.findall(r'hx-get="(/ficha/[^"]+)"', cliente.get(ruta).text)):
        r = cliente.get(enlace, headers={"HX-Request": "true"})
        assert r.status_code == 200, enlace
        assert "Documento" in r.text and "http" in r.text


def test_ficha_sin_htmx_es_pagina_completa(cliente):
    r = cliente.get("/ficha/cifra/ejecucion/unr-ejecucion")
    assert "<!doctype html>" in r.text and "Volver" in r.text


@pytest.mark.parametrize("ruta", RUTAS)
def test_textos_sin_adjetivos_valorativos(cliente, ruta):
    # Los títulos de prensa se citan tal como se publicaron; el control aplica al texto propio del portal.
    html = re.sub(r'<ul class="hito-medios">.*?</ul>', " ", cliente.get(ruta).text, flags=re.S)
    texto = re.sub(r"<[^>]+>", " ", html).lower()
    assert [p for p in VALORATIVOS if p in texto] == []
