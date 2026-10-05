"""Nodo `herramientas` (`spec.md` §5.2, §5.6).

Valida argumentos en código antes de ejecutar (no depende del modelo), ejecuta y agrega
observaciones. Si una validación falla, no ejecuta y devuelve el rechazo como observación.

Cuando el agente pide en una misma ronda varias herramientas que no comparten estado (p. ej. las
identificaciones, que el prompt ya pide en paralelo), se ejecutan en paralelo. Los resultados se
fusionan en el orden en que el modelo pidió las llamadas, para que el reporte sea determinista.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor

from langchain_core.messages import ToolMessage

import tools
from services import privacidad

_DICT_ACUMULABLES = ("identificaciones", "cotizaciones")

# Herramientas que pueden correr en paralelo dentro de una misma ronda: cada llamada se refiere a
# un centro distinto y no depende del resultado de otra llamada de la ronda. `consultar_centro`
# queda fuera porque el contrato la pide de a un centro por vez (spec.md §2, implementator.md).
_PARALELIZABLES = frozenset({"identificar_examen", "consultar_documentos"})


def _fusionar(destino: dict, nuevos: dict) -> None:
    for clave, valor in nuevos.items():
        if clave in _DICT_ACUMULABLES:
            acumulado = dict(destino.get(clave, {}))
            acumulado.update(valor)
            destino[clave] = acumulado
        else:
            destino[clave] = valor


def _paralelizable(nombres: list[str]) -> bool:
    """True si todas las llamadas de la ronda son de herramientas independientes."""
    return len(nombres) > 1 and all(nombre in _PARALELIZABLES for nombre in nombres)


def _procesar(llamada: dict, estado: dict) -> dict:
    """Valida y ejecuta una llamada. No muta `estado`; devuelve el delta y su observación."""
    nombre = llamada.get("name", "")
    args = llamada.get("args", {}) or {}
    tool_call_id = llamada.get("id", "")
    tool = tools.HERRAMIENTAS.get(nombre)

    culpables = privacidad.argumentos_con_dato_personal(args)
    if culpables:
        motivo = "argumento con dato personal: " + ", ".join(culpables)
    elif tool is None:
        motivo = f"herramienta desconocida: {nombre}"
    else:
        motivo = tool.validar(args, estado)

    if motivo:
        rechazo = {"herramienta": nombre, "argumentos": args, "motivo": motivo}
        texto = f"Rechazado por validación: {motivo}"
        return {
            "mensaje": ToolMessage(content=texto, tool_call_id=tool_call_id),
            "estado": {}, "alertas": [], "observacion": texto, "rechazo": rechazo,
        }

    try:
        resultado = tool.ejecutar(args, estado)
    except Exception as exc:  # Redis/LLM caídos, red, etc.: no tumbar el grafo
        motivo = f"error al ejecutar {nombre}: {exc}"
        rechazo = {"herramienta": nombre, "argumentos": args, "motivo": motivo}
        texto = f"Error de ejecución: {motivo}"
        return {
            "mensaje": ToolMessage(content=texto, tool_call_id=tool_call_id),
            "estado": {}, "alertas": [], "observacion": texto, "rechazo": rechazo,
        }

    texto = json.dumps(resultado.get("observacion", {}), ensure_ascii=False)
    return {
        "mensaje": ToolMessage(content=texto, tool_call_id=tool_call_id),
        "estado": resultado.get("estado", {}),
        "alertas": list(resultado.get("alertas", [])),
        "observacion": texto,
        "rechazo": None,
    }


def nodo_herramientas(state: dict) -> dict:
    ultimo = state["messages"][-1]
    llamadas = getattr(ultimo, "tool_calls", []) or []

    observaciones = list(state.get("observaciones", []))
    alertas = list(state.get("alertas", []))
    rechazos = list(state.get("rechazos", []))
    actualizaciones: dict = {}

    nombres = [llamada.get("name", "") for llamada in llamadas]
    if _paralelizable(nombres):
        with ThreadPoolExecutor(max_workers=len(llamadas)) as pool:
            resultados = list(pool.map(lambda c: _procesar(c, state), llamadas))
    else:
        resultados = []
        acumulado: dict = {}
        for llamada in llamadas:
            resultado = _procesar(llamada, {**state, **acumulado})
            resultados.append(resultado)
            _fusionar(acumulado, resultado["estado"])

    mensajes: list = []
    for resultado in resultados:
        if resultado["rechazo"]:
            rechazos.append(resultado["rechazo"])
        observaciones.append(resultado["observacion"])
        alertas.extend(resultado["alertas"])
        _fusionar(actualizaciones, resultado["estado"])
        mensajes.append(resultado["mensaje"])

    return {
        "messages": mensajes,
        "observaciones": observaciones,
        "alertas": alertas,
        "rechazos": rechazos,
        "iteraciones": state.get("iteraciones", 0) + 1,
        **actualizaciones,
    }
