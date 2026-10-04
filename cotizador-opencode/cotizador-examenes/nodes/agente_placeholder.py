"""Nodo temporal `agente_placeholder` (se retira en el paso `05-react-herramientas`).

Deja el grafo ejecutable de punta a punta mientras el ciclo ReAct no existe: registra una
observación y sigue a consolidación.
"""

from __future__ import annotations

AVISO = (
    "La cotización con centros todavía no está implementada en esta versión; "
    "el flujo llegó hasta este punto sin errores."
)


def nodo_agente_placeholder(state: dict) -> dict:
    return {
        "observaciones": [*state.get("observaciones", []), AVISO],
        "iteraciones": state.get("iteraciones", 0) + 1,
        "motivo_parada": "agente_no_implementado",
    }
