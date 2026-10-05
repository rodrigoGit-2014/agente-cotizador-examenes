"""Interpretación de una transcripción en una `Cotizacion` (`spec.md` §5.8).

Con validación por código [P-06]: cada valor distinto de "no confirmado" debe aparecer en la
transcripción; si no, pasa a "no confirmado" y se registra.
"""

from __future__ import annotations

import re

import config
import services.llm
from prompts.interpretar_prompt import construir_mensajes
from schemas import Cotizacion, Precio, SalidaInterpretacion, TurnoTranscripcion


def _formatear(transcripcion: list[dict]) -> str:
    return "\n".join(
        f"{'Paciente' if t['hablante'] == 'llamador' else 'Recepción'}: {t['texto']}"
        for t in transcripcion
    )


def _normalizar(salida) -> SalidaInterpretacion:
    if isinstance(salida, SalidaInterpretacion):
        return salida
    return SalidaInterpretacion(**dict(salida))


def validar_fuente(cot: Cotizacion, texto: str) -> list[str]:
    """[P-06] Reemplaza por "no confirmado" todo valor que no aparezca en la transcripción."""
    plano = re.sub(r"\s+", " ", texto)
    digitos = re.sub(r"\D", "", plano)
    corregidos: list[str] = []

    if cot.precio.tipo != "no_confirmado":
        numeros = [cot.precio.valor, cot.precio.desde, cot.precio.hasta]
        if not any(n is not None and str(int(n)) in digitos for n in numeros):
            corregidos.append("precio")
            cot.precio = Precio()

    if cot.proxima_hora.estado == "confirmada" and cot.proxima_hora.valor:
        if cot.proxima_hora.valor not in plano:
            corregidos.append("proxima_hora")
            cot.proxima_hora.estado = "no_confirmada"
            cot.proxima_hora.valor = None

    if cot.preparacion.estado == "informada" and cot.preparacion.texto:
        fragmento = cot.preparacion.texto[:25].lower()
        if fragmento and fragmento not in plano.lower():
            corregidos.append("preparacion")
            cot.preparacion.estado = "no_confirmada"
            cot.preparacion.texto = None

    return corregidos


def interpretar(
    transcripcion: list[dict],
    *,
    centro_id: str,
    centro: str,
    codigo_examen: str,
    nombre_examen_centro: str,
    eventos: list[str] | None = None,
) -> Cotizacion:
    texto = _formatear(transcripcion)
    llm = services.llm.llm_estructurado(SalidaInterpretacion, temperatura=config.TEMPERATURA_AGENTE)
    salida = _normalizar(llm.invoke(construir_mensajes(texto)))

    cotizacion = Cotizacion(
        centro_id=centro_id,
        centro=centro,
        codigo_examen=codigo_examen,
        nombre_examen_centro=nombre_examen_centro,
        contesto=salida.contesto,
        realiza=salida.realiza,
        precio=salida.precio,
        modalidad=salida.modalidad,
        proxima_hora=salida.proxima_hora,
        preparacion=salida.preparacion,
        reserva=salida.reserva,
        transcripcion=[TurnoTranscripcion(**t) for t in transcripcion],
        eventos_aplicados=list(eventos or []),
    )
    validar_fuente(cotizacion, texto)
    return cotizacion
