"""Embeddings de Google Gemini (`spec.md` §5.9)."""

from __future__ import annotations

import config

_AVISO = (
    "Falta GOOGLE_API_KEY o GOOGLE_EMBEDDINGS_MODEL en el .env. "
    "Copie .env.example a .env y complete sus credenciales."
)


def modelo_embeddings():
    if not config.GOOGLE_API_KEY or not config.MODELO_EMBEDDINGS:
        raise RuntimeError(_AVISO)
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    return GoogleGenerativeAIEmbeddings(
        model=config.MODELO_EMBEDDINGS,
        google_api_key=config.GOOGLE_API_KEY,
    )


def embeber(textos: list[str]) -> list[list[float]]:
    return modelo_embeddings().embed_documents(textos)


def embeber_consulta(texto: str) -> list[float]:
    return modelo_embeddings().embed_query(texto)


def dimensiones() -> int:
    return config.DIMENSIONES
