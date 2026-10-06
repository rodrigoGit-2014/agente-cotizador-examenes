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

# Precio en pesos tal como lo escribe la recepción: "$42.000" o "$42000".
PRECIO_RE = re.compile(r"\$\s?(\d{1,3}(?:\.\d{3})+|\d{4,})")


def _montos_de(texto: str) -> list[tuple[str, float]]:
    """Pares (texto crudo, valor) de los precios que aparecen en la transcripción."""
    return [
        (m.group(0), float(m.group(1).replace(".", "")))
        for m in PRECIO_RE.finditer(texto)
    ]


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

    # La recepción dio un precio numérico pero el modelo no lo registró: se recupera por código.
    # El dato está en la transcripción, así que sigue siendo fiel a la fuente. Se exige un único
    # valor distinto para no confundir un rango con un precio cerrado.
    if cot.precio.tipo == "no_confirmado":
        montos = _montos_de(plano)
        if len({valor for _, valor in montos}) == 1:
            crudo, valor = montos[0]
            cot.precio = Precio(tipo="cerrado", valor=valor, texto=crudo)
            corregidos.append("precio (recuperado de la transcripción)")
            if cot.modalidad == "no_especificada" and "particular" in plano.lower():
                cot.modalidad = "particular"

    if cot.proxima_hora.estado == "confirmada" and cot.proxima_hora.valor:
        # Compara por dígitos: la recepción puede decir "el 2025-03-12 a las 09:00" y el modelo
        # devolver "2025-03-12 09:00"; exigir la subcadena exacta descartaba toda hora válida.
        digitos_hora = re.sub(r"\D", "", cot.proxima_hora.valor)
        if not digitos_hora or digitos_hora not in digitos:
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
