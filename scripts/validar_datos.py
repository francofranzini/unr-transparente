"""Valida data/: toda fila debe tener ficha completa (principio 1). Sale con código 1 si hay errores."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.carga import ErrorDeCarga, cargar  # noqa: E402

try:
    repo = cargar()
except ErrorDeCarga as e:
    print(e, file=sys.stderr)
    sys.exit(1)
print(f"OK: {len(repo.datos)} datos y {len(repo.eventos)} eventos con ficha completa.")
