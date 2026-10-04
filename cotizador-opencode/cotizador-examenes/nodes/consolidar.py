"""Nodo `consolidar` — stub del paso `03`.

Arma un reporte mínimo (sin comparables) desde la solicitud y el motivo de parada. En el paso
`05` crecerá para armar comparables, dudosos y descartados desde las cotizaciones.
"""

from __future__ import annotations

from schemas import Reporte, Solicitud, Trayectoria


def nodo_consolidar(state: dict) -> dict:
    solicitud: Solicitud = state.get("solicitud") or Solicitud()
    motivo = state.get("motivo_parada") or "agente_no_implementado"
    reporte = Reporte(
        N=solicitud.N,
        comparables=[],
        dudosos=[],
        descartados=[],
        trayectoria=Trayectoria(centros_consultados=[], motivo_parada=motivo),
    )
    return {"reporte": reporte, "motivo_parada": motivo}
