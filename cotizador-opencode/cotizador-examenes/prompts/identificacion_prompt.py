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
- Veredicto `dudoso`: lo que ofrece el centro PODRÍA SER o PODRÍA INCLUIR el examen pedido, pero no
  hay certeza (por ejemplo, una evaluación integral que solo lo incluye "según criterio del profesional").
- Veredicto `no_coincide`: el centro no ofrece el examen pedido. Es `no_coincide` (no `dudoso`)
  cuando lo que tiene es un examen DISTINTO, aunque sea de la misma especialidad o sirva para
  controlar la misma enfermedad. Ejemplo: si se pide la medición de la presión ocular y el centro
  solo ofrece un fondo de ojo, es `no_coincide`; el fondo de ojo no mide la presión.
- No marques `dudoso` solo porque el examen del centro se relacione con la misma enfermedad del
  usuario; `dudoso` exige que podría tratarse del mismo examen pedido.
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
