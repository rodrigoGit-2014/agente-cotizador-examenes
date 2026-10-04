"""Grafo del cotizador de exámenes médicos (`spec.md` §2, §5.1).

Construye el StateGraph desde START hasta END y expone el grafo compilado como símbolo
importable (`app` y `build_graph()`). No contiene lógica de negocio. El bucle de consola vive
dentro de `if __name__ == "__main__":`.

Etapa actual (paso `03-grafo-minimo`): router + respuesta_directa + agente_placeholder +
consolidar + responder + verificador. Las herramientas y el ciclo ReAct llegan en el paso `05`.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from nodes.agente_placeholder import nodo_agente_placeholder
from nodes.consolidar import nodo_consolidar
from nodes.responder import nodo_responder
from nodes.respuesta_directa import nodo_respuesta_directa
from nodes.router import nodo_router
from nodes.verificador import nodo_verificador
from state import Estado


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

    # En el paso 05 este destino pasa a ser el nodo `agente` (ciclo ReAct).
    return "agente_placeholder"


def build_graph():
    grafo = StateGraph(Estado)

    grafo.add_node("router", nodo_router)
    grafo.add_node("respuesta_directa", nodo_respuesta_directa)
    grafo.add_node("agente_placeholder", nodo_agente_placeholder)
    grafo.add_node("consolidar", nodo_consolidar)
    grafo.add_node("responder", nodo_responder)
    grafo.add_node("verificador", nodo_verificador)

    grafo.add_edge(START, "router")
    grafo.add_conditional_edges(
        "router",
        ruta_condicional,
        {
            "respuesta_directa": "respuesta_directa",
            "agente_placeholder": "agente_placeholder",
        },
    )

    grafo.add_edge("respuesta_directa", END)
    grafo.add_edge("agente_placeholder", "consolidar")
    grafo.add_edge("consolidar", "responder")
    grafo.add_edge("responder", "verificador")
    grafo.add_edge("verificador", END)

    return grafo.compile()


app = build_graph()


def _texto(mensaje) -> str:
    contenido = getattr(mensaje, "content", mensaje)
    return contenido if isinstance(contenido, str) else str(contenido)


def _bucle_consola() -> None:
    from langchain_core.messages import HumanMessage

    print("Cotizador de exámenes médicos (escriba 'salir' para terminar).")
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
        estado = app.invoke({"messages": [HumanMessage(content=texto)]})
        print("agente>", _texto(estado["messages"][-1]))


if __name__ == "__main__":
    _bucle_consola()
