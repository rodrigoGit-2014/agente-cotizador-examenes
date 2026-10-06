"""Síntomas de alerta (`spec.md` §6.1, [P-08], RF-42).

Lista cerrada con los tres síntomas del intent y un mensaje fijo que no evalúa gravedad.
"""

from __future__ import annotations

import unicodedata

SINTOMAS_AGUDOS = (
    "perdida de vision",
    "dolor ocular",
    "vision borrosa reciente",
    "vision borrosa",
    "borroso",
)

MENSAJE_URGENCIAS = (
    "No puedo evaluar síntomas. Si es un síntoma nuevo o intenso, acuda a un servicio de urgencia."
)


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()


def detectar(texto: str | None) -> bool:
    t = _normalizar(texto or "")
    return any(s in t for s in SINTOMAS_AGUDOS)
