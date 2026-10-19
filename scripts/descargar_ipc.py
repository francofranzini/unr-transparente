"""Descarga el IPC nacional mensual (INDEC, base dic-2016) de la API de series de tiempo y escribe data/ipc.csv.

Uso: python scripts/descargar_ipc.py [desde AAAA-MM-DD]

Es una de las fuentes vigiladas (ADR 0010). Revisar el diff antes de versionar: el INDEC puede revisar valores.
"""

import csv
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

SERIE = "148.3_INIVELNAL_DICI_M_26"
URL = f"https://apis.datos.gob.ar/series/api/series/?ids={SERIE}&format=json&limit=1000"
SALIDA = Path(__file__).resolve().parent.parent / "data" / "ipc.csv"
COLUMNAS = ["id", "valor", "unidad", "entidad", "indicador", "periodo", "tipo_fuente", "documento", "url", "pagina",
            "consultado", "nota"]


def main(desde: str = "2022-11-01") -> None:
    url = f"{URL}&start_date={desde}"
    pedido = urllib.request.Request(url, headers={"User-Agent": "portal-transparencia-unr/0.1"})
    with urllib.request.urlopen(pedido, timeout=30) as respuesta:
        datos = json.load(respuesta)["data"]
    hoy = date.today().isoformat()
    with SALIDA.open("w", newline="", encoding="utf-8") as f:
        salida = csv.DictWriter(f, COLUMNAS, lineterminator="\n")
        salida.writeheader()
        for fecha, valor in datos:
            periodo = fecha[:7]
            salida.writerow({
                "id": f"ipc-nacional-{periodo}", "valor": valor, "unidad": "índice", "entidad": "INDEC",
                "indicador": "ipc_nivel_general", "periodo": periodo, "tipo_fuente": "primaria",
                "documento": "INDEC — IPC Nivel General Nacional, base dic-2016 (API de series de tiempo, serie "
                             f"{SERIE})",
                "url": url, "pagina": "", "consultado": hoy, "nota": "",
            })
    print(f"{len(datos)} meses escritos en {SALIDA} (último: {datos[-1][0][:7]})")


if __name__ == "__main__":
    main(*sys.argv[1:2])
