"""Historial visible y memoria con los tipos del dominio registrados."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

import schemas


def historial_visible(messages: list) -> list:
    return [
        m for m in messages
        if getattr(m, "type", "") == "human"
        or (getattr(m, "type", "") == "ai" and not getattr(m, "tool_calls", None))
    ]


def crear_memoria():
    tipos = [
        valor for valor in vars(schemas).values()
        if isinstance(valor, type) and valor.__module__ == schemas.__name__
    ]
    return MemorySaver(serde=JsonPlusSerializer(allowed_msgpack_modules=tipos))
