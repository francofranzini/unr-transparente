"""Revisa que respondan los enlaces de los eventos: la ficha de cada uno y sus noticias (ADR 0032).

Uso: .venv/bin/python scripts/verificar_enlaces.py [data/eventos/ley.yaml ...]

Sale con código 1 si alguna página ya no existe (404, 410) o su dominio no existe. Cada enlace con error se reintenta
una vez. Los sitios que rechazan pedidos automáticos (401, 403, 429, 503) o que tardan demasiado se informan aparte:
hay que abrirlos a mano. Si un enlace se cayó, su copia está en data/archivo_web.yaml (scripts/archivar_fuentes.py).
"""

import sys
from pathlib import Path

import httpx
import yaml

RAIZ = Path(__file__).resolve().parent.parent
CAIDA = {404, 410}


def enlaces(archivo: Path) -> list[tuple[str, str]]:
    salida = []
    for evento in yaml.safe_load(archivo.read_text(encoding="utf-8")) or []:
        salida.append((evento["id"], evento["url"]))
        salida += [(f"{evento['id']} · {n['medio']}", n["url"]) for n in evento.get("noticias", [])]
    return salida


def estado(cliente: httpx.Client, url: str, intentos: int = 2) -> int | str:
    for intento in range(intentos):
        try:
            codigo = cliente.get(url).status_code
        except httpx.HTTPError as e:
            codigo = e.__class__.__name__
        if codigo == 200 or intento == intentos - 1:
            return codigo
    return codigo


def caido(codigo: int | str) -> bool:
    """Solo lo que indica que la página ya no está: 404, 410 o un dominio que no existe."""
    return codigo in CAIDA or codigo == "ConnectError"


def main(archivos: list[Path]) -> int:
    caidos, bloqueados, total = [], [], 0
    with httpx.Client(follow_redirects=True, timeout=25, headers={"User-Agent": "Mozilla/5.0"}) as cliente:
        for archivo in archivos:
            vistos = set()
            for origen, url in enlaces(archivo):
                if url in vistos:
                    continue
                vistos.add(url)
                total += 1
                codigo = estado(cliente, url)
                if caido(codigo):
                    caidos.append(f"{origen}: {codigo} {url}")
                elif codigo != 200:
                    bloqueados.append(f"{origen}: {codigo} {url}")
    for linea in caidos:
        print("CAÍDO", linea)
    for linea in bloqueados:
        print("SIN PODER REVISAR (abrir a mano)", linea)
    print(f"{total} enlaces: {len(caidos)} caídos, {len(bloqueados)} sin poder revisar.")
    return 1 if caidos else 0


if __name__ == "__main__":
    rutas = [Path(a) for a in sys.argv[1:]] or [RAIZ / "data" / "eventos" / "ley.yaml"]
    sys.exit(main(rutas))
