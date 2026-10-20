import re

import pytest
from fastapi.testclient import TestClient

from app.main import PAGINAS, app, repo

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


def test_cronologia_de_la_ley_va_de_lo_mas_antiguo_a_lo_mas_reciente(cliente):
    # ADR 0030: orden cronológico, dentro de un recuadro con scroll propio.
    html = cliente.get("/").text
    cronologia = html[html.index("data-cronologia-scroll"):html.index("</ol>", html.index("data-cronologia-scroll"))]
    ids = re.findall(r'class="hito-ficha" href="/ficha/evento/([^"]+)"', cronologia)
    assert len(ids) > 1
    por_id = {e.id: e.fecha for e in repo.eventos}
    assert [por_id[i] for i in ids] == sorted(por_id[i] for i in ids)


def test_recorrido_de_la_ley_con_sellos(cliente):
    # ADR 0031: los controles del recorrido nacen ocultos (sin JavaScript se ve la lista) y cada sello es de un evento real.
    html = cliente.get("/").text
    assert 'class="recorrido-modos" hidden' in html and 'class="recorrido-nav" hidden' in html
    from core.ejes import SELLOS_LEY
    ids = {e.id for e in repo.eventos}
    assert set(SELLOS_LEY) <= ids
    assert html.count('class="sello"') == len(SELLOS_LEY)
    assert "<b>Vetada</b><small>Decreto 647/2025</small>" in html


def test_donde_esta_hoy_muestra_la_fecha_de_revision(cliente):
    # ADR 0032: el atraso se muestra; la fecha sale del evento de estado, no se escribe a mano.
    estado = max((e for e in repo.eventos_de("ley") if e.tipo == "estado"), key=lambda e: e.fecha)
    assert re.search(rf"Dónde está hoy · revisado el {int(estado.fecha[8:])} de \w+ de {estado.fecha[:4]}",
                     cliente.get("/").text)


@pytest.mark.parametrize("ruta", RUTAS)
def test_textos_sin_adjetivos_valorativos(cliente, ruta):
    # Los títulos de prensa se citan tal como se publicaron; el control aplica al texto propio del portal.
    html = re.sub(r'<ul class="hito-medios">.*?</ul>', " ", cliente.get(ruta).text, flags=re.S)
    texto = re.sub(r"<[^>]+>", " ", html).lower()
    assert [p for p in VALORATIVOS if p in texto] == []


def test_transferencias_muestra_el_caso_unr_con_grafico(cliente):
    texto = cliente.get("/").text
    assert "data-bloque-arts34" in texto
    assert 'data-panel="unr-arts34-"' in texto and 'data-panel="arts34-"' in texto
    assert "−42,3 %" in texto and "−32,4 %" in texto
