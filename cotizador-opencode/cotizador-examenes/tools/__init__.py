"""Registro de herramientas del agente (`spec.md` §5.6).

El LLM ve SOLO estos cuatro esquemas. Cualquier otro nombre se rechaza en código.
"""

from __future__ import annotations

from tools import buscar_centros, consultar_centro, consultar_documentos, identificar_examen

MODULOS = (buscar_centros, identificar_examen, consultar_centro, consultar_documentos)
HERRAMIENTAS = {m.NOMBRE: m for m in MODULOS}
NOMBRES = tuple(HERRAMIENTAS)


def construir_tools():
    """Herramientas para `llm.bind_tools(...)`. La ejecución la hace el nodo `herramientas`."""
    from langchain_core.tools import StructuredTool

    return [
        StructuredTool.from_function(
            func=lambda **_: "ejecutado por el nodo",
            name=m.NOMBRE,
            description=m.DESCRIPCION,
            args_schema=m.Args,
        )
        for m in MODULOS
    ]
