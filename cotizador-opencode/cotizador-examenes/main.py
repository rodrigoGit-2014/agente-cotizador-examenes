"""Grafo del cotizador de exámenes médicos (`spec.md` §2, §5.1).

Construye el StateGraph desde START hasta END y expone el grafo compilado como símbolo
importable (`app` y `build_graph()`). No contiene lógica de negocio. El bucle de consola vive
dentro de `if __name__ == "__main__":`.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

import config
import schemas
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from nodes.agente import nodo_agente
from nodes.consolidar import nodo_consolidar
from nodes.herramientas import nodo_herramientas
from nodes.responder import nodo_responder
from nodes.respuesta_directa import nodo_respuesta_directa
from nodes.router import nodo_router
from nodes.verificador import nodo_verificador
from schemas import Prevision
from state import Estado

# Número de rondas de herramientas permitidas (spec.md §5.10). El agente puede pedir varias
# herramientas por ronda; el tope acota el ciclo.
MAX_RONDAS_HERRAMIENTAS = config.MAX_ITERACIONES

# Tipos del dominio registrados en el serializador del checkpointer. Sin esto, al deserializar
# el estado LangGraph avisa "Deserializing unregistered type schemas.X" y en el futuro lo bloqueará.
_TIPOS_DOMINIO = [
    obj
    for obj in vars(schemas).values()
    if isinstance(obj, type) and getattr(obj, "__module__", "") == "schemas"
]
_SERDE = JsonPlusSerializer(allowed_msgpack_modules=_TIPOS_DOMINIO)


def ruta_condicional(state: Estado) -> str:
    """Ruteo por código sobre la salida del router (`spec.md` §5.3)."""
    ruta = state.get("ruta")
    solicitud = state.get("solicitud")

    if ruta in ("respuesta_directa", "fuera_de_alcance"):
        return "respuesta_directa"

    if ruta in ("cotizar", "info_publicada"):
        falta_datos = (
            solicitud is None
            or not solicitud.necesidad
            or solicitud.necesidad_ambigua
            or not solicitud.ciudad
        )
        if falta_datos:
            return "respuesta_directa"

    if (
        ruta == "cotizar"
        and solicitud is not None
        and solicitud.prevision == Prevision.no_indicada
        and not state.get("prevision_preguntada")
    ):
        return "respuesta_directa"  # pregunta la previsión una sola vez (RF-05)

    return "agente"


def despues_agente(state: Estado) -> str:
    """El agente sigue al ciclo de herramientas o consolida (spec.md §5.10)."""
    ultimo = state["messages"][-1]
    tiene_herramientas = bool(getattr(ultimo, "tool_calls", None))
    if tiene_herramientas and state.get("iteraciones", 0) < MAX_RONDAS_HERRAMIENTAS:
        return "herramientas"
    return "consolidar"


def build_graph():
    grafo = StateGraph(Estado)

    grafo.add_node("router", nodo_router)
    grafo.add_node("respuesta_directa", nodo_respuesta_directa)
    grafo.add_node("agente", nodo_agente)
    grafo.add_node("herramientas", nodo_herramientas)
    grafo.add_node("consolidar", nodo_consolidar)
    grafo.add_node("responder", nodo_responder)
    grafo.add_node("verificador", nodo_verificador)

    grafo.add_edge(START, "router")
    grafo.add_conditional_edges(
        "router",
        ruta_condicional,
        {"respuesta_directa": "respuesta_directa", "agente": "agente"},
    )
    grafo.add_conditional_edges(
        "agente",
        despues_agente,
        {"herramientas": "herramientas", "consolidar": "consolidar"},
    )
    grafo.add_edge("herramientas", "agente")
    grafo.add_edge("respuesta_directa", END)
    grafo.add_edge("consolidar", "responder")
    grafo.add_edge("responder", "verificador")
    grafo.add_edge("verificador", END)

    return grafo.compile(checkpointer=MemorySaver(serde=_SERDE))


app = build_graph()


def _texto(mensaje) -> str:
    contenido = getattr(mensaje, "content", mensaje)
    return contenido if isinstance(contenido, str) else str(contenido)


def _bucle_consola() -> None:
    from services import privacidad

    print("Cotizador de exámenes médicos (escriba 'salir' para terminar).")
    runtime = {"configurable": {"thread_id": "consola"}}
    while True:
        try:
            texto = input("usted> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if texto.lower() in {"salir", "exit", "quit"}:
            break
        if not texto:
            continue
        entrada = privacidad.preparar_entrada(texto)
        estado = app.invoke(
            {"messages": [entrada], "escenario_id": config.ESCENARIO_POR_DEFECTO},
            runtime,
        )
        print("agente>", _texto(estado["messages"][-1]))


if __name__ == "__main__":
    _bucle_consola()
