"""Construcción del LLM de OpenAI desde `config.py`.

Ningún otro módulo lee la credencial: aquí se toma de `config.OPENAI_API_KEY`.
"""

from __future__ import annotations

from typing import Type, TypeVar

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

import config

EsquemaT = TypeVar("EsquemaT", bound=BaseModel)


def _verificar_credencial() -> None:
    if not config.OPENAI_API_KEY:
        raise RuntimeError(
            "Falta OPENAI_API_KEY en el .env. Complete su clave de la API de OpenAI."
        )


def construir_llm(
    temperatura: float | None = None,
    modelo: str | None = None,
) -> ChatOpenAI:
    """Devuelve un cliente `ChatOpenAI` con temperatura baja."""
    _verificar_credencial()
    return ChatOpenAI(
        model=modelo or config.MODELO_LLM,
        temperature=config.TEMPERATURA_AGENTE if temperatura is None else temperatura,
        api_key=config.OPENAI_API_KEY,
        timeout=30,
        max_retries=1,
    )


def llm_agente() -> ChatGoogleGenerativeAI:
    return construir_llm(temperatura=config.TEMPERATURA_AGENTE)


def llm_recepcionista() -> ChatGoogleGenerativeAI:
    return construir_llm(temperatura=config.TEMPERATURA_RECEPCIONISTA)


def llm_estructurado(esquema: Type[EsquemaT], temperatura: float | None = None):
    """Devuelve el LLM con salida estructurada sobre `esquema` (Pydantic)."""
    return construir_llm(temperatura=temperatura).with_structured_output(
        esquema, method="function_calling", strict=False
    )
