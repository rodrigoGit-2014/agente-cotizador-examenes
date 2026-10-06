"""Captura y versiona un web snapshot de búsqueda de centros (`spec.md` §5.5, §5.6).

El web snapshot es el modo por defecto de `buscar_centros`: un archivo versionado con los
resultados de una búsqueda web, para repetir una prueba aunque la web cambie (RF-09).

Modos:
- `--desde-json <archivo>`: normaliza un volcado crudo de resultados (lo que devolvió el
  proveedor) y escribe el web snapshot versionado.
- `--en-vivo`: consulta el proveedor configurado. Si no hay proveedor (DA-02 pendiente),
  informa y termina con código 2, sin inventar endpoints ni credenciales.

Uso:
    python scripts/capturar_web_snapshot.py --desde-json crudo.json \
        --id talca-oftalmologia --especialidad Oftalmología --ciudad Talca \
        --consulta "oftalmología Talca"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import config  # noqa: E402


def normalizar_telefono(telefono: str) -> str:
    """Teléfono -> centro_id (solo dígitos, con código de país)."""
    return re.sub(r"\D", "", telefono or "")


def normalizar(
    *,
    id: str,
    especialidad: str,
    ciudad: str,
    consulta: str,
    resultados_crudos: list[dict],
    fecha_captura: str,
) -> dict:
    return {
        "id": id,
        "especialidad": especialidad,
        "ciudad": ciudad,
        "fecha_captura": fecha_captura,
        "consulta_usada": consulta,
        "resultados": [
            {
                "nombre": r.get("nombre", ""),
                "direccion": r.get("direccion"),
                "telefono": r.get("telefono"),
                "fragmento_web": r.get("fragmento_web"),
            }
            for r in resultados_crudos
        ],
    }


def _leer_crudos(ruta: Path) -> list[dict]:
    data = json.loads(ruta.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("resultados", [])
    if not isinstance(data, list):
        raise ValueError("El volcado crudo debe ser una lista de resultados o un objeto con 'resultados'.")
    return data


def capturar_en_vivo(consulta: str) -> list[dict]:
    """Consulta el proveedor de búsqueda web. Proveedor pendiente (DA-02)."""
    if not config.BUSQUEDA_API_KEY:
        print(
            "Modo en vivo no disponible: no hay BUSQUEDA_API_KEY configurada (DA-02 pendiente). "
            "Use --desde-json para versionar una captura, o configure el proveedor.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    # El proveedor concreto (endpoint y formato) está por decidir (DA-02). No se inventa aquí.
    raise NotImplementedError(
        "Proveedor de búsqueda en vivo pendiente (DA-02). Configure el endpoint y el parseo."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Versiona un web snapshot de búsqueda de centros.")
    parser.add_argument("--desde-json", type=Path, help="Volcado crudo de resultados a normalizar.")
    parser.add_argument("--en-vivo", action="store_true", help="Consultar el proveedor (DA-02).")
    parser.add_argument("--id", required=True, help="Identificador del web snapshot, p. ej. talca-oftalmologia.")
    parser.add_argument("--especialidad", required=True)
    parser.add_argument("--ciudad", required=True)
    parser.add_argument("--consulta", default="")
    parser.add_argument("--fecha", default=date.today().isoformat())
    parser.add_argument("--salida", type=Path, default=None)
    args = parser.parse_args()

    if args.en_vivo:
        crudos = capturar_en_vivo(args.consulta)
    elif args.desde_json:
        crudos = _leer_crudos(args.desde_json)
    else:
        parser.error("Indique --desde-json <archivo> o --en-vivo.")

    web_snapshot = normalizar(
        id=args.id,
        especialidad=args.especialidad,
        ciudad=args.ciudad,
        consulta=args.consulta,
        resultados_crudos=crudos,
        fecha_captura=args.fecha,
    )
    salida = args.salida or (config.WEB_SNAPSHOTS_DIR / f"{args.id}.json")
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(web_snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Web snapshot escrita en {salida} ({len(web_snapshot['resultados'])} resultados).")


if __name__ == "__main__":
    main()
