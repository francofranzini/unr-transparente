"""Verifica la transcripción de los anexos de la Res. C.S. UNR 1016/2022 (presupuesto 2023).

Cada rubro debe sumar su subtotal, y los subtotales el total. Las discrepancias
que están en el documento original se declaran explícitamente acá; cualquier
otra diferencia es un error de transcripción.
"""

import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
ANEXO1 = DATA / "unr_presupuesto_2023_anexo1.csv"
ANEXO2 = DATA / "unr_presupuesto_2023_anexo2_facultades.csv"

# Discrepancias del original (subtotal impreso - suma del detalle impreso).
DISCREPANCIAS_ANEXO1 = {"Asociación Universidades Grupo Montevideo": Decimal("45.10")}
# El Anexo II redondea a centavos fila por fila.
TOLERANCIA_ANEXO2 = Decimal("0.05")

TOTAL_LEY_27701_UNR = Decimal("34259832336")


def _leer(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_ficha_completa():
    for path in (ANEXO1, ANEXO2):
        for fila in _leer(path):
            for campo in ("id", "valor", "unidad", "periodo", "tipo_fuente", "documento", "url", "pagina", "consultado"):
                assert fila[campo], f"{path.name}: {fila['id']} sin {campo}"


def test_ids_unicos():
    ids = [f["id"] for path in (ANEXO1, ANEXO2) for f in _leer(path)]
    assert len(ids) == len(set(ids))


def test_items_suman_su_rubro():
    filas = _leer(ANEXO1)
    rubros = {f["rubro"]: Decimal(f["valor"]) for f in filas if f["nivel"] == "rubro"}
    items = defaultdict(Decimal)
    for f in filas:
        if f["nivel"] == "item" and f["rubro"] in rubros:
            items[f["rubro"]] += Decimal(f["valor"])
    for rubro, suma in items.items():
        esperado = DISCREPANCIAS_ANEXO1.get(rubro, Decimal(0))
        assert rubros[rubro] - suma == esperado, rubro


def test_rubros_suman_el_total():
    filas = _leer(ANEXO1)
    por_nivel = {f["rubro"]: Decimal(f["valor"]) for f in filas if f["nivel"] in ("total", "subtotal")}
    rubros = {f["rubro"]: Decimal(f["valor"]) for f in filas if f["nivel"] == "rubro"}
    funcionamiento = sum(v for r, v in rubros.items() if r != "Personal")
    assert funcionamiento == por_nivel["Total Gastos de Funcionamiento"]
    assert rubros["Personal"] + funcionamiento == por_nivel["Total Gastos"]


def test_total_coincide_con_ley_27701():
    total = next(Decimal(f["valor"]) for f in _leer(ANEXO1) if f["nivel"] == "total")
    assert total == TOTAL_LEY_27701_UNR


def test_anexo2_filas_y_columnas():
    filas = _leer(ANEXO2)
    tabla = defaultdict(dict)
    for f in filas:
        tabla[f["dependencia"]][f["componente"]] = Decimal(f["valor"])
    totales = tabla.pop("Totales")
    for dep, c in tabla.items():
        assert abs(c["historico"] + c["nuevo_modelo"] - c["total"]) <= TOLERANCIA_ANEXO2, dep
    for comp in ("historico", "nuevo_modelo", "total"):
        suma = sum(c[comp] for c in tabla.values())
        assert abs(suma - totales[comp]) <= TOLERANCIA_ANEXO2, comp
    for comp in ("porcentaje_historico", "porcentaje_nuevo_modelo"):
        assert sum(c[comp] for c in tabla.values()) == Decimal(100), comp


def test_anexo2_coincide_con_anexo1():
    a1 = {f["item"]: Decimal(f["valor"]) for f in _leer(ANEXO1) if f["nivel"] == "item"}
    a2 = {f["componente"]: Decimal(f["valor"]) for f in _leer(ANEXO2) if f["dependencia"] == "Totales"}
    assert abs(a1["Facultades y Escuelas"] - a2["historico"]) <= TOLERANCIA_ANEXO2
    assert abs(a1["Facultades y Escuelas Nuevo Modelo"] - a2["nuevo_modelo"]) <= TOLERANCIA_ANEXO2
