"""Nodo `respuesta_directa` (`spec.md` §5.2).

Responde saludos, límites y pedidos de datos faltantes. Es el único nodo, junto con la cadena
de consolidación, que redacta la respuesta final. Va directo a END.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage

import services.llm
from prompts.respuesta_directa_prompt import construir_mensajes
from schemas import Solicitud


def _historial_visible(messages: list) -> list:
    visibles = [m for m in messages if getattr(m, "type", "") in ("human", "ai")]
    return visibles or messages[-1:]


def _determinar_motivo(state: dict) -> str:
    ruta = state.get("ruta")
    if ruta == "fuera_de_alcance":
        return "fuera_de_alcance"
    if ruta == "respuesta_directa":
        return "respuesta_directa"
    # cotizar o info_publicada con datos faltantes
    sol: Solicitud | None = state.get("solicitud")
    faltantes = []
    if not sol or not sol.necesidad or sol.necesidad_ambigua:
        faltantes.append("necesidad")
    if not sol or not sol.ciudad:
        faltantes.append("ciudad")
    return "falta_informacion" if faltantes else "respuesta_directa"


def _caso(state: dict) -> str:
    ruta = state.get("ruta")
    sol: Solicitud | None = state.get("solicitud")
    if ruta == "fuera_de_alcance":
        return "fuera_de_alcance o límite: nombra el límite y ofrece lo que sí puedes hacer."
    if ruta == "respuesta_directa":
        return "saludo, agradecimiento o pregunta sobre lo que puedes hacer."
    faltantes = []
    if not sol or not sol.necesidad or sol.necesidad_ambigua:
        faltantes.append("la necesidad (qué examen y para qué)")
    if not sol or not sol.ciudad:
        faltantes.append("la ciudad")
    return "faltan datos para cotizar: pide " + " y ".join(faltantes) + "."


def _a_ai(mensaje) -> AIMessage:
    if isinstance(mensaje, AIMessage):
        return mensaje
    contenido = getattr(mensaje, "content", mensaje)
    return AIMessage(content=contenido if isinstance(contenido, str) else str(contenido))


def nodo_respuesta_directa(state: dict) -> dict:
    mensajes = construir_mensajes(_historial_visible(state.get("messages", [])), _caso(state))
    llm = services.llm.llm_agente()
    respuesta = _a_ai(llm.invoke(mensajes))
    return {"messages": [respuesta], "motivo_parada": _determinar_motivo(state)}
