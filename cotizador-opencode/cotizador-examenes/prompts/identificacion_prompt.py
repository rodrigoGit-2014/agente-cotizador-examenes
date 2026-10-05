"""Prompt de identificación del examen por centro (`spec.md` §5.7)."""

from __future__ import annotations

from prompts.seguridad import BLOQUE_AGENTE, BLOQUE_UNIVERSAL

SYSTEM = f"""\
Decides, para un centro, cuál de sus exámenes corresponde a la necesidad del usuario.

{BLOQUE_UNIVERSAL}

{BLOQUE_AGENTE}

Criterio:
- Decide por la DESCRIPCIÓN y el PROPÓSITO del examen, no por su nombre. Dos exámenes con el
  mismo nombre y distinto propósito NO son el mismo.
- Veredicto `coincide`: el examen es claramente el que se necesita.
- Veredicto `dudoso`: podría corresponder, pero no con certeza.
- Veredicto `no_coincide`: el centro no ofrece ese examen.
- Si `coincide` o `dudoso`, devuelve el `codigo_examen` y el `nombre_examen_centro`.
- Justifica en una frase."""


def construir_mensajes(necesidad: str, examenes: list[dict]) -> list:
    from langchain_core.messages import HumanMessage, SystemMessage

    catalogo = "\n".join(
        f"- Código: {e['codigo']} | Nombre: {e['nombre']}\n"
        f"  Descripción: {e.get('descripcion', '')}\n"
        f"  Propósito: {e.get('proposito', '')}"
        for e in examenes
    )
    return [
        SystemMessage(content=SYSTEM),
        HumanMessage(
            content=f"Necesidad del usuario: {necesidad}\n\nExámenes del centro:\n{catalogo}"
        ),
    ]
