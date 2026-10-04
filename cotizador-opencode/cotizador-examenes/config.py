"""Configuración centralizada del cotizador.

Único módulo que lee variables de entorno (`os.environ`). Todo lo demás importa de aquí.
Ver `spec.md` §5.11.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Carga el .env de la raíz del proyecto (cotizador-examenes/.env).
load_dotenv(BASE_DIR / ".env")


# --- Credenciales (solo nombres en el código; valores en .env) -----------------

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL")
GOOGLE_EMBEDDINGS_MODEL = os.getenv("GOOGLE_EMBEDDINGS_MODEL")
REDIS_URL = os.getenv("REDIS_URL")
BUSQUEDA_API_KEY = os.getenv("BUSQUEDA_API_KEY")


# --- Parámetros fijos del agente (spec.md §5.11) -------------------------------

TEMPERATURA_AGENTE = 0.0
TEMPERATURA_RECEPCIONISTA = 0.1

MODELO_LLM = GOOGLE_MODEL
MODELO_EMBEDDINGS = GOOGLE_EMBEDDINGS_MODEL
DIMENSIONES = 768

N_POR_DEFECTO = 2
K_MAX_CENTROS = 6
MAX_ITERACIONES = 10

BUSQUEDA_MODO = os.getenv("BUSQUEDA_MODO", "instantanea")
ESCENARIO_POR_DEFECTO = "default"

# Redis del curso: índice vectorial de los documentos de centro.
INDICE_CENTROS = "cotizador_centros_v1"
PREFIJO_FRAGMENTOS = "cotizador:frag"
TOP_K_FRAGMENTOS = 4


# --- Rutas del proyecto ---------------------------------------------------------

DATA_DIR = BASE_DIR / "data"
DOCUMENTOS_DIR = DATA_DIR / "documentos"
INSTANTANEAS_DIR = DATA_DIR / "instantaneas"
ESCENARIOS_DIR = DATA_DIR / "escenarios"
EVENTOS_PATH = DATA_DIR / "eventos.json"
CIUDADES_CHILE_PATH = DATA_DIR / "ciudades_chile.json"
PROMPTS_DIR = BASE_DIR / "prompts"
RESULTADOS_DIR = BASE_DIR / "resultados"


def credenciales_presentes() -> dict[str, bool]:
    """Devuelve qué credenciales están definidas, sin exponer sus valores."""
    return {
        "GOOGLE_API_KEY": bool(GOOGLE_API_KEY),
        "GOOGLE_MODEL": bool(GOOGLE_MODEL),
        "GOOGLE_EMBEDDINGS_MODEL": bool(GOOGLE_EMBEDDINGS_MODEL),
        "REDIS_URL": bool(REDIS_URL),
        "BUSQUEDA_API_KEY": bool(BUSQUEDA_API_KEY),
    }


def resumen() -> dict[str, object]:
    """Configuración no sensible, para imprimir en el notebook y en debug."""
    return {
        "modelo_llm": MODELO_LLM,
        "modelo_embeddings": MODELO_EMBEDDINGS,
        "dimensiones": DIMENSIONES,
        "temperatura_agente": TEMPERATURA_AGENTE,
        "temperatura_recepcionista": TEMPERATURA_RECEPCIONISTA,
        "n_por_defecto": N_POR_DEFECTO,
        "k_max_centros": K_MAX_CENTROS,
        "max_iteraciones": MAX_ITERACIONES,
        "busqueda_modo": BUSQUEDA_MODO,
        "escenario_por_defecto": ESCENARIO_POR_DEFECTO,
        "indice_centros": INDICE_CENTROS,
    }


if __name__ == "__main__":
    from pprint import pprint

    print("Credenciales presentes (sin valores):")
    pprint(credenciales_presentes())
    print("Configuración:")
    pprint(resumen())
