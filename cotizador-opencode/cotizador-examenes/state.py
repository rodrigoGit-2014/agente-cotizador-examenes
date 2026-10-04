"""Estado compartido del grafo (`spec.md` §5.4).

`messages` persiste entre turnos del mismo hilo (checkpointer). Los demás campos se
reinician en cada turno, salvo `prevision_preguntada`.
"""

from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages

from schemas import (
    Centro,
    Cotizacion,
    Identificacion,
    Reporte,
    Ruta,
    Solicitud,
)


class Estado(TypedDict, total=False):
    # Historial: usuario, pedidos de herramientas, observaciones y respuestas.
    messages: Annotated[list, add_messages]

    # Ruta elegida por el router.
    ruta: Ruta

    # Escenario activo del turno (para que las herramientas lean el mundo correcto).
    escenario_id: str

    # Solicitud extraída (necesidad, ciudad, previsión, N).
    solicitud: Solicitud

    # Control de la pregunta por previsión (RF-05); persiste entre turnos.
    prevision_preguntada: bool

    # Aviso de privacidad (RF-43).
    datos_personales_detectados: bool

    # Resultado de la búsqueda del turno (máx. K).
    centros: list[Centro]

    # Identificación del examen por centro.
    identificaciones: dict[str, Identificacion]

    # Cotizaciones registradas por centro.
    cotizaciones: dict[str, Cotizacion]

    # Observaciones del turno en JSON; fuente del verificador.
    observaciones: list[str]

    # Instrucciones incrustadas detectadas en contenido externo (RF-44).
    alertas: list[str]

    # Llamadas rechazadas por validación, con motivo.
    rechazos: list[dict]

    # Rondas agente -> herramientas.
    iteraciones: int

    # Motivo de parada (`spec.md` §5.10).
    motivo_parada: str

    # Reporte consolidado (comparables, dudosos, descartados, trayectoria).
    reporte: Reporte

    # Veredicto del verificador, valores corregidos y texto original.
    verificacion: dict
