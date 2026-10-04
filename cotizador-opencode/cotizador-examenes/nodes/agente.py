"""Nodo `agente` (ciclo ReAct) (`spec.md` §5.2, §5.7)."""

from __future__ import annotations

from langchain_core.messages import AIMessage

import services.llm
import tools
from prompts.agente_prompt import construir_mensajes


def nodo_agente(state: dict) -> dict:
    try:
        llm = services.llm.llm_agente().bind_tools(tools.construir_tools())
        respuesta = llm.invoke(construir_mensajes(state))
    except Exception as exc:  # LLM caído: consolidar lo que haya, sin romper el grafo
        respuesta = AIMessage(content=f"No pude seguir consultando centros ({exc}).")
    return {"messages": [respuesta]}
