"""Ingesta de documentos de centro en el Redis del curso.

Uso (con el intérprete del .venv, desde la raíz del proyecto):
    python scripts/ingesta.py [--forzar]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from services import ingesta  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga los documentos de centro en Redis.")
    parser.add_argument("--forzar", action="store_true", help="Recarga aunque ya esté cargado.")
    args = parser.parse_args()

    examenes, fragmentos = ingesta.analizar_carpeta()
    print(f"Documentos analizados: {len(fragmentos)} fragmentos, {len(examenes)} exámenes.")
    for e in examenes:
        print(f"  - {e.centro_id} · {e.codigo} · {e.nombre}")

    resultado = ingesta.ingestar(forzar=args.forzar)
    print("Ingesta:", resultado)


if __name__ == "__main__":
    main()
