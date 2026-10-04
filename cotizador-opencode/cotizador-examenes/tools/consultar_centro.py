"""Herramienta `consultar_centro` (`spec.md` §5.6, §5.8)."""

from __future__ import annotations

from pydantic import BaseModel, Field

import config
from services import busqueda, redis_store, simulador

NOMBRE = "consultar_centro"
DESCRIPCION = (
    "Ejecuta la llamada simulada con un centro que ya fue identificado como 'coincide' y "
    "registra la cotización. Se pide de a un centro por vez."
)


class Args(BaseModel):
    centro_id: str = Field(..., description="Un centro de la búsqueda actual con examen 'coincide'.")
    codigo_examen: str = Field(..., description="El código del examen identificado como 'coincide'.")


def validar(args: dict, state: dict) -> str | None:
    centros = {c.centro_id: c for c in state.get("centros", [])}
    centro_id = args.get("centro_id")
    if centro_id not in centros:
        return "el centro no pertenece a la búsqueda actual"
    ident = state.get("identificaciones", {}).get(centro_id)
    if not ident or ident.veredicto != "coincide":
        return "el examen no fue identificado como 'coincide' en ese centro"
    if ident.codigo_examen != args.get("codigo_examen"):
        return "el código no coincide con el examen identificado en ese centro"
    if centro_id in state.get("cotizaciones", {}):
        return "el centro ya fue consultado en este turno"
    n = state["solicitud"].N if state.get("solicitud") else config.N_POR_DEFECTO
    comparables = sum(1 for c in state.get("cotizaciones", {}).values() if c.es_comparable())
    if comparables >= n:
        return f"ya hay {n} cotizaciones comparables"
    return None


def ejecutar(args: dict, state: dict) -> dict:
    centro = next(c for c in state["centros"] if c.centro_id == args["centro_id"])
    ident = state["identificaciones"][args["centro_id"]]
    escenario = busqueda.cargar_escenario(
        state.get("escenario_id") or config.ESCENARIO_POR_DEFECTO
    )
    prevision = state["solicitud"].prevision.value

    client = redis_store.cliente()
    fragmentos = redis_store.obtener_fragmentos(
        client, args["centro_id"], args["codigo_examen"]
    )

    cotizacion = simulador.ejecutar_llamada(
        centro=centro,
        codigo_examen=args["codigo_examen"],
        nombre_examen_centro=ident.nombre_examen_centro or args["codigo_examen"],
        prevision=prevision,
        escenario=escenario,
        fragmentos=fragmentos,
    )

    cotizaciones = dict(state.get("cotizaciones", {}))
    cotizaciones[args["centro_id"]] = cotizacion
    comparables = sum(1 for c in cotizaciones.values() if c.es_comparable())
    n = state["solicitud"].N
    pendientes = [
        c.centro_id
        for c in state.get("centros", [])
        if state.get("identificaciones", {}).get(c.centro_id)
        and state["identificaciones"][c.centro_id].veredicto == "coincide"
        and c.centro_id not in cotizaciones
    ]
    alertas = [
        "Instrucción incrustada detectada en un turno de la recepción"
        for t in cotizacion.transcripcion
        if t.hablante == "centro" and busqueda.contiene_instruccion(t.texto)
    ]
    return {
        "estado": {"cotizaciones": cotizaciones},
        "observacion": {
            "cotizacion": cotizacion.model_dump(),
            "progreso": {"comparables": comparables, "N": n, "pendientes": pendientes},
        },
        "alertas": alertas,
    }
