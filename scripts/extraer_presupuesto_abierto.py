"""Extrae de un CSV de crédito anual de Presupuesto Abierto las transferencias del Programa 26 por universidad.

Uso:
    python scripts/extraer_presupuesto_abierto.py <credito-anual-AAAA.csv> <url-del-zip> <AAAA-MM-DD consultado> > data/ejecucion_programa26_AAAA.csv

El resultado es una propuesta para revisar a mano antes de versionarla (ADR 0010): no hay ingesta automática.
Presupuesto Abierto informa en millones de pesos; acá se convierte a pesos.
"""

import csv
import re
import sys
from collections import defaultdict
from decimal import Decimal
from unicodedata import normalize

PROGRAMA = "Desarrollo de la Educacion Superior"
PARCIAL = "Transferencias a universidades nacionales"
UNR = "Universidad Nacional de Rosario"
SIN_DISCRIMINAR = "Universidades sin Discriminar"
INDICADORES = {
    "credito_presupuestado": "credito_asignado",
    "credito_vigente": "credito_vigente",
    "credito_devengado": "devengado",
}
COLUMNAS = ["id", "valor", "unidad", "entidad", "indicador", "universidad", "actividad", "fecha_corte",
            "periodo", "tipo_fuente", "documento", "url", "pagina", "consultado", "nota"]


def _slug(texto: str) -> str:
    texto = normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", texto).strip("-")


def _pesos(millones: Decimal) -> str:
    texto = f"{millones * 1_000_000:f}"
    return texto.rstrip("0").rstrip(".") if "." in texto else texto


def _entidad(universidad: str) -> str:
    if universidad == UNR:
        return "UNR"
    if universidad == SIN_DISCRIMINAR:
        return "CREDITO_NO_ASIGNADO"
    return "OTRA_UNIVERSIDAD"


def extraer(path: str) -> tuple[str, str, dict, dict]:
    por_universidad = defaultdict(lambda: defaultdict(Decimal))
    unr_por_actividad = defaultdict(lambda: defaultdict(Decimal))
    anio = leyenda = None
    with open(path, encoding="utf-8-sig") as f:
        for fila in csv.DictReader(f):
            if not (fila["programa_desc"].startswith(PROGRAMA) and fila["parcial_desc"].startswith(PARCIAL)):
                continue
            anio, leyenda = fila["ejercicio_presupuestario"], fila["ultima_actualizacion_fecha"]
            universidad = fila["subparcial_desc"]
            for columna in INDICADORES:
                millones = Decimal(fila[columna].replace(",", "."))
                por_universidad[universidad][columna] += millones
                if universidad == UNR:
                    unr_por_actividad[(fila["actividad_id"], fila["actividad_desc"])][columna] += millones
    return anio, leyenda, por_universidad, unr_por_actividad


def main(path: str, url: str, consultado: str) -> None:
    anio, leyenda, por_universidad, unr_por_actividad = extraer(path)
    fecha = re.search(r"(\d{1,2}) (\w+) (\d{4})", leyenda)
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
             "septiembre", "octubre", "noviembre", "diciembre"]
    fecha_corte = f"{fecha[3]}-{meses.index(fecha[2].lower()) + 1:02d}-{int(fecha[1]):02d}"
    documento = (f"Presupuesto Abierto — Crédito anual {anio} (datos abiertos). Programa 26 «{PROGRAMA}», "
                 f"partida «{PARCIAL}…», apertura por universidad (subparcial)")
    salida = csv.DictWriter(sys.stdout, COLUMNAS, lineterminator="\n")
    salida.writeheader()

    def escribir(universidad: str, actividad: tuple[str, str] | None, montos: dict) -> None:
        for columna, indicador in INDICADORES.items():
            sufijo = f"-act{actividad[0]}" if actividad else ""
            salida.writerow({
                "id": f"pa{anio}-p26-{_slug(universidad)[:50]}{sufijo}-{indicador.replace('_', '-')}",
                "valor": _pesos(montos[columna]),
                "unidad": "ARS corrientes", "entidad": _entidad(universidad), "indicador": indicador,
                "universidad": universidad, "actividad": actividad[1] if actividad else "", "fecha_corte": fecha_corte,
                "periodo": anio, "tipo_fuente": "primaria", "documento": documento, "url": url, "pagina": "",
                "consultado": consultado,
                "nota": f"{leyenda} Valor original en millones de pesos; fuente de financiamiento Tesoro Nacional.",
            })

    for universidad in sorted(por_universidad):
        escribir(universidad, None, por_universidad[universidad])
    for actividad in sorted(unr_por_actividad):
        escribir(UNR, actividad, unr_por_actividad[actividad])


if __name__ == "__main__":
    main(*sys.argv[1:4])
