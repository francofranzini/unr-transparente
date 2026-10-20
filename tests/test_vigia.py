"""Vigía de fuentes (ADR 0032), sin red: páginas y feeds de ejemplo escritos acá."""

import importlib.util
import re
from datetime import date
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("vigia_fuentes", RAIZ / "scripts" / "vigia_fuentes.py")
vigia = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vigia)

INFOLEG = """<table>
<tr><td><a href="/infolegInternet/verNorma.do;jsessionid=ABC123?id=417371">Decreto 647/2025</a></td></tr>
<tr><td><a href="/infolegInternet/verNorma.do;jsessionid=ABC123?id=999999">Decreto 1/2027</a></td></tr>
<tr><td><a href="/infolegInternet/estilos/x.css">estilos</a></td></tr>
</table>"""

SENADO = """<table>
<tr><td>Financiamiento de la educación universitaria y recomposición del salario docente.</td>
    <td><a href="/votaciones/detalleActa/2571" title="Detalle"><img src="ver.png"></a></td></tr>
<tr><td>Presupuesto de la Administración Nacional 2027</td>
    <td><a href="/votaciones/detalleActa/2700" title="Detalle"><img src="ver.png"></a></td></tr>
<tr><td>Insistencia en la ley 27.795 (nueva votación)</td>
    <td><a href="/votaciones/detalleActa/2701" title="Detalle"><img src="ver.png"></a></td></tr>
</table>"""

FEED = """<rss><channel>
<item><title>La Cámara resolvió la apelación de la sentencia - Infobae</title><link>https://ejemplo.org/a</link>
  <pubDate>Tue, 20 Oct 2026 10:00:00 GMT</pubDate></item>
<item><title><![CDATA[Marcha universitaria en Rosario]]></title><link>https://ejemplo.org/b</link>
  <pubDate>Tue, 20 Oct 2026 11:00:00 GMT</pubDate></item>
<item><title>La Cámara confirmó la cautelar - Infobae</title><link>https://ejemplo.org/c</link>
  <pubDate>Tue, 31 Mar 2026 10:00:00 GMT</pubDate></item>
<item><title>El Gobierno deberá pagar una multa por no cumplir la Ley de Financiamiento Universitario - Página|12</title>
  <link>https://news.google.com/rss/articles/XYZ</link><pubDate>Wed, 21 Oct 2026 10:00:00 GMT</pubDate></item>
</channel></rss>"""


def test_normalizar_url_quita_sesion_y_barra_final():
    assert (vigia.normalizar_url("http://Servicios.Infoleg.gob.ar/a/verNorma.do;jsessionid=XY?id=1")
            == "https://servicios.infoleg.gob.ar/a/verNorma.do?id=1")
    assert vigia.normalizar_url("https://ejemplo.org/nota/") == vigia.normalizar_url("https://ejemplo.org/nota")


def test_normalizar_titulo_quita_el_medio_del_final():
    assert vigia.normalizar_titulo("Vetó la ley - Página|12") == vigia.normalizar_titulo("Vetó la ley")
    assert vigia.normalizar_titulo("«Vetó» la ley - Diario Uno") == "vetó la ley"


def test_enlaces_de_infoleg_cumplen_el_patron():
    enlaces = vigia.extraer_enlaces(INFOLEG, "https://servicios.infoleg.gob.ar/infolegInternet/verVinculos.do",
                                    r"verNorma\.do.*\?id=\d+")
    assert [e.titulo for e in enlaces] == ["Decreto 647/2025", "Decreto 1/2027"]


def test_en_el_senado_filtra_por_el_texto_de_la_fila():
    enlaces = vigia.extraer_enlaces(SENADO, "https://www.senado.gob.ar/votaciones/actas", r"/votaciones/detalleActa/\d+",
                                    r"27\.795|financiamiento\s+(de\s+la\s+educaci[oó]n\s+)?universitari", bloque="tr")
    assert [e.url.rsplit("/", 1)[1] for e in enlaces] == ["2571", "2701"]
    assert enlaces[1].titulo.startswith("Insistencia en la ley 27.795")


def test_feed_respeta_la_fecha_de_corte_y_el_filtro():
    entradas = vigia.extraer_feed(FEED, filtro=r"C[aá]mara|multa", desde=date(2026, 10, 19))
    assert [e.url for e in entradas] == ["https://ejemplo.org/a", "https://news.google.com/rss/articles/XYZ"]
    assert entradas[0].fecha == "2026-10-20"


def test_lo_ya_citado_o_ignorado_no_es_novedad():
    conocidas = {vigia.normalizar_url("https://www.senado.gob.ar/votaciones/detalleActa/2571")}
    fuente = {"metodo": "enlaces", "url": "https://www.senado.gob.ar/votaciones/actas", "bloque": "tr",
              "patron": r"/votaciones/detalleActa/\d+", "filtro": r"27\.795|financiamiento",
              "ignorar": ["https://www.senado.gob.ar/votaciones/detalleActa/2701"]}
    assert vigia.novedades_de(fuente, SENADO, conocidas, None) == []
    fuente["ignorar"] = []
    assert [n.url for n in vigia.novedades_de(fuente, SENADO, conocidas, None)] == [
        "https://www.senado.gob.ar/votaciones/detalleActa/2701"]


def test_una_noticia_ya_cargada_no_es_novedad_aunque_cambie_el_enlace():
    # Google Noticias da un enlace propio: se reconoce por el título, sin « - Medio».
    conocidas = vigia.conocidos()
    fuente = {"metodo": "feed", "url": "https://news.google.com/rss", "filtro": "multa"}
    assert vigia.novedades_de(fuente, FEED, conocidas, date(2026, 10, 19)) == []


def test_los_enlaces_cargados_en_ley_yaml_son_conocidos():
    conocidas = vigia.conocidos()
    assert vigia.normalizar_url("https://www.senado.gob.ar/votaciones/detalleActa/2598") in conocidas
    assert vigia.normalizar_url("https://votaciones.hcdn.gob.ar/votacion/5702") in conocidas  # citado en una nota


def test_fuentes_yaml_es_valido():
    fuentes = vigia.leer_fuentes()
    assert fuentes and all(f["eje"] for f in fuentes)
    assert len({f["id"] for f in fuentes}) == len(fuentes)
    assert {f["id"] for f in vigia.leer_fuentes("ley")} >= {"infoleg-ley-27795-vinculos", "senado-votaciones"}


def test_fuente_con_metodo_desconocido_es_error(tmp_path):
    archivo = tmp_path / "fuentes.yaml"
    archivo.write_text("- {id: x, eje: ley, nombre: X, url: 'https://x.org', metodo: magia}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="método desconocido"):
        vigia.leer_fuentes(archivo=archivo)


def test_el_informe_incluye_el_procedimiento_de_carga():
    texto = vigia.informe("ley", date(2026, 10, 19), [({"nombre": "Senado", "url": "u"},
                                                       [vigia.Novedad("Acta 1", "https://x.org/1")])], [])
    assert "### Senado" in texto and "- [ ] [Acta 1](https://x.org/1)" in texto
    assert re.search(r"Buscar el original", texto) and "pull request" in texto


def test_solo_cuenta_como_caido_lo_que_ya_no_existe():
    spec = importlib.util.spec_from_file_location("verificar_enlaces", RAIZ / "scripts" / "verificar_enlaces.py")
    enlaces = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(enlaces)
    assert enlaces.caido(404) and enlaces.caido(410) and enlaces.caido("ConnectError")
    assert not any(enlaces.caido(c) for c in (200, 403, 429, 503, "ReadTimeout"))
