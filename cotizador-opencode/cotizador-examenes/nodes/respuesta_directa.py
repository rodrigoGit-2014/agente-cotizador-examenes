"""Nodo `respuesta_directa` (`spec.md` §5.2).

Responde saludos, límites y pedidos de datos faltantes. Es el único nodo, junto con la cadena
de consolidación, que redacta la respuesta final. Va directo a END.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage

import services.llm
from prompts.respuesta_directa_prompt import construir_mensajes
from schemas import Prevision, Solicitud
from services import sintomas


def _historial_visible(messages: list) -> list:
    """Mensajes del usuario y respuestas finales (sin las rondas de herramientas)."""
    visibles = [
        m for m in messages
        if getattr(m, "type", "") == "human"
        or (getattr(m, "type", "") == "ai" and not getattr(m, "tool_calls", None))
    ]
    return visibles or messages[-1:]


def _ultimo_usuario(messages: list) -> str:
    for m in reversed(messages):
        if getattr(m, "type", "") == "human":
            contenido = getattr(m, "content", "")
            return contenido if isinstance(contenido, str) else str(contenido)
    return ""


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


def _pidiendo_prevision(state: dict) -> bool:
    sol: Solicitud | None = state.get("solicitud")
    return (
        state.get("ruta") == "cotizar"
        and sol is not None
        and sol.prevision == Prevision.no_indicada
        and not state.get("prevision_preguntada")
    )


def _caso(state: dict) -> str:
    if sintomas.detectar(_ultimo_usuario(state.get("messages", []))):
        return (
            "síntoma agudo: entrega el mensaje fijo de derivación a urgencias "
            f'("{sintomas.MENSAJE_URGENCIAS}") y ofrece seguir con la cotización.'
        )
    if _pidiendo_prevision(state):
        return (
            "pide la previsión una sola vez (Fonasa, Isapre o particular); deja claro que si "
            "no la sabe se puede continuar igual."
        )
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

    if sintomas.detectar(_ultimo_usuario(state.get("messages", []))):
        texto = respuesta.content if isinstance(respuesta.content, str) else str(respuesta.content)
        if sintomas.MENSAJE_URGENCIAS not in texto:
            respuesta = AIMessage(content=f"{sintomas.MENSAJE_URGENCIAS} {texto}")

    salida: dict = {"messages": [respuesta], "motivo_parada": _determinar_motivo(state)}
    if _pidiendo_prevision(state):
        salida["prevision_preguntada"] = True
    return salida
