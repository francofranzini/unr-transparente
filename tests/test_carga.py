import textwrap

import pytest

from core.carga import ErrorDeCarga, cargar

ENCABEZADO = "id,valor,unidad,entidad,indicador,periodo,tipo_fuente,documento,url,pagina,consultado,nota\n"
FILA_OK = "unr-x-2026,10,personas,UNR,alumnos,2026,primaria,Doc,https://ejemplo.org/doc.pdf,,2026-10-19,\n"


def test_datos_del_repositorio_cargan():
    repo = cargar()
    assert repo.datos and repo.eventos


def test_fila_completa_carga(tmp_path):
    (tmp_path / "a.csv").write_text(ENCABEZADO + FILA_OK, encoding="utf-8")
    assert "unr-x-2026" in cargar(tmp_path).datos


@pytest.mark.parametrize("campo", ["documento", "url", "consultado", "tipo_fuente", "periodo"])
def test_fila_sin_ficha_completa_es_error(tmp_path, campo):
    columnas = ENCABEZADO.strip().split(",")
    valores = FILA_OK.strip().split(",")
    valores[columnas.index(campo)] = ""
    (tmp_path / "a.csv").write_text(ENCABEZADO + ",".join(valores) + "\n", encoding="utf-8")
    with pytest.raises(ErrorDeCarga) as e:
        cargar(tmp_path)
    assert campo in str(e.value)


def test_columnas_extra_van_a_dimensiones(tmp_path):
    (tmp_path / "a.csv").write_text(ENCABEZADO.replace("\n", ",rubro\n") + FILA_OK.replace("\n", ",Personal\n"),
                                    encoding="utf-8")
    assert cargar(tmp_path).datos["unr-x-2026"].dimensiones == {"rubro": "Personal"}


def test_id_duplicado_es_error(tmp_path):
    (tmp_path / "a.csv").write_text(ENCABEZADO + FILA_OK, encoding="utf-8")
    (tmp_path / "b.csv").write_text(ENCABEZADO + FILA_OK, encoding="utf-8")
    with pytest.raises(ErrorDeCarga, match="duplicado"):
        cargar(tmp_path)


def test_evento_sin_url_es_error(tmp_path):
    (tmp_path / "eventos.yaml").write_text(textwrap.dedent("""
        - id: e1
          fecha: "2026-01"
          tipo: estado
          ejes: [control]
          titulo: Algo
          tipo_fuente: primaria
          documento: Doc
          consultado: 2026-10-19
    """), encoding="utf-8")
    with pytest.raises(ErrorDeCarga, match="url"):
        cargar(tmp_path)


EVENTO = """
- id: {id}
  fecha: "2026-01"
  tipo: estado
  ejes: [control]
  titulo: Algo
  tipo_fuente: primaria
  documento: Doc
  url: https://ejemplo.org
  consultado: 2026-10-19
"""


def test_eventos_por_tema_en_carpeta(tmp_path):
    (tmp_path / "eventos").mkdir()
    (tmp_path / "eventos" / "ley.yaml").write_text(EVENTO.format(id="e1"), encoding="utf-8")
    (tmp_path / "eventos" / "control.yaml").write_text(EVENTO.format(id="e2"), encoding="utf-8")
    assert sorted(e.id for e in cargar(tmp_path).eventos) == ["e1", "e2"]


def test_id_de_evento_repetido_entre_archivos_es_error(tmp_path):
    (tmp_path / "eventos").mkdir()
    (tmp_path / "eventos" / "ley.yaml").write_text(EVENTO.format(id="e1"), encoding="utf-8")
    (tmp_path / "eventos" / "control.yaml").write_text(EVENTO.format(id="e1"), encoding="utf-8")
    with pytest.raises(ErrorDeCarga, match="duplicado"):
        cargar(tmp_path)
