"""Copias de las fuentes en la Wayback Machine (ADR 0035), para cuando un enlace se cae.

Uso: .venv/bin/python scripts/archivar_fuentes.py [--guardar] [--limite 10] [--revisar] [data/eventos/ley.yaml ...]

- Sin opciones: busca la copia más reciente de cada enlace (ficha y noticias de cada evento) y la registra en
  data/archivo_web.yaml. La aplicación no lee ese archivo.
- --guardar: además pide a la Wayback Machine una copia de los enlaces que no tienen ninguna (hasta --limite por
  corrida, porque el servicio limita los pedidos). Se usa al cargar un hecho nuevo.
- --revisar: no escribe nada; solo informa qué enlaces no tienen copia registrada (lo usa el workflow semanal).
"""

import argparse
import re
import sys
import time
from pathlib import Path

import httpx
import yaml

RAIZ = Path(__file__).resolve().parent.parent
REGISTRO = RAIZ / "data" / "archivo_web.yaml"
DISPONIBLE = "https://archive.org/wayback/available"
GUARDAR = "https://web.archive.org/save/"
ENCABEZADO = ("# Copias de las fuentes en la Wayback Machine (ADR 0035). Las escribe scripts/archivar_fuentes.py;\n"
              "# la aplicación no lee este archivo. Si un enlace de un evento se cae, la copia está acá.\n")


def enlaces(archivos: list[Path]) -> list[str]:
    """Primero la ficha de cada evento (el documento que lo sostiene), después las noticias."""
    fichas, noticias = [], []
    for archivo in archivos:
        for evento in yaml.safe_load(archivo.read_text(encoding="utf-8")) or []:
            fichas.append(evento["url"])
            noticias += [n["url"] for n in evento.get("noticias", [])]
    return list(dict.fromkeys(fichas + noticias))


def leer_registro(archivo: Path = REGISTRO) -> dict[str, dict]:
    if not archivo.exists():
        return {}
    return {fila["url"]: fila for fila in yaml.safe_load(archivo.read_text(encoding="utf-8")) or []}


def escribir_registro(registro: dict[str, dict], archivo: Path = REGISTRO) -> None:
    filas = [registro[u] for u in sorted(registro)]
    archivo.write_text(ENCABEZADO + yaml.safe_dump(filas, allow_unicode=True, sort_keys=False, width=200),
                       encoding="utf-8")


def copia_existente(cliente: httpx.Client, url: str) -> dict | None:
    try:
        cercana = cliente.get(DISPONIBLE, params={"url": url}).json()["archived_snapshots"].get("closest")
    except (httpx.HTTPError, ValueError, KeyError):
        return None
    if not cercana or not cercana.get("available"):
        return None
    marca = cercana["timestamp"]
    return {"url": url, "copia": cercana["url"].replace("http://", "https://", 1),
            "fecha": f"{marca[:4]}-{marca[4:6]}-{marca[6:8]}"}


def copia_recien_pedida(cliente: httpx.Client, url: str) -> dict | None:
    """La API tarda en indexar una copia nueva: se sigue la redirección de /web/<url> hasta la copia con fecha."""
    try:
        final = str(cliente.head(f"https://web.archive.org/web/{url}", timeout=90).url)
    except httpx.HTTPError:
        return None
    m = re.search(r"/web/(\d{14})/", final)
    if not m:
        return None
    marca = m.group(1)
    return {"url": url, "copia": final, "fecha": f"{marca[:4]}-{marca[4:6]}-{marca[6:8]}"}


def pedir_copia(cliente: httpx.Client, url: str) -> bool:
    try:
        return cliente.get(GUARDAR + url, timeout=120).status_code < 400
    except httpx.HTTPError:
        return False


def main() -> int:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("archivos", nargs="*", type=Path)
    argumentos.add_argument("--guardar", action="store_true")
    argumentos.add_argument("--revisar", action="store_true")
    argumentos.add_argument("--limite", type=int, default=10)
    opciones = argumentos.parse_args()
    archivos = opciones.archivos or [RAIZ / "data" / "eventos" / "ley.yaml"]

    registro = leer_registro()
    faltan = [u for u in enlaces(archivos) if u not in registro]
    if opciones.revisar:
        for url in faltan:
            print("SIN COPIA REGISTRADA", url)
        print(f"{len(faltan)} enlaces sin copia registrada en {REGISTRO.name}.")
        return 0

    nuevas, pedidas, sin_copia = 0, 0, []
    with httpx.Client(follow_redirects=True, timeout=30, headers={"User-Agent": "Mozilla/5.0"}) as cliente:
        for url in faltan:
            fila = copia_existente(cliente, url)
            if fila is None and opciones.guardar and pedidas < opciones.limite:
                pedidas += 1
                if pedir_copia(cliente, url):
                    time.sleep(5)
                    fila = copia_existente(cliente, url) or copia_recien_pedida(cliente, url)
            if fila:
                registro[url] = fila
                nuevas += 1
            else:
                sin_copia.append(url)
    escribir_registro(registro)
    for url in sin_copia:
        print("SIN COPIA", url)
    print(f"{nuevas} copias registradas ({pedidas} pedidas ahora); {len(sin_copia)} enlaces siguen sin copia.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
