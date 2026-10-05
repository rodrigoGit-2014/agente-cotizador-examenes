"""Nodo `router` (`spec.md` §5.2, §5.3).

Clasifica la ruta y extrae solo necesidad, ciudad, previsión y N, usando el historial visible.
El ruteo fino (por código) lo hace `main.py` sobre esta salida.
"""

from __future__ import annotations

import config
from langchain_core.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
import services.llm
from prompts.router_prompt import construir_mensajes
from schemas import SalidaRouter, Solicitud
from services import privacidad
from services.historial import historial_visible

TIPOS_VISIBLES = ("human", "ai")


def _historial_visible(messages: list) -> list:
    """Solo los mensajes del usuario y las respuestas finales."""
    return historial_visible(messages)


def _hay_datos_personales(messages: list) -> bool:
    for m in messages:
        if getattr(m, "type", "") == "human" and privacidad.contiene_rut(getattr(m, "content", "")):
            return True
    return False


def _normalizar_salida(salida) -> SalidaRouter:
    if isinstance(salida, SalidaRouter):
        return salida
    return SalidaRouter(**dict(salida))


def nodo_router(state: dict) -> dict:
    entrada = construir_mensajes(_historial_visible(state.get("messages", [])))
    try:
        llm = services.llm.llm_estructurado(SalidaRouter)
        salida = _normalizar_salida(llm.invoke(entrada))
    except Exception:  # sin credenciales o fallo del modelo -> ruta directa
        salida = SalidaRouter(
            ruta="respuesta_directa", motivo="No se pudo interpretar la consulta."
        )

    ruta = salida.ruta or "respuesta_directa"
    n_indicado = salida.N if (salida.N is not None and salida.N >= 1) else None
    solicitud = Solicitud(
        necesidad=salida.necesidad,
        necesidad_ambigua=salida.necesidad_ambigua,
        especialidad=salida.especialidad,
        ciudad=salida.ciudad,
        prevision=salida.prevision,
        N=n_indicado or config.N_POR_DEFECTO,
        N_por_defecto=n_indicado is None,
    )

    return {
        "messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *_historial_visible(state.get("messages", []))],
        "centros": [],
        "identificaciones": {},
        "cotizaciones": {},
        "observaciones": [],
        "alertas": [],
        "rechazos": [],
        "iteraciones": 0,
        "motivo_parada": "",
        "reporte": None,
        "verificacion": {},
        "ruta": ruta,
        "solicitud": solicitud,
        "datos_personales_detectados": bool(salida.datos_personales)
        or _hay_datos_personales(state.get("messages", [])),
    }
