"""Nodo `herramientas` (`spec.md` §5.2, §5.6).

Valida argumentos en código antes de ejecutar (no depende del modelo), ejecuta y agrega
observaciones. Si una validación falla, no ejecuta y devuelve el rechazo como observación.
"""

from __future__ import annotations

import json

from langchain_core.messages import ToolMessage

import tools
from services import privacidad

_DICT_ACUMULABLES = ("identificaciones", "cotizaciones")


def _fusionar(destino: dict, nuevos: dict) -> None:
    for clave, valor in nuevos.items():
        if clave in _DICT_ACUMULABLES:
            acumulado = dict(destino.get(clave, {}))
            acumulado.update(valor)
            destino[clave] = acumulado
        else:
            destino[clave] = valor


def nodo_herramientas(state: dict) -> dict:
    ultimo = state["messages"][-1]
    llamadas = getattr(ultimo, "tool_calls", []) or []

    observaciones = list(state.get("observaciones", []))
    alertas = list(state.get("alertas", []))
    rechazos = list(state.get("rechazos", []))
    actualizaciones: dict = {}
    mensajes: list = []

    for llamada in llamadas:
        nombre = llamada.get("name", "")
        args = llamada.get("args", {}) or {}
        tool = tools.HERRAMIENTAS.get(nombre)

        culpables = privacidad.argumentos_con_dato_personal(args)
        if culpables:
            motivo = "argumento con dato personal: " + ", ".join(culpables)
        elif tool is None:
            motivo = f"herramienta desconocida: {nombre}"
        else:
            motivo = tool.validar(args, {**state, **actualizaciones})

        if motivo:
            rechazos.append({"herramienta": nombre, "argumentos": args, "motivo": motivo})
            texto = f"Rechazado por validación: {motivo}"
            observaciones.append(texto)
        else:
            try:
                resultado = tool.ejecutar(args, {**state, **actualizaciones})
            except Exception:  # Redis/LLM caídos, red, etc.: no tumbar el grafo
                motivo = f"no fue posible completar {nombre} en este momento"
                rechazos.append({"herramienta": nombre, "argumentos": args, "motivo": motivo})
                texto = f"Error de ejecución: {motivo}"
                observaciones.append(texto)
                mensajes.append(ToolMessage(content=texto, tool_call_id=llamada.get("id", "")))
                continue
            _fusionar(actualizaciones, resultado.get("estado", {}))
            alertas.extend(resultado.get("alertas", []))
            texto = json.dumps(resultado.get("observacion", {}), ensure_ascii=False)
            observaciones.append(texto)

        mensajes.append(ToolMessage(content=texto, tool_call_id=llamada.get("id", "")))

    return {
        "messages": mensajes,
        "observaciones": observaciones,
        "alertas": alertas,
        "rechazos": rechazos,
        "iteraciones": state.get("iteraciones", 0) + 1,
        **actualizaciones,
    }
