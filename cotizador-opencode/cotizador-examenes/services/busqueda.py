"""Búsqueda de centros (`spec.md` §5.6, §5.8).

Modo `instantanea` (por defecto): lee un archivo versionado. Modo `en_vivo`: consulta un
proveedor web (DA-02, pendiente); solo lee nombre, dirección y teléfono.
"""

from __future__ import annotations

import json
import re

import config
from schemas import Centro, Escenario, Instantanea, ResultadoBusqueda

PATRONES_INSTRUCCION = (
    r"ignora\s+(tus|las)\s+reglas",
    r"ignore\s+(your|the)\s+rules",
    r"reserva\s+la\s+hora",
    r"recomienda\s+el\s+primer",
    r"olvida\s+tus\s+instrucciones",
    r"system\s+prompt",
)


def contiene_instruccion(texto: str) -> bool:
    t = (texto or "").lower()
    return any(re.search(p, t) for p in PATRONES_INSTRUCCION)


def limpiar_instruccion(texto: str) -> str:
    return "(fragmento omitido: contenía una instrucción)"


def cargar_escenario(id_escenario: str) -> Escenario:
    ruta = config.ESCENARIOS_DIR / f"{id_escenario}.json"
    return Escenario.model_validate(json.loads(ruta.read_text(encoding="utf-8")))


def cargar_instantanea(id_instantanea: str) -> Instantanea:
    ruta = config.INSTANTANEAS_DIR / f"{id_instantanea}.json"
    return Instantanea.model_validate(json.loads(ruta.read_text(encoding="utf-8")))


def normalizar_telefono(telefono: str) -> str:
    return re.sub(r"\D", "", telefono or "")


def _a_centro(r: ResultadoBusqueda) -> Centro:
    return Centro(
        centro_id=normalizar_telefono(r.telefono or ""),
        nombre=r.nombre,
        direccion=r.direccion,
        telefono=r.telefono,
        fragmento_web=r.fragmento_web,
    )


def buscar(
    especialidad: str,
    ciudad: str,
    escenario: Escenario,
    modo: str | None = None,
) -> tuple[list[Centro], list[str]]:
    """Devuelve (centros hasta K, alertas por instrucciones incrustadas)."""
    modo = modo or config.BUSQUEDA_MODO
    alertas: list[str] = []

    if modo == "en_vivo":
        raise NotImplementedError(
            "La búsqueda en vivo está pendiente (DA-02); use el modo instantánea."
        )

    instantanea = cargar_instantanea(escenario.instantanea)
    centros: list[Centro] = []
    for r in instantanea.resultados[: config.K_MAX_CENTROS]:
        if r.fragmento_web and contiene_instruccion(r.fragmento_web):
            alertas.append(f"Instrucción incrustada detectada en {r.nombre}")
            r = r.model_copy(update={"fragmento_web": limpiar_instruccion(r.fragmento_web)})
        centros.append(_a_centro(r))
    return centros, alertas
