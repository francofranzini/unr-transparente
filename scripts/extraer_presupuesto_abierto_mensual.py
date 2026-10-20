"""Extrae de un CSV de crédito mensual de Presupuesto Abierto el devengado mensual por actividad del Programa 26.

Uso:
    python scripts/extraer_presupuesto_abierto_mensual.py unr <credito-mensual-AAAA.csv> <url-del-zip> <AAAA-MM-DD consultado> \
        > data/presupuesto_unr_mensual_AAAA.csv
    python scripts/extraer_presupuesto_abierto_mensual.py sistema <credito-mensual-AAAA.csv> <url-del-zip> <AAAA-MM-DD> \
        > data/presupuesto_sistema_mensual_AAAA.csv

`unr`: todas las actividades de la UNR. `sistema`: las actividades de los arts. 3 y 4 de la Ley 27.795 (14, 15, 16 y 25),
sumadas para todas las universidades, y aparte el crédito sin universidad asignada («Universidades sin Discriminar»).

El resultado es una propuesta para revisar a mano antes de versionarla (ADR 0010): no hay ingesta automática.
Presupuesto Abierto informa en millones de pesos; acá se convierte a pesos. Se suman todas las fuentes de
financiamiento (en 2024 hay «Tesoro Nacional» y «Crédito Interno»); la nota de cada fila dice cuánto vino de cada una.
Los meses posteriores al de la fecha de corte no se escriben: todavía no ocurrieron.
"""

import csv
import re
import sys
from collections import defaultdict
from decimal import Decimal

from extraer_presupuesto_abierto import PARCIAL, PROGRAMA, SIN_DISCRIMINAR, UNR, _pesos

ACTIVIDADES_ARTS_3_4 = ("14", "15", "16", "25")
COLUMNAS = ["id", "valor", "unidad", "entidad", "indicador", "actividad_id", "actividad", "fecha_corte",
            "periodo", "tipo_fuente", "documento", "url", "pagina", "consultado", "nota"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]


GRUPOS = {
    # alcance → {entidad: (slug del id, descripción para el documento)}
    "unr": {"UNR": ("unr", f"subparcial «{UNR}»")},
    "sistema": {"SISTEMA_UNIVERSITARIO": ("sistema", "suma de todas las universidades (subparciales)"),
                "CREDITO_NO_ASIGNADO": ("sin-asignar", f"subparcial «{SIN_DISCRIMINAR}»")},
}


def _grupo(alcance: str, fila: dict) -> str | None:
    universidad = fila["subparcial_desc"]
    if alcance == "unr":
        return "UNR" if universidad == UNR else None
    if fila["actividad_id"] not in ACTIVIDADES_ARTS_3_4:
        return None
    return "CREDITO_NO_ASIGNADO" if universidad == SIN_DISCRIMINAR else "SISTEMA_UNIVERSITARIO"


def extraer(alcance: str, path: str) -> tuple[str, str, dict, dict, dict]:
    devengado = defaultdict(lambda: defaultdict(Decimal))  # (entidad, actividad_id, desc) → mes → millones
    por_fuente = defaultdict(lambda: defaultdict(Decimal))  # (entidad, actividad_id, mes) → fuente → millones
    universidades = defaultdict(set)  # (entidad, actividad_id) → universidades con devengado
    anio = leyenda = None
    with open(path, encoding="utf-8-sig") as f:
        for fila in csv.DictReader(f):
            if not (fila["programa_desc"].startswith(PROGRAMA) and fila["parcial_desc"].startswith(PARCIAL)):
                continue
            entidad = _grupo(alcance, fila)
            if entidad is None:
                continue
            anio, leyenda = fila["ejercicio_presupuestario"], fila["ultima_actualizacion_fecha"]
            actividad = (entidad, fila["actividad_id"], fila["actividad_desc"])
            mes = int(fila["impacto_presupuestario_mes"])
            millones = Decimal(fila["credito_devengado"].replace(",", "."))
            devengado[actividad][mes] += millones
            por_fuente[(entidad, actividad[1], mes)][fila["fuente_financiamiento_desc"]] += millones
            if millones:
                universidades[(entidad, actividad[1])].add(fila["subparcial_desc"])
    return anio, leyenda, devengado, por_fuente, universidades


def main(alcance: str, path: str, url: str, consultado: str) -> None:
    anio, leyenda, devengado, por_fuente, universidades = extraer(alcance, path)
    fecha = re.search(r"(\d{1,2}) (\w+) (\d{4})", leyenda)
    fecha_corte = f"{fecha[3]}-{MESES.index(fecha[2].lower()) + 1:02d}-{int(fecha[1]):02d}"
    ultimo_mes = 12 if fecha[3] != anio else MESES.index(fecha[2].lower()) + 1
    salida = csv.DictWriter(sys.stdout, COLUMNAS, lineterminator="\n")
    salida.writeheader()
    for entidad, (slug, descripcion) in GRUPOS[alcance].items():
        documento = (f"Presupuesto Abierto — Crédito mensual {anio} (datos abiertos). Programa 26 «{PROGRAMA}», "
                     f"partida «{PARCIAL}…», {descripcion}, devengado por actividad y mes de impacto")
        for actividad in sorted((a for a in devengado if a[0] == entidad), key=lambda a: int(a[1])):
            if alcance == "unr" and not any(devengado[actividad].values()):
                continue
            n = len(universidades[(entidad, actividad[1])])
            cuantas = f" Suma de {n} universidades con devengado en el año." if entidad == "SISTEMA_UNIVERSITARIO" else ""
            for mes in range(1, ultimo_mes + 1):
                fuentes = {f: m for f, m in por_fuente[(entidad, actividad[1], mes)].items() if m}
                detalle = " + ".join(f"{f} {m:f}" for f, m in sorted(fuentes.items())) if len(fuentes) > 1 else ""
                parcial = " Mes en curso a la fecha de corte." if fecha[3] == anio and mes == ultimo_mes else ""
                salida.writerow({
                    "id": f"pa{anio}-mensual-{slug}-act{actividad[1]}-{anio}-{mes:02d}-devengado",
                    "valor": _pesos(devengado[actividad][mes]),
                    "unidad": "ARS corrientes", "entidad": entidad, "indicador": "devengado",
                    "actividad_id": actividad[1], "actividad": actividad[2], "fecha_corte": fecha_corte,
                    "periodo": f"{anio}-{mes:02d}", "tipo_fuente": "primaria", "documento": documento, "url": url,
                    "pagina": "", "consultado": consultado,
                    "nota": (f"{leyenda} Valor original en millones de pesos; suma de todas las fuentes de "
                             f"financiamiento" + (f" (millones: {detalle})" if detalle else "") + "." + cuantas
                             + parcial),
                })


if __name__ == "__main__":
    main(*sys.argv[1:5])
