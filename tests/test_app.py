import re

import pytest
from fastapi.testclient import TestClient

from app.main import PAGINAS, app

# Control mínimo del principio 2. No reemplaza la revisión humana de los textos.
VALORATIVOS = ["brutal", "histórico", "historico", "motosierra", "ajuste", "recorte", "derroche", "desfinanci",
               "escandal", "récord", "drástic", "drastic", "catastróf", "excelente", "pésim"]
RUTAS = ["/"]


@pytest.fixture(scope="module")
def cliente():
    return TestClient(app)


@pytest.mark.parametrize("ruta", RUTAS)
def test_paginas_responden(cliente, ruta):
    assert cliente.get(ruta).status_code == 200


def test_portada_tiene_cada_seccion(cliente):
    texto = cliente.get("/").text
    for pagina in PAGINAS:
        assert f'id="{pagina}"' in texto


@pytest.mark.parametrize("pagina", list(PAGINAS))
def test_direcciones_de_ejes_llevan_a_su_seccion(cliente, pagina):
    r = cliente.get(f"/{pagina}", follow_redirects=False)
    assert r.status_code == 301 and r.headers["location"] == f"/#{pagina}"


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


def test_transferencias_muestra_el_caso_unr_con_grafico(cliente):
    texto = cliente.get("/").text
    assert "data-bloque-arts34" in texto
    assert 'data-panel="unr-arts34-2025"' in texto and 'data-panel="arts34-2025"' in texto
    # El año en curso, con su referencia (la ley no fija nada para 2026: ADR 0024).
    assert 'data-panel="arts34-2026"' in texto and "−34,7 %" in texto and "−52,0 %" in texto
    assert "−42,3 %" in texto and "−32,4 %" in texto


def test_salario_muestra_el_calendario(cliente):
    texto = cliente.get("/").text
    assert "data-calendario" in texto and 'href="/ficha/cifra/salario/dias-2026-08"' in texto


@pytest.mark.parametrize("ficha, norma", [
    ("ejecucion/arts34-exigido", "Ley 27.795, art. 4"),
    ("ejecucion/arts34-relacion-2026", "la ley no lo pide"),
    ("salario/exigido", "Ley 27.795, art. 5"),
    ("salario/faltan-2026-08", "Ley 27.795, art. 5"),
])
def test_las_cifras_de_la_ley_citan_la_norma(cliente, ficha, norma):
    texto = cliente.get(f"/ficha/cifra/{ficha}", headers={"HX-Request": "true"}).text
    assert "<dt>Norma</dt>" in texto and norma in texto
    assert "https://www.boletinoficial.gob.ar/detalleAviso/primera/333139/20251021" in texto


def test_antes_de_que_rija_la_ley_no_hay_norma(cliente):
    # Mayo de 2025: pérdida de poder de compra, pero el art. 5 todavía no regía.
    assert "<dt>Norma</dt>" not in cliente.get("/ficha/cifra/salario/faltan-2025-05", headers={"HX-Request": "true"}).text
