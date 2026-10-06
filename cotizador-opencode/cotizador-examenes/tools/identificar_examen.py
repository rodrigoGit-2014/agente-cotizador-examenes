"""Herramienta `identificar_examen` (`spec.md` §5.6, RF-11)."""

from __future__ import annotations

from pydantic import BaseModel, Field

import services.llm
from prompts.identificacion_prompt import construir_mensajes
from schemas import Identificacion, SalidaIdentificacion

NOMBRE = "identificar_examen"
DESCRIPCION = (
    "Para un centro de la búsqueda actual, decide cuál de sus exámenes corresponde a la "
    "necesidad del usuario. Devuelve un veredicto: coincide, dudoso o no_coincide."
)


class Args(BaseModel):
    centro_id: str = Field(..., description="centro_id de un centro devuelto por buscar_centros.")
    necesidad: str = Field(..., description="La necesidad del usuario, en palabras simples.")


def validar(args: dict, state: dict) -> str | None:
    ids = {c.centro_id for c in state.get("centros", [])}
    if args.get("centro_id") not in ids:
        return "el centro no pertenece a la búsqueda actual"
    return None


def _normalizar(salida) -> SalidaIdentificacion:
    if isinstance(salida, SalidaIdentificacion):
        return salida
    return SalidaIdentificacion(**dict(salida))


def ejecutar(args: dict, state: dict) -> dict:
    from services import ingesta, redis_store

    centro_id = args["centro_id"]
    client = redis_store.cliente()
    examenes = ingesta.cargar_examenes(client, centro_id)

    if not examenes:
        ident = Identificacion(
            centro_id=centro_id,
            veredicto="sin_documento",
            justificacion="el centro no tiene documento cargado",
        )
    else:
        llm = services.llm.llm_estructurado(SalidaIdentificacion)
        salida = _normalizar(
            llm.invoke(construir_mensajes(args["necesidad"], [e.model_dump() for e in examenes]))
        )
        codigos = {e.codigo for e in examenes}
        if salida.veredicto == "coincide" and salida.codigo_examen not in codigos:
            salida.veredicto = "dudoso"
            salida.justificacion = (salida.justificacion + " (código inexistente)").strip()
        ident = Identificacion(centro_id=centro_id, **salida.model_dump())

    return {
        "estado": {"identificaciones": {centro_id: ident}},
        "observacion": ident.model_dump(),
        "alertas": [],
    }
