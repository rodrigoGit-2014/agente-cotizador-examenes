"""Validación de ciudades de Chile (`spec.md` §5.6, [P-13])."""

from __future__ import annotations

import json
import unicodedata

import config

_CACHE: set[str] | None = None


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.strip().lower()


def _ciudades() -> set[str]:
    global _CACHE
    if _CACHE is None:
        if config.CIUDADES_CHILE_PATH.exists():
            datos = json.loads(config.CIUDADES_CHILE_PATH.read_text(encoding="utf-8"))
            _CACHE = {_normalizar(c) for c in datos.get("ciudades", [])}
        else:
            _CACHE = set()
    return _CACHE


def es_ciudad_chile(ciudad: str | None) -> bool:
    return bool(ciudad) and _normalizar(ciudad) in _ciudades()
