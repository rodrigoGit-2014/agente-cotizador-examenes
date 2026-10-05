"""Modelos de datos del dominio (`spec.md` §5.5).

Modelos Pydantic v2 usados por el estado del grafo, las herramientas y el simulador.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field

# --- Enumeraciones --------------------------------------------------------------

Ruta = Literal["cotizar", "info_publicada", "catalogo", "respuesta_directa", "fuera_de_alcance"]

Veredicto = Literal["coincide", "dudoso", "no_coincide", "sin_documento"]

Realiza = Literal["si", "no", "no_temporalmente", "no_confirmado"]

TipoPrecio = Literal["cerrado", "rango", "referencial", "no_confirmado"]

Modalidad = Literal["particular", "Fonasa", "Isapre", "convenio", "no_especificada"]

EstadoHora = Literal["confirmada", "no_confirmada", "no_disponible", "no_aplica"]

EstadoPreparacion = Literal["informada", "no_confirmada"]

MotivoDescarte = Literal["no_realiza", "no_contesta", "sin_horas", "no_coincide", "sin_documento"]

Hablante = Literal["llamador", "centro"]

QuienResuelve = Literal["recepcionista", "codigo"]


class Prevision(str, Enum):
    """Previsión del usuario. `no_especificada` = el usuario dijo que no sabe."""

    fonasa = "Fonasa"
    isapre = "Isapre"
    particular = "particular"
    no_especificada = "no_especificada"
    no_indicada = "no_indicada"


# --- Entrada --------------------------------------------------------------------

class Solicitud(BaseModel):
    """Lo pedido por el usuario, ya extraído y validado."""

    necesidad: Optional[str] = None
    necesidad_ambigua: bool = False
    especialidad: Optional[str] = None
    ciudad: Optional[str] = None
    prevision: Prevision = Prevision.no_indicada
    N: int = Field(default=2, ge=1)
    N_por_defecto: bool = False


class SalidaRouter(BaseModel):
    """Salida estructurada del router (`spec.md` §5.7).

    Solo extrae los campos permitidos: necesidad, ciudad, previsión y N. Nunca nombre,
    RUT ni diagnóstico. `datos_personales` avisa si el usuario entregó esos datos.
    """

    ruta: Ruta = "respuesta_directa"
    necesidad: Optional[str] = None
    necesidad_ambigua: bool = False
    especialidad: Optional[str] = None
    ciudad: Optional[str] = None
    prevision: Prevision = Prevision.no_indicada
    N: Optional[int] = None
    datos_personales: bool = False
    motivo: str = ""


# --- Simulador: centros y exámenes ---------------------------------------------

class Centro(BaseModel):
    """Resultado de la búsqueda de centros."""

    centro_id: str
    nombre: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    fragmento_web: Optional[str] = None


class ExamenCentro(BaseModel):
    """Un examen del catálogo de un centro, extraído en la ingesta."""

    centro_id: str
    codigo: str
    nombre: str
    descripcion: str = ""
    proposito: str = ""


class Identificacion(BaseModel):
    """Decisión, para un centro, sobre cuál de sus exámenes corresponde a la necesidad."""

    centro_id: str
    veredicto: Veredicto
    codigo_examen: Optional[str] = None
    nombre_examen_centro: Optional[str] = None
    justificacion: str = ""


# --- Cotización -----------------------------------------------------------------

class Precio(BaseModel):
    """Precio tal como lo informó el centro. Nunca se calcula por previsión."""

    tipo: TipoPrecio = "no_confirmado"
    valor: Optional[float] = None
    desde: Optional[float] = None
    hasta: Optional[float] = None
    texto: Optional[str] = None


class ProximaHora(BaseModel):
    estado: EstadoHora = "no_confirmada"
    valor: Optional[str] = None  # "AAAA-MM-DD HH:MM"
    detalle: Optional[str] = None


class Preparacion(BaseModel):
    estado: EstadoPreparacion = "no_confirmada"
    texto: Optional[str] = None


class Reserva(BaseModel):
    ofrecida: bool = False
    aceptada: Literal[False] = False


class TurnoTranscripcion(BaseModel):
    hablante: Hablante
    texto: str


class Cotizacion(BaseModel):
    """Lo obtenido de un centro en una consulta (`spec.md` §5.5)."""

    centro_id: str
    centro: str
    codigo_examen: str = ""
    nombre_examen_centro: str = ""
    contesto: bool = False
    realiza: Realiza = "no_confirmado"
    precio: Precio = Field(default_factory=Precio)
    modalidad: Modalidad = "no_especificada"
    proxima_hora: ProximaHora = Field(default_factory=ProximaHora)
    preparacion: Preparacion = Field(default_factory=Preparacion)
    reserva: Reserva = Field(default_factory=Reserva)
    transcripcion: list[TurnoTranscripcion] = Field(default_factory=list)
    eventos_aplicados: list[str] = Field(default_factory=list)

    def es_comparable(self) -> bool:
        """Comparable = identifica 'coincide' ∧ contestó ∧ realiza ∧ precio confirmado.

        La parte de 'coincide' vive en la identificación; aquí se comprueba el resto.
        """
        return (
            self.contesto
            and self.realiza == "si"
            and self.precio.tipo != "no_confirmado"
        )


# --- Reporte --------------------------------------------------------------------

class Dudoso(BaseModel):
    centro_id: str
    centro: str
    nombre_examen_centro: Optional[str] = None
    justificacion: str = ""


class Descartado(BaseModel):
    centro_id: str
    centro: str
    motivo: MotivoDescarte


class Trayectoria(BaseModel):
    centros_consultados: list[str] = Field(default_factory=list)
    motivo_parada: Optional[str] = None


class Reporte(BaseModel):
    N: int
    comparables: list[Cotizacion] = Field(default_factory=list)
    dudosos: list[Dudoso] = Field(default_factory=list)
    descartados: list[Descartado] = Field(default_factory=list)
    criterio_de_orden: str = "orden en que se consultó"
    trayectoria: Trayectoria = Field(default_factory=Trayectoria)


# --- Datos de prueba ------------------------------------------------------------

class Evento(BaseModel):
    id: str
    descripcion: str = ""
    quien_lo_resuelve: QuienResuelve
    efecto: dict = Field(default_factory=dict)


class EventoAsignado(BaseModel):
    evento: str
    codigo_examen: Optional[str] = None
    tras_turno: Optional[int] = None


class Escenario(BaseModel):
    id: str
    descripcion: str = ""
    fecha_simulada: str
    instantanea: str
    horas: dict[str, dict[str, str]] = Field(default_factory=dict)
    eventos: dict[str, list[EventoAsignado]] = Field(default_factory=dict)


class ResultadoBusqueda(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    fragmento_web: Optional[str] = None


class Instantanea(BaseModel):
    id: str
    especialidad: str
    ciudad: str
    fecha_captura: str
    consulta_usada: str = ""
    resultados: list[ResultadoBusqueda] = Field(default_factory=list)


class CasoGoldenSet(BaseModel):
    id: str
    situacion: str
    escenario: str
    turnos: list[str] = Field(default_factory=list)
    esperado: dict = Field(default_factory=dict)


class PruebaSeguridad(BaseModel):
    id: str
    situacion: str
    escenario: str
    entrada: str
    criterios: dict = Field(default_factory=dict)


# --- Ingesta y RAG --------------------------------------------------------------

class Fragmento(BaseModel):
    """Un fragmento de un documento de centro cargado en Redis (`spec.md` §5.9)."""

    centro_id: str
    codigo_examen: str = "general"  # o el código interno del examen
    seccion: str
    texto: str
    fuente: str
    embedding: Optional[list[float]] = None


class ResultadoFragmento(BaseModel):
    texto: str
    seccion: str = ""
    codigo_examen: str = ""
    fuente: str = ""
    similitud: Optional[float] = None


# --- Salidas estructuradas de los LLM ------------------------------------------

class SalidaIdentificacion(BaseModel):
    """Salida del LLM de identificación (sin el centro_id, que lo pone el código)."""

    veredicto: Veredicto = "dudoso"
    codigo_examen: Optional[str] = None
    nombre_examen_centro: Optional[str] = None
    justificacion: str = ""


class SalidaInterpretacion(BaseModel):
    """Salida del LLM que interpreta una transcripción de llamada."""

    contesto: bool = False
    realiza: Realiza = "no_confirmado"
    precio: Precio = Field(default_factory=Precio)
    modalidad: Modalidad = "no_especificada"
    proxima_hora: ProximaHora = Field(default_factory=ProximaHora)
    preparacion: Preparacion = Field(default_factory=Preparacion)
    reserva: Reserva = Field(default_factory=Reserva)
