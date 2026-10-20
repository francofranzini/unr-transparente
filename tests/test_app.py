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
    ley = _seccion(html, "ley")
    assert ley.count('class="sello"') == len(SELLOS_LEY)
    assert "<b>Vetada</b><small>Decreto 647/2025</small>" in ley


def _seccion(html: str, ancla: str) -> str:
    inicio = html.index(f'id="{ancla}"')
    return html[inicio:html.index("</section>", inicio)]


def test_control_usa_la_misma_cronologia_que_la_ley(cliente):
    # ADR 0025: misma plantilla (scroll, filtros, recorrido), en orden cronológico y con un actor por hecho.
    # Los sellos son solo de la sección de la ley.
    control = _seccion(cliente.get("/").text, "control")
    for marca in ("data-cronologia", "data-cronologia-scroll", 'class="recorrido-modos" hidden', 'data-filtro="congreso"'):
        assert marca in control
    ids = re.findall(r'class="hito-ficha" href="/ficha/evento/([^"]+)"', control)
    hitos = [e for e in repo.eventos_de("control") if e.tipo != "estado"]
    assert ids == [e.id for e in hitos]
    assert 'class="hito actor-otro' not in control
    assert 'class="sello"' not in control


def test_control_tiene_una_cronologia_por_universidad(cliente):
    # ADR 0025: cada universidad, en su recuadro desplegable (hoy, solo la UNR, abierto); la cronología va adentro.
    from core.ejes import UNIVERSIDADES_CONTROL
    control = _seccion(cliente.get("/").text, "control")
    assert control.count('<details class="universidad" open>') == len(UNIVERSIDADES_CONTROL)
    inicio = control.index('<details class="universidad" open>')
    assert '<span class="universidad-nombre">Universidad Nacional de Rosario (UNR)</span>' in control[inicio:]
    assert inicio < control.index("data-cronologia-scroll")


def test_control_explica_quien_controla_debajo_de_la_pregunta(cliente):
    # ADR 0025: debajo de la pregunta, plegado («Ver más» / «Ver menos»), el texto sobre la autarquía de las universidades
    # y quién las audita (AGN y SIGEN); el último control externo ya está en la línea de tiempo, no en un recuadro aparte.
    control = _seccion(cliente.get("/").text, "control")
    pregunta = control.index("¿Quién audita a la UNR?</h2>")
    assert pregunta < control.index('presentacion') < control.index("Sindicatura General de la Nación") < control.index("data-cronologia")
    assert "¿Quién controla a la UNR?" not in control
    assert '<span class="si-cerrado">Ver más</span><span class="si-abierto">Ver menos</span>' in control
    assert "artículo 75, inciso 19, de la Constitución Nacional" in control and "Auditoría General de la Nación" in control
    visible = re.sub(r"<details.*?</details>", "", control, flags=re.S)
    assert "Sindicatura General de la Nación" not in visible
    assert 'class="hoy' not in control and "Último control externo" not in control


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


def test_salario_muestra_el_billete(cliente):
    texto = cliente.get("/").text
    assert "data-billete" in texto and 'href="/ficha/cifra/salario/compra-2026-08"' in texto


@pytest.mark.parametrize("ficha, norma", [
    ("ejecucion/arts34-exigido", "Ley 27.795, art. 4"),
    ("ejecucion/arts34-relacion-2026", "la ley no lo pide"),
    ("salario/exigido", "Ley 27.795, art. 5"),
    ("salario/poder-2026-08", "Ley 27.795, art. 5"),
])
def test_las_cifras_de_la_ley_citan_la_norma(cliente, ficha, norma):
    texto = cliente.get(f"/ficha/cifra/{ficha}", headers={"HX-Request": "true"}).text
    assert "<dt>Norma</dt>" in texto and norma in texto
    assert "https://www.boletinoficial.gob.ar/detalleAviso/primera/333139/20251021" in texto


def test_antes_de_que_rija_la_ley_no_hay_norma(cliente):
    # Mayo de 2025: pérdida de poder de compra, pero el art. 5 todavía no regía.
    assert "<dt>Norma</dt>" not in cliente.get("/ficha/cifra/salario/poder-2025-05", headers={"HX-Request": "true"}).text
