"""Nodo `consolidar` (`spec.md` §5.2, §5.10).

Arma el reporte (comparables, dudosos, descartados, trayectoria) y calcula el motivo de parada.
"""

from __future__ import annotations

import config
from langchain_core.messages import ToolMessage
from schemas import (
    Cotizacion,
    Descartado,
    Dudoso,
    Identificacion,
    Reporte,
    Solicitud,
    Trayectoria,
)


def _motivo_descarte(ident: Identificacion, cot: Cotizacion | None) -> str:
    if ident.veredicto in ("no_coincide",):
        return "no_coincide"
    if ident.veredicto == "sin_documento":
        return "no_contesta"
    if cot is None:
        return "no_contesta"
    if not cot.contesto:
        return "no_contesta"
    if cot.realiza in ("no", "no_temporalmente"):
        return "no_realiza"
    if cot.proxima_hora.estado in ("no_disponible", "no_confirmada"):
        return "sin_horas"
    return "no_contesta"


def _motivo_parada(state: dict, comparables: list[Cotizacion], hay_coincide: bool,
                   ninguno_contesta: bool) -> str:
    if state.get("iteraciones", 0) >= config.MAX_ITERACIONES:
        return "tope_iteraciones"
    if state.get("ruta") == "info_publicada":
        return "respuesta_info_publicada"
    if not state.get("centros"):
        return "sin_centros"
    if hay_coincide and ninguno_contesta:
        return "ninguno_contesta"
    if len(comparables) >= (state.get("solicitud").N if state.get("solicitud") else config.N_POR_DEFECTO):
        return "N_alcanzado"
    if not hay_coincide:
        return "sin_coincidencias"
    return "centros_agotados"


def nodo_consolidar(state: dict) -> dict:
    solicitud: Solicitud = state.get("solicitud") or Solicitud()
    centros = {c.centro_id: c for c in state.get("centros", [])}
    identificaciones: dict[str, Identificacion] = state.get("identificaciones", {})
    cotizaciones: dict[str, Cotizacion] = state.get("cotizaciones", {})

    comparables: list[Cotizacion] = []
    dudosos: list[Dudoso] = []
    descartados: list[Descartado] = []
    hay_coincide = False
    algun_contesta = False

    for centro_id, ident in identificaciones.items():
        centro = centros.get(centro_id)
        nombre = centro.nombre if centro else centro_id
        cot = cotizaciones.get(centro_id)

        if ident.veredicto == "dudoso":
            dudosos.append(
                Dudoso(centro_id=centro_id, centro=nombre,
                       nombre_examen_centro=ident.nombre_examen_centro,
                       justificacion=ident.justificacion)
            )
            continue

        if ident.veredicto == "coincide":
            hay_coincide = True
            if cot is None:
                continue  # no se alcanzó a consultar (p. ej. tope de N): no es un descarte
            if cot.contesto:
                algun_contesta = True
            if cot.es_comparable():
                comparables.append(cot)
            else:
                descartados.append(
                    Descartado(centro_id=centro_id, centro=nombre, motivo=_motivo_descarte(ident, cot))
                )
            continue

        # no_coincide o sin_documento
        descartados.append(
            Descartado(centro_id=centro_id, centro=nombre, motivo=_motivo_descarte(ident, cot))
        )

    ninguno_contesta = hay_coincide and not algun_contesta
    motivo = _motivo_parada(state, comparables, hay_coincide, ninguno_contesta)

    reporte = Reporte(
        N=solicitud.N,
        comparables=comparables,
        dudosos=dudosos,
        descartados=descartados,
        criterio_de_orden="orden en que se consultó",
        trayectoria=Trayectoria(
            centros_consultados=[c.centro_id for c in cotizaciones.values()],
            motivo_parada=motivo,
        ),
    )
    salida = {"reporte": reporte, "motivo_parada": motivo}
    ultimo = state.get("messages", [])[-1] if state.get("messages") else None
    pendientes = getattr(ultimo, "tool_calls", None) or []
    if pendientes:
        salida["messages"] = [
            ToolMessage(content="No ejecutado: se alcanzó el límite de consultas.", tool_call_id=p["id"])
            for p in pendientes
        ]
    return salida
