"""Geometría de gráficos en SVG, calculada en el servidor (sin librerías de gráficos en el navegador)."""

import json
from decimal import Decimal

from app.formato import numero
from core.ejes import mes_legible

FORMATOS = {
    "ancho": {"ancho": 720, "alto": 300, "margen": {"izq": 64, "der": 132, "sup": 16, "inf": 28}},
    "angosto": {"ancho": 360, "alto": 280, "margen": {"izq": 52, "der": 96, "sup": 12, "inf": 26}},
}


def _paso_eje(maximo: float) -> float:
    for paso in (100_000, 250_000, 500_000, 1_000_000, 2_500_000):
        if maximo / paso <= 5:
            return paso
    return 5_000_000


def salario_contra_ley(serie: list[dict], formato: str = "ancho") -> dict:
    """Dos líneas: básico pagado y salario exigido por el art. 5 (desde nov-2023)."""
    ANCHO, ALTO, MARGEN = (FORMATOS[formato][k] for k in ("ancho", "alto", "margen"))
    n = len(serie)
    maximo = float(max(max(p["pagado"], p["exigido"] or 0) for p in serie))
    paso = _paso_eje(maximo)
    tope = paso * (int(maximo // paso) + 1)
    ancho_util = ANCHO - MARGEN["izq"] - MARGEN["der"]
    alto_util = ALTO - MARGEN["sup"] - MARGEN["inf"]

    def x(i: int) -> float:
        return round(MARGEN["izq"] + ancho_util * i / (n - 1), 1)

    def y(v: Decimal) -> float:
        return round(MARGEN["sup"] + alto_util * (1 - float(v) / tope), 1)

    def trazo(puntos: list[tuple[int, Decimal]]) -> str:
        return " ".join(f"{'M' if k == 0 else 'L'}{x(i)},{y(v)}" for k, (i, v) in enumerate(puntos))

    confirmados = [(i, p["pagado"]) for i, p in enumerate(serie) if p["vigencia"] != "no_confirmada"]
    ultimo_confirmado = confirmados[-1][0]
    no_confirmados = [(i, p["pagado"]) for i, p in enumerate(serie) if i >= ultimo_confirmado]
    exigido = [(i, p["exigido"]) for i, p in enumerate(serie) if p["exigido"] is not None]

    ticks_y = [{"y": y(Decimal(v)), "texto": f"$ {numero(Decimal(v) / 1_000_000, 1)} M" if v else "0"}
               for v in range(0, int(tope) + 1, int(paso))]
    ticks_x = [{"x": x(i), "texto": p["periodo"][:4]} for i, p in enumerate(serie) if p["periodo"].endswith("-01")]
    fin = n - 1
    puntos = [{"x": x(i), "mes": mes_legible(p["periodo"]),
               "pagado": f"$ {numero(p['pagado'])}",
               "exigido": f"$ {numero(p['exigido'])}" if p["exigido"] is not None else None,
               "brecha": (f"{numero((p['exigido'] / p['pagado'] - 1) * 100, 1)} %"
                          if p["exigido"] is not None else None),
               "vigencia": p["vigencia"], "y_pagado": y(p["pagado"]),
               "y_exigido": y(p["exigido"]) if p["exigido"] is not None else None}
              for i, p in enumerate(serie)]
    return {
        "formato": formato, "ancho": ANCHO, "alto": ALTO, "margen": MARGEN,
        "pagado": trazo(confirmados), "pagado_no_confirmado": trazo(no_confirmados) if len(no_confirmados) > 1 else "",
        "exigido": trazo(exigido),
        "fin_pagado": {"x": x(fin), "y": y(serie[fin]["pagado"])},
        "fin_exigido": {"x": x(fin), "y": y(serie[fin]["exigido"])},
        "inicio_exigido": {"x": x(exigido[0][0]), "y": y(exigido[0][1])},
        "ticks_y": ticks_y, "ticks_x": ticks_x,
        "puntos_json": json.dumps(puntos, ensure_ascii=False),
        "base_y": y(Decimal(0)),
    }
