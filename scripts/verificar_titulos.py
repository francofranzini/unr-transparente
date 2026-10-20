"""Compara el título guardado de cada noticia con el `og:title` de su página (ESTANDAR §5.7).

Uso: .venv/bin/python scripts/verificar_titulos.py [data/eventos/ley.yaml ...]
Sale con código 1 si algún título no coincide. Las páginas que no responden se informan aparte:
hay que revisarlas a mano, no cuentan como error.
"""

import html
import re
import sys
import unicodedata
from pathlib import Path

import httpx
import yaml

RAIZ = Path(__file__).resolve().parent.parent
# Sufijos con el nombre del medio que algunas páginas agregan al og:title.
SUFIJO = re.compile(r"\s*[|\-–—]\s*(canal26\.com|Microjuris Argentina al Día|NoticiasNQN|Chequeado|Infobae|Perfil|La Nación|"
                    r"Página\|?12|Tiempo Argentino|El Destape|Ámbito|La Capital|iProfesional|InfoGremiales)\s*$", re.I)
OG_TITLE = re.compile(r"""<meta[^>]+(?:property|name)=["']og:title["'][^>]*>""", re.I)
CONTENT = re.compile(r"""content=["']([^"']*)["']""", re.I)
TITLE = re.compile(r"<title[^>]*>([^<]*)</title>", re.I)  # respaldo: páginas AMP sin og:title


def normalizar(texto: str) -> str:
    texto = html.unescape(html.unescape(texto))  # algunas páginas codifican dos veces (&amp;quot;)
    texto = unicodedata.normalize("NFC", texto).replace("“", '"').replace("”", '"')
    return " ".join(texto.split())


def og_title(cliente: httpx.Client, url: str) -> str | None:
    try:
        r = cliente.get(url)
    except httpx.HTTPError:
        return None
    if r.status_code != 200:
        return None
    if (meta := OG_TITLE.search(r.text)) and (c := CONTENT.search(meta.group(0))):
        return SUFIJO.sub("", normalizar(c.group(1)))
    if t := TITLE.search(r.text):
        return SUFIJO.sub("", normalizar(t.group(1)))
    return None


def main(archivos: list[Path]) -> int:
    distintos, sin_respuesta = [], []
    with httpx.Client(follow_redirects=True, timeout=20, headers={"User-Agent": "Mozilla/5.0"}) as cliente:
        for archivo in archivos:
            for evento in yaml.safe_load(archivo.read_text(encoding="utf-8")) or []:
                for n in evento.get("noticias", []):
                    leido = og_title(cliente, n["url"])
                    if leido is None:
                        sin_respuesta.append(f"{evento['id']} · {n['medio']}: {n['url']}")
                    elif leido != normalizar(n["titulo"]):
                        distintos.append(f"{evento['id']} · {n['medio']}\n  guardado: {n['titulo']}\n  og:title: {leido}")
    for linea in distintos:
        print("DISTINTO", linea)
    for linea in sin_respuesta:
        print("SIN og:title (revisar a mano)", linea)
    total = sum(len(e.get("noticias", [])) for a in archivos for e in yaml.safe_load(a.read_text(encoding="utf-8")) or [])
    print(f"{total} noticias: {len(distintos)} distintas, {len(sin_respuesta)} sin og:title legible.")
    return 1 if distintos else 0


if __name__ == "__main__":
    rutas = [Path(a) for a in sys.argv[1:]] or [RAIZ / "data" / "eventos" / "ley.yaml"]
    sys.exit(main(rutas))
