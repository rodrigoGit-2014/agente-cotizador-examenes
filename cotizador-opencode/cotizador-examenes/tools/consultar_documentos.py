"""Herramienta `consultar_documentos` (RAG) (`spec.md` §5.6, RF-28/29, [P-04])."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from services import busqueda, embeddings, redis_store

NOMBRE = "consultar_documentos"
DESCRIPCION = (
    "Recupera fragmentos de los documentos publicados de un centro para responder preguntas "
    "de preparación, requisitos o días de atención. No entrega precios."
)

PRECIO_RE = re.compile(r"\$ ?\d[\d.]*")


class Args(BaseModel):
    centro_id: str = Field(..., description="Un centro de la búsqueda actual.")
    consulta: str = Field(..., description="La pregunta del usuario, en palabras simples.")
    codigo_examen: str | None = Field(None, description="Opcional: código del examen.")


def validar(args: dict, state: dict) -> str | None:
    ids = {c.centro_id for c in state.get("centros", [])}
    if args.get("centro_id") not in ids:
        return "el centro no pertenece a la búsqueda actual"
    return None


def quitar_precios(texto: str) -> str:
    """[P-04] El precio vigente se obtiene de la llamada, no de los documentos."""
    return PRECIO_RE.sub("(precio no se informa por este canal)", texto)


def ejecutar(args: dict, state: dict) -> dict:
    client = redis_store.cliente()
    vector = embeddings.embeber_consulta(args["consulta"])
    encontrados = redis_store.buscar_fragmentos(
        client, vector, args["centro_id"], args.get("codigo_examen")
    )
    alertas: list[str] = []
    fragmentos = []
    for f in encontrados:
        texto = f["texto"]
        if busqueda.contiene_instruccion(texto):
            alertas.append("Instrucción incrustada detectada en un fragmento de documento")
            texto = busqueda.limpiar_instruccion(texto)
        fragmentos.append({**f, "texto": quitar_precios(texto)})

    centro = next(c for c in state["centros"] if c.centro_id == args["centro_id"])
    return {
        "estado": {},
        "observacion": {"centro": centro.nombre, "fragmentos": fragmentos},
        "alertas": alertas,
    }
