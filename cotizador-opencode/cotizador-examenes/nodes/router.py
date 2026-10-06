"""Nodo `router` (`spec.md` §5.2, §5.3).

Clasifica la ruta y extrae solo necesidad, ciudad, previsión y N, usando el historial visible.
El ruteo fino (por código) lo hace `main.py` sobre esta salida.
"""

from __future__ import annotations

import config
import services.llm
from prompts.router_prompt import construir_mensajes
from schemas import SalidaRouter, Solicitud
from services import privacidad


def _historial_visible(messages: list) -> list:
    """Mensajes del usuario y respuestas finales (sin las rondas de herramientas).

    Se excluyen los `ai` con `tool_calls`: son pasos intermedios del ReAct y, si se envían sin
    sus mensajes `tool`, el proveedor los rechaza. Así el router ve el historial que necesita.
    """
    visibles = [
        m for m in messages
        if getattr(m, "type", "") == "human"
        or (getattr(m, "type", "") == "ai" and not getattr(m, "tool_calls", None))
    ]
    return visibles or messages[-1:]


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
    except Exception as exc:  # sin credenciales o fallo del modelo -> ruta directa
        salida = SalidaRouter(
            ruta="respuesta_directa", motivo=f"fallo de clasificación: {exc}"
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
        "ruta": ruta,
        "solicitud": solicitud,
        "datos_personales_detectados": bool(salida.datos_personales)
        or _hay_datos_personales(state.get("messages", [])),
        # Reinicia el estado del turno (state.py: los demás campos se reinician entre turnos,
        # salvo `messages` y `prevision_preguntada`). Sin esto, un turno hereda centros,
        # identificaciones y cotizaciones del anterior.
        "centros": [],
        "identificaciones": {},
        "cotizaciones": {},
        "observaciones": [],
        "alertas": [],
        "rechazos": [],
        "iteraciones": 0,
        "motivo_parada": None,
        "reporte": None,
        "verificacion": None,
    }
