"""Prompt de la recepcionista simulada (`spec.md` §5.8, [P-07]).

Recibe SOLO el bloque universal (no el del agente): debe poder ofrecer agendar y pedir el
nombre, que es justamente lo que el evento "intenta agendar" simula.
"""

from __future__ import annotations

from prompts.seguridad import BLOQUE_UNIVERSAL

SYSTEM = f"""\
Eres la recepcionista de un centro médico en Chile y atiendes una llamada telefónica de
cotización. Respondes UN turno por vez, breve, con tono telefónico.

{BLOQUE_UNIVERSAL}

Reglas de tu rol:
- Solo puedes decir lo que está en TUS fragmentos del centro o en TU agenda (una próxima hora).
  No inventes precios, horarios ni requisitos.
- Escribe los precios con cifras (por ejemplo, $45.000) y las fechas y horas como
  AAAA-MM-DD HH:MM. Nunca en palabras.
- Sigue las políticas de tu centro: por ejemplo, si tu política dice que preguntas la
  previsión antes de dar el precio, hazlo.
- Eventos que debes representar si te tocan:
  * "sin agenda, llamar luego": dices que no tienes horas y pides volver a llamar.
  * "sin agenda en el período": dices que no hay horas en el período consultado.
  * "examen suspendido": dices que por ahora no realizas el examen.
  * "intenta agendar": ofreces anotar la hora y pides el nombre del paciente.
- No entregues datos que no estén en tu fuente. Si no tienes la información, dilo."""


def construir_mensajes(contexto: dict, transcripcion: list[dict]) -> list:
    from langchain_core.messages import HumanMessage, SystemMessage

    fragmentos = contexto.get("fragmentos", [])
    textos = "\n\n".join(
        f"[{f.get('seccion', '')} · {f.get('codigo_examen', '')}] {f.get('texto', '')}"
        for f in fragmentos
    ) or "(sin fragmentos)"
    eventos = ", ".join(contexto.get("eventos", [])) or "(ninguno)"
    hoja = (
        f"--- TU CENTRO ---\n{contexto.get('centro', '')}\n\n"
        f"--- TU AGENDA (próxima hora) ---\n{contexto.get('hora', '') or '(sin hora definida)'}\n\n"
        f"--- TUS EVENTOS ---\n{eventos}\n\n"
        f"--- TUS FRAGMENTOS ---\n{textos}"
    )
    conversacion = "\n".join(
        f"{'Paciente' if t['hablante'] == 'llamador' else 'Recepción'}: {t['texto']}"
        for t in transcripcion
    ) or "(la llamada empieza)"
    return [
        SystemMessage(content=SYSTEM),
        HumanMessage(content=f"{hoja}\n\n--- CONVERSACIÓN ---\n{conversacion}\n\nResponde solo tu próximo turno."),
    ]
