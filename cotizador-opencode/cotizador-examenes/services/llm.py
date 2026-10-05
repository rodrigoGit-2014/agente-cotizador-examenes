"""Construcción del LLM (OpenAI u OpenCode Zen) desde `config.py`.

Ningún otro módulo lee las credenciales: aquí se toman de `config.OPENAI_API_KEY` u
`config.OPENCODE_API_KEY` según el proveedor de `config.LLM_MODELO_AGENTE`.
Ambos proveedores se usan con `ChatOpenAI`: OpenCode Zen expone una API compatible con OpenAI.
"""

from __future__ import annotations

from typing import Type, TypeVar

import httpx
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

import config

EsquemaT = TypeVar("EsquemaT", bound=BaseModel)

# Conexión HTTP compartida: sin esto, cada llamada al LLM crea su propio cliente y repite el
# saludo TLS. El turno hace decenas de llamadas, así que reutilizar el pool ahorra ese costo.
# `httpx.Client` es seguro entre hilos y la usan también las herramientas en paralelo.
_CLIENTE_HTTP = httpx.Client(
    timeout=config.LLM_TIMEOUT_S,
    follow_redirects=True,
    limits=httpx.Limits(max_connections=16, max_keepalive_connections=16),
)


def _credenciales() -> dict[str, str]:
    """Devuelve `api_key` (y `base_url` si aplica) del proveedor configurado."""
    if config.PROVEEDOR_LLM not in config.PROVEEDORES_LLM or not config.MODELO_LLM:
        raise RuntimeError(
            "LLM_MODELO_AGENTE del .env debe tener el formato 'openai:<modelo>' u 'opencode:<modelo>'."
        )
    if config.PROVEEDOR_LLM == "openai":
        if not config.OPENAI_API_KEY:
            raise RuntimeError("Falta OPENAI_API_KEY en el .env.")
        return {"api_key": config.OPENAI_API_KEY}
    if not config.OPENCODE_API_KEY:
        raise RuntimeError("Falta OPENCODE_API_KEY en el .env.")
    return {"api_key": config.OPENCODE_API_KEY, "base_url": config.OPENCODE_BASE_URL}


def construir_llm(
    temperatura: float | None = None,
    modelo: str | None = None,
) -> ChatOpenAI:
    """Devuelve un cliente `ChatOpenAI` con temperatura baja."""
    return ChatOpenAI(
        model=modelo or config.MODELO_LLM,
        temperature=config.TEMPERATURA_AGENTE if temperatura is None else temperatura,
        timeout=config.LLM_TIMEOUT_S,
        max_retries=config.LLM_MAX_REINTENTOS,
        http_client=_CLIENTE_HTTP,
        **_credenciales(),
    )


def llm_agente() -> ChatOpenAI:
    return construir_llm(temperatura=config.TEMPERATURA_AGENTE)


def llm_recepcionista() -> ChatOpenAI:
    return construir_llm(temperatura=config.TEMPERATURA_RECEPCIONISTA)


def llm_estructurado(esquema: Type[EsquemaT], temperatura: float | None = None):
    """Devuelve el LLM con salida estructurada sobre `esquema` (Pydantic).

    Usa `function_calling` porque es el método que soportan tanto OpenAI como los modelos de OpenCode.
    """
    return construir_llm(temperatura=temperatura).with_structured_output(esquema, method="function_calling")
