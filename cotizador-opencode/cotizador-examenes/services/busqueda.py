"""Búsqueda de centros (`spec.md` §5.6, §5.8).

Modo `web_snapshot` (por defecto): lee un archivo versionado. Modo `en_vivo`: consulta un
proveedor web (DA-02, pendiente); solo lee nombre, dirección y teléfono.
"""

from __future__ import annotations

import json
import re
import unicodedata

import config
from schemas import Centro, Escenario, WebSnapshot, ResultadoBusqueda

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


def cargar_web_snapshot(id_web_snapshot: str) -> WebSnapshot:
    ruta = config.WEB_SNAPSHOTS_DIR / f"{id_web_snapshot}.json"
    return WebSnapshot.model_validate(json.loads(ruta.read_text(encoding="utf-8")))


def normalizar_telefono(telefono: str) -> str:
    return re.sub(r"\D", "", telefono or "")


def _normalizar(texto: str) -> str:
    """Minúsculas y sin tildes, para comparar ciudades ('Puerto Montt' == 'puerto montt')."""
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.strip().lower()


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
            "La búsqueda en vivo está pendiente (DA-02); use el modo web_snapshot."
        )

    web_snapshot = cargar_web_snapshot(escenario.web_snapshot)
    # El web snapshot del escenario es de una ciudad concreta. Si se pide otra ciudad, no hay
    # datos para ella: se devuelve vacío, en vez de mostrar centros de otra ciudad
    # (RF-08: buscar "en la ciudad"; RF-40: agregar una ciudad = generar su web snapshot).
    if _normalizar(web_snapshot.ciudad) != _normalizar(ciudad):
        return [], []
    centros: list[Centro] = []
    for r in web_snapshot.resultados[: config.K_MAX_CENTROS]:
        if r.fragmento_web and contiene_instruccion(r.fragmento_web):
            alertas.append(f"Instrucción incrustada detectada en {r.nombre}")
            r = r.model_copy(update={"fragmento_web": limpiar_instruccion(r.fragmento_web)})
        centros.append(_a_centro(r))
    return centros, alertas
