"""Avisa por IndexNow (Bing, Yandex, Seznam, Naver) que la portada cambió, para que vuelvan a leerla.

Ejecutar después de publicar un cambio visible: .venv/bin/python scripts/avisar_buscadores.py
Google no usa IndexNow; ahí se pide desde Search Console («Inspección de URLs»).
"""

import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.main import INDEXNOW_CLAVE, SITIO  # noqa: E402

respuesta = httpx.post("https://api.indexnow.org/indexnow", json={
    "host": SITIO.removeprefix("https://"),
    "key": INDEXNOW_CLAVE,
    "keyLocation": f"{SITIO}/{INDEXNOW_CLAVE}.txt",
    "urlList": [f"{SITIO}/"],
})
print(respuesta.status_code, respuesta.text or "aviso recibido")
