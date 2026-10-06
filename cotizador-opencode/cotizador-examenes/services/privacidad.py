"""Privacidad: RUT y datos personales (`spec.md` §6.2, [P-01], RF-43)."""

from __future__ import annotations

import re

import config

RUT_RE = re.compile(r"\b\d{1,2}\.?\d{3}\.?\d{3}[-–]?[0-9kK]\b")
MARCA = "[RUT omitido]"


def contiene_rut(texto: str | None) -> bool:
    return bool(texto) and bool(RUT_RE.search(texto))


def enmascarar_rut(texto: str) -> str:
    """Reemplaza el RUT antes de guardarlo en el historial [P-01]."""
    return RUT_RE.sub(MARCA, texto or "")


def argumentos_con_dato_personal(args: dict) -> list[str]:
    """Nombres de los argumentos que contienen un RUT."""
    culpables = []
    for clave, valor in (args or {}).items():
        for hoja in _hojas(valor):
            if contiene_rut(hoja):
                culpables.append(clave)
                break
    return culpables


def _hojas(valor):
    if isinstance(valor, str):
        yield valor
    elif isinstance(valor, dict):
        for v in valor.values():
            yield from _hojas(v)
    elif isinstance(valor, (list, tuple)):
        for v in valor:
            yield from _hojas(v)


def preparar_entrada(texto: str):
    """Crea el HumanMessage del turno, enmascarando el RUT antes de guardarlo."""
    from langchain_core.messages import HumanMessage

    return HumanMessage(content=enmascarar_rut(texto))


def modelo_escenario_por_defecto() -> str:
    return config.ESCENARIO_POR_DEFECTO
