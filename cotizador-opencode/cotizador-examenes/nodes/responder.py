"""Nodo `responder` (`spec.md` §5.2, [P-11]).

Redacta la respuesta al usuario a partir del reporte armado en código.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage

import config
import services.llm
from prompts.responder_prompt import construir_mensajes
from schemas import Reporte, Solicitud


def _a_ai(mensaje) -> AIMessage:
    if isinstance(mensaje, AIMessage):
        return mensaje
    contenido = getattr(mensaje, "content", mensaje)
    return AIMessage(content=contenido if isinstance(contenido, str) else str(contenido))


def nodo_responder(state: dict) -> dict:
    reporte: Reporte = state.get("reporte") or Reporte(N=config.N_POR_DEFECTO)
    solicitud: Solicitud = state.get("solicitud") or Solicitud()
    mensajes = construir_mensajes(reporte.model_dump_json(), solicitud.model_dump_json())
    try:
        llm = services.llm.llm_agente()
        respuesta = _a_ai(llm.invoke(mensajes))
    except Exception as exc:  # LLM caído: respuesta de respaldo, sin traceback al usuario
        respuesta = AIMessage(
            content="No pude redactar la respuesta en este momento. Intente nuevamente en unos instantes."
        )
    return {"messages": [respuesta]}
