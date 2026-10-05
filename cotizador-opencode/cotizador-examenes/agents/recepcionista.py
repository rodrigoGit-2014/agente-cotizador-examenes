"""Recepcionista simulada (LLM) con validador de fidelidad (`spec.md` §5.8, [P-05])."""

from __future__ import annotations

import re

import services.llm
from prompts.recepcionista_prompt import construir_mensajes

PRECIO_RE = re.compile(r"\$\s?(\d{1,3}(?:[.\s]\d{3})+|\d{4,})")
FECHA_RE = re.compile(r"\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?")


def _texto(mensaje) -> str:
    contenido = getattr(mensaje, "content", mensaje)
    return contenido if isinstance(contenido, str) else str(contenido)


def responder(contexto: dict, transcripcion: list[dict]) -> str:
    """Un turno de la recepcionista, usando solo sus fragmentos, agenda y eventos."""
    llm = services.llm.llm_recepcionista()
    return _texto(llm.invoke(construir_mensajes(contexto, transcripcion))).strip()


def _normalizar_monto(crudo: str) -> str:
    return re.sub(r"\D", "", crudo)


def validar_fidelidad(transcripcion: list[dict], fuentes_texto: list[str]) -> list[str]:
    """Valores (montos o fechas) que dice la recepción y no existen en su fuente.

    Devuelve la lista de valores infieles. Vacía = fiel.
    """
    fuente_plana = re.sub(r"\s+", " ", " ".join(fuentes_texto))
    fuente_digitos = re.sub(r"\D", "", fuente_plana)
    faltantes: list[str] = []
    for t in transcripcion:
        if t.get("hablante") != "centro":
            continue
        texto = t.get("texto", "")
        for m in PRECIO_RE.finditer(texto):
            if _normalizar_monto(m.group(1)) not in fuente_digitos:
                faltantes.append(m.group(0))
        for m in FECHA_RE.finditer(texto):
            if m.group(0) not in fuente_plana:
                faltantes.append(m.group(0))
    return faltantes
