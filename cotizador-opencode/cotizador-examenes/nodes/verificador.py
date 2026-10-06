"""Nodo `verificador` (`spec.md` §5.2, RF-24/26, [P-11]).

Antes de responder, cada dato del reporte debe aparecer en una observación; el que no aparezca
se reemplaza por "no confirmado". También revisa el texto redactado y retira recomendaciones.
"""

from __future__ import annotations

import re

from langchain_core.messages import AIMessage

from schemas import Precio, Reporte

RECOMENDACIONES_RE = re.compile(
    r"[^.]*\b(?:le recomiendo|te recomiendo|recomiendo el|recomiendo la|el mejor centro|"
    r"la mejor opción|lo mejor es)\b[^.]*\.?",
    re.IGNORECASE,
)
PRECIO_RE = re.compile(r"\$\s?\d[\d.]*")
FECHA_RE = re.compile(r"\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?")


def _solo_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto)


def _verificar_comparables(reporte: Reporte, observaciones: str, digitos: str) -> list[str]:
    correcciones: list[str] = []
    for cot in reporte.comparables:
        if cot.precio.tipo != "no_confirmado":
            numeros = [cot.precio.valor, cot.precio.desde, cot.precio.hasta]
            if not any(n is not None and str(int(n)) in digitos for n in numeros):
                cot.precio = Precio()
                correcciones.append(f"{cot.centro}: precio -> no confirmado")
        if cot.proxima_hora.estado == "confirmada" and cot.proxima_hora.valor:
            if cot.proxima_hora.valor not in observaciones:
                cot.proxima_hora.estado = "no_confirmada"
                cot.proxima_hora.valor = None
                correcciones.append(f"{cot.centro}: hora -> no confirmada")
        if cot.preparacion.estado == "informada" and cot.preparacion.texto:
            fragmento = cot.preparacion.texto[:20].lower()
            if fragmento and fragmento not in observaciones.lower():
                cot.preparacion.estado = "no_confirmada"
                cot.preparacion.texto = None
                correcciones.append(f"{cot.centro}: preparación -> no confirmada")
    return correcciones


def _retirar_recomendaciones(texto: str) -> tuple[str, bool]:
    """Retira recomendaciones. Devuelve (texto, hubo_recomendacion).

    Solo cuenta como cambio si de verdad se retiró una recomendación: antes, colapsar cualquier
    espacio doble (por ejemplo los saltos de párrafo) marcaba toda respuesta como corregida y
    dejaba `verificacion.aprobado` en False.
    """
    sin_recomendacion = RECOMENDACIONES_RE.sub("", texto)
    if sin_recomendacion == texto:
        return texto, False
    limpio = re.sub(r"[ \t]{2,}", " ", sin_recomendacion).strip()
    return limpio, True


def _marcar_no_confirmado(texto: str, observaciones: str, digitos: str) -> tuple[str, bool]:
    cambio = False

    def _precio(m):
        nonlocal cambio
        if _solo_digitos(m.group(0)) in digitos:
            return m.group(0)
        cambio = True
        return "[no confirmado]"

    def _fecha(m):
        nonlocal cambio
        if m.group(0) in observaciones:
            return m.group(0)
        cambio = True
        return "[no confirmado]"

    nuevo = PRECIO_RE.sub(_precio, texto)
    nuevo = FECHA_RE.sub(_fecha, nuevo)
    return nuevo, cambio


def nodo_verificador(state: dict) -> dict:
    reporte: Reporte | None = state.get("reporte")
    observaciones = " ".join(state.get("observaciones", []))
    digitos = _solo_digitos(observaciones)

    correcciones: list[str] = []
    if reporte is not None:
        correcciones = _verificar_comparables(reporte, observaciones, digitos)

    ultimo = state["messages"][-1] if state.get("messages") else None
    texto_original = getattr(ultimo, "content", "") if ultimo is not None else ""
    mensajes: list = []
    texto_final = texto_original

    if isinstance(texto_original, str) and texto_original:
        texto_final, rec = _retirar_recomendaciones(texto_original)
        texto_final, dato = _marcar_no_confirmado(texto_final, observaciones, digitos)
        if rec:
            correcciones.append("texto: recomendación retirada")
        if dato:
            correcciones.append("texto: dato sin respaldo -> [no confirmado]")
        if texto_final != texto_original:
            mensajes = [AIMessage(content=texto_final)]

    verificacion = {
        "aprobado": not correcciones,
        "correcciones": correcciones,
        "texto_original": texto_original,
    }
    salida: dict = {"verificacion": verificacion}
    if reporte is not None:
        salida["reporte"] = reporte
    if mensajes:
        salida["messages"] = mensajes
    return salida
