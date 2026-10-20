"""Carga automática de la ley (ADR 0033), sin red: páginas y feeds de ejemplo con la estructura de las fuentes reales."""

import importlib.util
import sys
from datetime import date
from pathlib import Path

import yaml

from core.carga import cargar
from core.modelos import Evento

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
_spec = importlib.util.spec_from_file_location("actualizar_ley", RAIZ / "scripts" / "actualizar_ley.py")
al = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(al)

INFOLEG = """<table><tr><td>Número</td><td>Fecha</td><td>Descripción</td></tr>
<tr> <td class="vr_azul11"> <a href="/infolegInternet/verNorma.do;jsessionid=ABC?id=417371">Decreto&nbsp; 647/2025</a>
 PODER EJECUTIVO NACIONAL (P.E.N.)<br/> </td> <td class="vr_azul11" align="center"> 10-sep-2025 </td>
 <td class="vr_azul11"> <b>VETO</b> <br/> PROYECTO DE LEY Nº 27.795 - OBSERVASE </td> </tr></table>"""

ACTA = """<div>Acta Nro: 10 Insistencia en la sanción original del proyecto de ley registrado bajo el número 27.795, que fuera
vetado totalmente por el Poder Ejecutivo Nacional. CD-20/25-CD 02/10/2025 - 18:31 DOS TERCIOS DE VOTOS EMITIDOS
AFIRMATIVO OTRA <span>58</span> AFIRMATIVOS 7 NEGATIVOS 4 ABSTENCIONES 3 AUSENTES</div>"""

SITEMAP = """<urlset><url><loc>https://www.ambito.com/politica/nota-n1</loc><news:news>
<news:publication_date>2026-10-15T23:30:00-03:00</news:publication_date><news:title>La Justicia suspendió las multas</news:title>
</news:news></url></urlset>"""

RSS = """<rss><channel><item><title><![CDATA[Financiamiento universitario: nuevo fallo]]></title>
<link>https://www.infobae.com/politica/2026/10/16/nota/</link><pubDate>Fri, 16 Oct 2026 02:00:00 GMT</pubDate></item>
</channel></rss>"""


def _hito(id_: str, fecha: str) -> Evento:
    return Evento(id=id_, fecha=fecha, tipo="judicial", ejes=["ley"], titulo="x", tipo_fuente="secundaria",
                  documento="d", url="https://ejemplo.org", consultado=date(2026, 10, 19))


def test_lee_las_normas_de_infoleg():
    [norma] = al.leer_normas_infoleg(INFOLEG, "https://servicios.infoleg.gob.ar/infolegInternet/verVinculos.do")
    assert norma.numero == "Decreto 647/2025" and norma.fecha == "2025-09-10"
    assert norma.dependencia == "PODER EJECUTIVO NACIONAL (P.E.N.)"
    assert norma.descripcion == "VETO PROYECTO DE LEY Nº 27.795 - OBSERVASE"
    assert norma.url == "https://servicios.infoleg.gob.ar/infolegInternet/verNorma.do?id=417371"  # sin la sesión


def test_lee_el_acta_del_senado():
    v = al.leer_acta_senado(ACTA, "https://www.senado.gob.ar/votaciones/detalleActa/2598")
    assert (v.acta, v.fecha, v.resultado) == ("10", "2025-10-02", "afirmativo")
    assert (v.afirmativos, v.negativos, v.abstenciones, v.ausentes) == (58, 7, 4, 3)
    assert v.titulo.startswith("Insistencia en la sanción original") and "CD-20" not in v.titulo


def test_lee_rss_y_mapas_de_noticias_con_la_fecha_de_argentina():
    [(titulo, enlace, publicado)] = al.entradas_feed(SITEMAP)
    assert titulo == "La Justicia suspendió las multas" and al.fecha_argentina(publicado) == date(2026, 10, 15)
    [(titulo, enlace, publicado)] = al.entradas_feed(RSS)
    assert titulo == "Financiamiento universitario: nuevo fallo"
    assert al.fecha_argentina(publicado) == date(2026, 10, 15)  # 2:00 GMT es el día anterior en Argentina


def test_una_nota_se_suma_solo_si_coincide_con_un_unico_hito():
    hitos = [_hito("multa", "2026-10-14"), _hito("queja", "2026-10-15")]
    claves = {"multa": "multa diaria|impuso una multa", "queja": "suspend\\w* (las )?multas"}
    assert al.hito_de_nota("La Justicia suspendió las multas", date(2026, 10, 15), hitos, claves) == ("queja", "")
    assert al.hito_de_nota("Impuso una multa diaria", date(2026, 10, 15), hitos, claves) == ("multa", "")
    hito, motivo = al.hito_de_nota("Marcha universitaria", date(2026, 10, 15), hitos, claves)
    assert hito is None and "no coincide" in motivo
    hito, motivo = al.hito_de_nota("Impuso una multa diaria", date(2026, 10, 30), hitos, claves)
    assert hito is None and "hecho nuevo" in motivo  # fuera de los 3 días
    hito, motivo = al.hito_de_nota("Suspendió las multas e impuso una multa diaria", date(2026, 10, 15), hitos, claves)
    assert hito is None and "más de un hito" in motivo


def test_lo_que_escribe_el_script_sigue_siendo_un_ley_yaml_valido(tmp_path):
    texto = (RAIZ / "data" / "eventos" / "ley.yaml").read_text(encoding="utf-8")
    texto = al.agregar_noticia(texto, "ley-27795-multa", "Medio de prueba", "Título «con comillas»",
                               "https://ejemplo.org/nota", "2026-10-15")
    texto = al.agregar_evento(texto, al.bloque_evento("ley-27795-decreto-1-2027", "2027-01-02", "norma",
                                                      "Decreto 1/2027: título de prueba", "InfoLEG — Decreto 1/2027",
                                                      "https://ejemplo.org/norma", "Cargado automáticamente."))
    (tmp_path / "eventos").mkdir()
    (tmp_path / "eventos" / "ley.yaml").write_text(texto, encoding="utf-8")
    eventos = {e.id: e for e in cargar(tmp_path).eventos}
    assert eventos["ley-27795-multa"].noticias[-1].titulo == "Título «con comillas»"
    assert eventos["ley-27795-decreto-1-2027"].tipo_fuente.value == "primaria"
    # El evento de estado sigue al final del archivo.
    assert list(eventos)[-1].startswith("estado-")


def test_las_claves_de_los_hitos_son_validas():
    import re
    claves = yaml.safe_load((RAIZ / "data" / "vigia" / "claves_ley.yaml").read_text(encoding="utf-8"))
    ids = {e.id for e in cargar().eventos_de("ley")}
    for hito, patron in claves.items():
        assert hito in ids, f"claves_ley.yaml: {hito} no existe en ley.yaml"
        re.compile(patron)
