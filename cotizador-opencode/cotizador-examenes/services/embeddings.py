"""Embeddings de OpenAI para el índice Redis de 768 dimensiones."""

from __future__ import annotations

import config

_AVISO = (
    "Falta OPENAI_API_KEY o OPENAI_EMBEDDINGS_MODEL en el .env. "
    "Copie .env.example a .env y complete sus credenciales."
)


def modelo_embeddings():
    if not config.OPENAI_API_KEY or not config.MODELO_EMBEDDINGS:
        raise RuntimeError(_AVISO)
    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(
        model=config.MODELO_EMBEDDINGS,
        api_key=config.OPENAI_API_KEY,
        dimensions=config.DIMENSIONES,
        request_timeout=30,
        max_retries=1,
    )


def embeber(textos: list[str]) -> list[list[float]]:
    return modelo_embeddings().embed_documents(textos)


def embeber_consulta(texto: str) -> list[float]:
    return modelo_embeddings().embed_query(texto)


def dimensiones() -> int:
    return config.DIMENSIONES
