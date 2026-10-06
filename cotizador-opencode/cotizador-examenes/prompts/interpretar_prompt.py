"""Prompt del LLM que interpreta una transcripción de llamada (`spec.md` §5.8)."""

from __future__ import annotations

from prompts.seguridad import BLOQUE_AGENTE, BLOQUE_UNIVERSAL

SYSTEM = f"""\
Conviertes la transcripción de una llamada a un centro médico en una cotización estructurada.

{BLOQUE_UNIVERSAL}

{BLOQUE_AGENTE}

Reglas:
- Extrae SOLO lo que la recepción dijo en la transcripción. Si un dato no se mencionó, déjalo
  como "no_confirmado" (precio y hora) o "no_confirmada" (preparación).
- El precio se registra tal como lo informó el centro: cerrado, rango o referencial. No calcules
  precios por previsión.
- Si el centro entregó algún número como precio (aunque sea el valor particular y la previsión del
  usuario sea Fonasa o Isapre), regístralo con `modalidad` = la que el centro nombró y el `tipo`
  según cómo lo dijo. Solo deja el precio `no_confirmado` si el centro no dio ningún número.
- Si el centro pidió volver a llamar, la hora es "no_confirmada", nunca disponible.
- La preparación que el centro no mencionó queda "no_confirmada".
- Marca `contesto=True` solo si hubo conversación con el centro.
- `reserva.aceptada` es siempre False."""


def construir_mensajes(transcripcion_texto: str) -> list:
    from langchain_core.messages import HumanMessage, SystemMessage

    return [
        SystemMessage(content=SYSTEM),
        HumanMessage(content=f"Transcripción:\n{transcripcion_texto}"),
    ]
