"""Herramienta `buscar_centros` (`spec.md` §5.6)."""

from __future__ import annotations

from pydantic import BaseModel, Field

import config
from services import busqueda, ciudades

NOMBRE = "buscar_centros"
DESCRIPCION = (
    "Busca centros de una especialidad en una ciudad de Chile y devuelve su nombre, "
    "dirección y teléfono públicos."
)


class Args(BaseModel):
    especialidad: str = Field(..., description="Especialidad médica, por ejemplo 'oftalmología'.")
    ciudad: str = Field(..., description="Ciudad de Chile, por ejemplo 'Talca'.")


def validar(args: dict, state: dict) -> str | None:
    if not args.get("especialidad"):
        return "falta la especialidad"
    if not args.get("ciudad"):
        return "falta la ciudad"
    if not ciudades.es_ciudad_chile(args["ciudad"]):
        return f"la ciudad '{args['ciudad']}' no es de Chile"
    return None


def ejecutar(args: dict, state: dict) -> dict:
    escenario = busqueda.cargar_escenario(
        state.get("escenario_id") or config.ESCENARIO_POR_DEFECTO
    )
    centros, alertas = busqueda.buscar(args["especialidad"], args["ciudad"], escenario)
    return {
        "estado": {"centros": centros},
        "observacion": {"centros": [c.model_dump() for c in centros]},
        "alertas": alertas,
    }
