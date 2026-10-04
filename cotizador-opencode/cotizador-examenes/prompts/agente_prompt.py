"""Prompt del nodo `agente` (ciclo ReAct) (`spec.md` §5.7, §5.10)."""

from __future__ import annotations

from prompts.seguridad import BLOQUE_AGENTE, BLOQUE_UNIVERSAL

BASE = f"""\
Eres un asistente que cotiza exámenes médicos en Chile y opera en un ciclo de herramientas.

{BLOQUE_UNIVERSAL}

{BLOQUE_AGENTE}

Cómo operar:
- Para cotizar: primero busca centros, luego identifica en cada uno el examen que corresponde,
  y finalmente consulta uno por uno solo los centros cuyo examen fue identificado como
  "coincide". Pide las identificaciones en paralelo cuando puedas.
- Para preguntas de información publicada: busca el centro y consulta sus documentos; no llames
  por teléfono.
- Deja de pedir herramientas cuando: ya tienes N cotizaciones comparables, o no quedan centros
  "coincide" por consultar, o no hay centros aplicables.
- Cuando termines, responde sin pedir más herramientas."""


def construir_system(state: dict) -> str:
    from schemas import Solicitud

    solicitud: Solicitud | None = state.get("solicitud")
    identificaciones = state.get("identificaciones", {})
    cotizaciones = state.get("cotizaciones", {})
    comparables = sum(1 for c in cotizaciones.values() if c.es_comparable())

    lineas = [
        f"Ruta: {state.get('ruta')}",
        f"Iteraciones usadas: {state.get('iteraciones', 0)}",
    ]
    if solicitud:
        lineas += [
            f"Necesidad: {solicitud.necesidad}",
            f"Ciudad: {solicitud.ciudad}",
            f"Previsión: {solicitud.prevision.value}",
            f"N: {solicitud.N}",
        ]
    if state.get("centros"):
        lineas.append("Centros encontrados: " + ", ".join(c.centro_id for c in state["centros"]))
    if identificaciones:
        lineas.append(
            "Identificaciones: "
            + "; ".join(f"{cid}={i.veredicto}" for cid, i in identificaciones.items())
        )
    lineas.append(f"Cotizaciones comparables: {comparables} de {solicitud.N if solicitud else '?'}")

    return BASE + "\n\n--- ESTADO ACTUAL ---\n" + "\n".join(lineas)


def construir_mensajes(state: dict) -> list:
    from langchain_core.messages import SystemMessage

    return [SystemMessage(content=construir_system(state)), *state.get("messages", [])]
