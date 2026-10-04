"""Construcción del LLM de Google Gemini desde `config.py`.

Ningún otro módulo lee la credencial: aquí se toma de `config.GOOGLE_API_KEY`.
"""

from __future__ import annotations

from typing import Type, TypeVar

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

import config

EsquemaT = TypeVar("EsquemaT", bound=BaseModel)


def _verificar_credencial() -> None:
    if not config.GOOGLE_API_KEY:
        raise RuntimeError(
            "Falta GOOGLE_API_KEY en el .env. Copie .env.example a .env y complete sus credenciales."
        )


def construir_llm(
    temperatura: float | None = None,
    modelo: str | None = None,
) -> ChatGoogleGenerativeAI:
    """Devuelve un cliente `ChatGoogleGenerativeAI` con temperatura baja."""
    _verificar_credencial()
    return ChatGoogleGenerativeAI(
        model=modelo or config.MODELO_LLM,
        temperature=config.TEMPERATURA_AGENTE if temperatura is None else temperatura,
        google_api_key=config.GOOGLE_API_KEY,
    )


def llm_agente() -> ChatGoogleGenerativeAI:
    return construir_llm(temperatura=config.TEMPERATURA_AGENTE)


def llm_recepcionista() -> ChatGoogleGenerativeAI:
    return construir_llm(temperatura=config.TEMPERATURA_RECEPCIONISTA)


def llm_estructurado(esquema: Type[EsquemaT], temperatura: float | None = None):
    """Devuelve el LLM con salida estructurada sobre `esquema` (Pydantic)."""
    return construir_llm(temperatura=temperatura).with_structured_output(esquema)
