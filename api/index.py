"""Punto de entrada para Vercel (ADR 0036): la misma aplicación de app/main.py, como función de Python.

Vercel la vuelve a publicar con cada commit en main, así que lo que carga el vigía aparece en la página sin pasos manuales.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402,F401
