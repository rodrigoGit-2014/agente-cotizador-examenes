"""Configuración centralizada del cotizador.

Único módulo que lee variables de entorno (`os.environ`). Todo lo demás importa de aquí.
Ver `spec.md` §5.11.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Carga el .env de la raíz del repositorio y, si existe, el de cotizador-examenes/ (este último prevalece).
load_dotenv(BASE_DIR.parent / ".env")
load_dotenv(BASE_DIR / ".env", override=True)


# --- Credenciales (solo nombres en el código; valores en .env) -----------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDINGS_MODEL = os.getenv("OPENAI_EMBEDDINGS_MODEL")
OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")
BUSQUEDA_API_KEY = os.getenv("BUSQUEDA_API_KEY")

# Modelo del LLM en formato "proveedor:modelo", con proveedor "openai" u "opencode".
# Ej.: "opencode:deepseek-v4.1-flash" o "openai:gpt-5.4-mini".
LLM_MODELO_AGENTE = os.getenv("LLM_MODELO_AGENTE", "")

# OpenCode Zen expone una API compatible con OpenAI.
OPENCODE_BASE_URL = "https://opencode.ai/zen/v1"
PROVEEDORES_LLM = ("openai", "opencode")


# --- Parámetros fijos del agente (spec.md §5.11) -------------------------------

TEMPERATURA_AGENTE = 0.0
TEMPERATURA_RECEPCIONISTA = 0.1

# Tiempos de red del LLM: acotan cuánto espera el grafo por una llamada colgada y cuántos
# reintentos silenciosos puede hacer el cliente antes de fallar.
LLM_TIMEOUT_S = 90.0
LLM_MAX_REINTENTOS = 1

PROVEEDOR_LLM, _, MODELO_LLM = LLM_MODELO_AGENTE.partition(":")
MODELO_EMBEDDINGS = OPENAI_EMBEDDINGS_MODEL
DIMENSIONES = 768

N_POR_DEFECTO = 2
K_MAX_CENTROS = 6
MAX_ITERACIONES = 10

BUSQUEDA_MODO = os.getenv("BUSQUEDA_MODO", "web_snapshot")
ESCENARIO_POR_DEFECTO = "default"

# Redis del curso: índice vectorial de los documentos de centro.
INDICE_CENTROS = "cotizador_centros_v1"
PREFIJO_FRAGMENTOS = "cotizador:frag"
TOP_K_FRAGMENTOS = 4


# --- Rutas del proyecto ---------------------------------------------------------

DATA_DIR = BASE_DIR / "data"
DOCUMENTOS_DIR = DATA_DIR / "documentos"
WEB_SNAPSHOTS_DIR = DATA_DIR / "web_snapshots"
ESCENARIOS_DIR = DATA_DIR / "escenarios"
EVENTOS_PATH = DATA_DIR / "eventos.json"
CIUDADES_CHILE_PATH = DATA_DIR / "ciudades_chile.json"
PROMPTS_DIR = BASE_DIR / "prompts"
RESULTADOS_DIR = BASE_DIR / "resultados"


def credenciales_presentes() -> dict[str, bool]:
    """Devuelve qué credenciales están definidas, sin exponer sus valores."""
    return {
        "OPENAI_API_KEY": bool(OPENAI_API_KEY),
        "OPENAI_EMBEDDINGS_MODEL": bool(OPENAI_EMBEDDINGS_MODEL),
        "OPENCODE_API_KEY": bool(OPENCODE_API_KEY),
        "LLM_MODELO_AGENTE": bool(LLM_MODELO_AGENTE),
        "REDIS_URL": bool(REDIS_URL),
        "BUSQUEDA_API_KEY": bool(BUSQUEDA_API_KEY),
    }


def resumen() -> dict[str, object]:
    """Configuración no sensible, para imprimir en el notebook y en debug."""
    return {
        "proveedor_llm": PROVEEDOR_LLM,
        "modelo_llm": MODELO_LLM,
        "modelo_embeddings": MODELO_EMBEDDINGS,
        "dimensiones": DIMENSIONES,
        "temperatura_agente": TEMPERATURA_AGENTE,
        "temperatura_recepcionista": TEMPERATURA_RECEPCIONISTA,
        "llm_timeout_s": LLM_TIMEOUT_S,
        "llm_max_reintentos": LLM_MAX_REINTENTOS,
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
