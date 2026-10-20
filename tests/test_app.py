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


def test_los_recorridos_de_ley_y_control_tienen_transicion(cliente):
    # ADR 0025: en las dos cronologías el paso entre hechos se desliza; en la ley, el sello cae después.
    html = cliente.get("/").text
    for ancla in ("ley", "control"):
        assert "data-cronologia data-transicion" in _seccion(html, ancla)


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


def test_donde_esta_hoy_muestra_la_fecha_del_resumen(cliente):
    # ADR 0032 y 0033: el atraso se muestra. La fecha del resumen sale del evento de estado; la de consulta, del vigía.
    estado = max((e for e in repo.eventos_de("ley") if e.tipo == "estado"), key=lambda e: e.fecha)
    # Una sola fecha si coincide con la consulta de fuentes; si no, «resumen del … · fuentes consultadas el …».
    assert re.search(rf"Dónde está hoy · (resumen del )?{int(estado.fecha[8:])} de \w+ de {estado.fecha[:4]}",
                     cliente.get("/").text)


def test_la_ficha_muestra_el_tipo_con_una_etiqueta_legible(cliente):
    # ADR 0034: «estado», «judicial», etc. son valores internos; el lector ve una etiqueta.
    from core.ejes import TIPOS_EVENTO
    for evento in repo.eventos_de("ley"):
        ficha = cliente.get(f"/ficha/evento/{evento.id}", headers={"HX-Request": "true"}).text
        assert f"<dt>Tipo</dt><dd>{TIPOS_EVENTO[evento.tipo][0]}</dd>" in ficha


def test_la_linea_de_tiempo_marca_el_ultimo_hecho_importante(cliente):
    # ADR 0034: un solo hecho marcado, el mismo que destaca «Dónde está hoy», con un ancla para llegar desde el recuadro.
    from core.ejes import eje_ley
    eje = eje_ley(repo)
    ley = _seccion(cliente.get("/").text, "ley")
    assert ley.count(" hito-importante") == 1 and ley.count("Último hecho importante") == 1
    importante = eje.detalle["importante"]
    assert f'id="hito-{importante.id}"' in ley
    marcado = ley[:ley.index(f'id="hito-{importante.id}"')]
    assert marcado.rindex(" hito-importante") > marcado.rindex("<li")
    if eje.detalle["destacado"]:
        assert importante.id == eje.detalle["destacado"].id and f'href="#hito-{importante.id}"' in ley


def test_en_una_misma_fecha_el_hecho_de_mas_peso_queda_ultimo():
    from core.ejes import ordenar_cronologia
    estado = next(e for e in repo.eventos if e.tipo == "estado" and "ley" in e.ejes)
    fallo = estado.model_copy(update={"id": "x-fallo", "tipo": "judicial"})
    acuerdo = estado.model_copy(update={"id": "x-acuerdo", "tipo": "convenio"})
    assert [e.id for e in ordenar_cronologia([fallo, estado, acuerdo])] == [estado.id, "x-acuerdo", "x-fallo"]


def test_donde_esta_hoy_destaca_el_mismo_hecho_que_cierra_la_cronologia(cliente):
    # ADR 0034: el hecho de más peso desde el resumen va primero en el recuadro, y es el último de la línea de tiempo.
    from core.ejes import eje_ley
    eje = eje_ley(repo)
    destacado = eje.detalle["destacado"]
    ley = _seccion(cliente.get("/").text, "ley")
    hitos = [e for e in eje.eventos if e.tipo != "estado"]
    if destacado:
        assert destacado.id == hitos[-1].id
        recuadro = ley[ley.index('class="hoy'):ley.index("</div>", ley.index('class="hoy'))]
        assert recuadro.index(destacado.titulo) < recuadro.index('class="hoy-resumen"')


def test_un_hecho_posterior_al_resumen_genera_el_aviso():
    from core.carga import Repositorio
    from core.ejes import eje_ley
    eventos = list(repo.eventos)
    estado = next(e for e in eventos if e.tipo == "estado" and "ley" in e.ejes)
    nuevo = estado.model_copy(update={"id": "ley-27795-prueba", "tipo": "judicial", "fecha": "2099-01-01",
                                      "titulo": "Hecho de prueba"})
    eje = eje_ley(Repositorio(datos=repo.datos, eventos=eventos + [nuevo]))
    assert [e.id for e in eje.detalle["posteriores"]] == ["ley-27795-prueba"]
    assert eje.detalle["destacado"].id == "ley-27795-prueba"  # el hecho nuevo pasa al frente


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


@pytest.mark.parametrize("panel, cifra", [
    ("arts34-2025", "ejecucion/arts34-exigido"), ("unr-arts34-2025", "ejecucion/unr-arts34-exigido"),
    ("arts34-2026", "ejecucion/arts34-piso-2026"), ("unr-arts34-2026", "ejecucion/unr-arts34-piso-2026"),
])
def test_de_donde_sale_sigue_la_seleccion(cliente, panel, cifra):
    # «¿De dónde sale este número?» explica el número de las universidades y el año elegidos.
    texto = cliente.get("/").text
    articulo = re.search(rf'<section class="articulo" data-panel="{panel}".*?</section>', texto, flags=re.S)
    assert articulo and f'/ficha/cifra/{cifra}"' in articulo[0]


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


@pytest.mark.parametrize("ficha, sitio", [
    ("ejecucion/arts34-transferido", "https://www.presupuestoabierto.gob.ar/sici/datos-abiertos"),
    ("ejecucion/arts34-ipc-art3", "https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31"),
])
def test_la_ficha_lleva_al_sitio_oficial_y_no_a_una_descarga(cliente, ficha, sitio):
    # El documento abre la página oficial; el archivo de datos queda como «descargar los datos».
    texto = cliente.get(f"/ficha/cifra/{ficha}", headers={"HX-Request": "true"}).text
    documento = re.search(r'<a href="([^"]+)" rel="noopener" target="_blank">', texto.split("<dt>Documento</dt>")[1])
    assert documento[1] == sitio and "descargar los datos" in texto



def test_la_ficha_es_breve_y_deja_el_detalle_plegado(cliente):
    # ADR 0032: a la vista, el número, cómo se calcula y de dónde sale; citas, documentos e ids, en «Ver el detalle».
    texto = cliente.get("/ficha/cifra/ejecucion/unr-arts34-brecha", headers={"HX-Request": "true"}).text
    breve, detalle = texto.split('<details class="ficha-detalle">')
    assert "Cómo se calcula" in breve and "Sale de" in breve and "Norma: <a" in breve
    assert "<dt>Norma</dt>" in detalle and "<code>" in detalle and "<code>" not in breve


def test_la_ficha_de_la_partida_muestra_de_que_se_compone(cliente):
    # La partida de los arts. 3 y 4 es la suma de cuatro actividades: la ficha muestra cada una, no solo los ids.
    texto = cliente.get("/ficha/cifra/ejecucion/unr-arts34-partida", headers={"HX-Request": "true"}).text
    breve, detalle = texto.split('<details class="ficha-detalle">')
    assert "<span>Asistencia Financiera para el Funcionamiento Universitarios</span><span>$ 1.483 millones</span>" in breve
    assert "$ 1.482.584.082,00" in detalle and "$ 1.529.018.216,00" in detalle
    assert '<span class="ficha-periodo">sep 2024</span>' in breve


def test_la_ficha_de_la_partida_explica_que_el_mes_es_una_eleccion(cliente):
    # La ley no fija el mes de la partida (ADR 0020): la ficha lo dice y muestra los 12 meses de donde se eligió.
    texto = cliente.get("/ficha/cifra/ejecucion/unr-arts34-partida", headers={"HX-Request": "true"}).text
    assert "no dice de qué mes" in texto.split('<details class="ficha-detalle">')[0]
    cada_mes = texto.split("<dt>Cada mes</dt>")[1]
    assert '<tr class="total"><th>sep 2024</th><td>$ 1.529.018.216</td></tr>' in cada_mes
    assert "<th>dic 2024</th><td>$ 2.408.852.952</td>" in cada_mes
