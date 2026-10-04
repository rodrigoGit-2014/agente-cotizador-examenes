# Cotizador de exámenes médicos

Asistente que permite a una persona en Chile saber, en una sola consulta, **qué centros hacen el
examen que necesita, cuánto cuesta y cuándo hay hora**, sin llamar centro por centro. Interpreta la
necesidad en palabras propias, busca centros de la especialidad en la ciudad, identifica en cada centro
el examen que corresponde por su propósito, consulta los centros mediante llamadas simuladas y presenta
las opciones de forma comparable. **Informa, no decide.**

Este proyecto es el banco de pruebas (V1): la búsqueda de centros es real (con instantánea versionada por
defecto); los centros, sus documentos, sus conversaciones, precios y agendas son simulados. La exactitud
se mide contra la verdad del simulador.

## Requisitos

* Python 3.12 (o 3.10+).
* Credenciales propias: API key de Google Gemini y la URL del Redis del curso.

## Instalación

### macOS / Linux

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows

```powershell
python.exe --version
python.exe -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración

Copia `.env.example` a `.env` y completa tus credenciales (nunca se suben al repositorio):

```
GOOGLE_API_KEY=...
GOOGLE_MODEL=...
GOOGLE_EMBEDDINGS_MODEL=...
REDIS_URL=...
BUSQUEDA_API_KEY=
```

`config.py` es el único módulo que lee el `.env`.

## Verificación del entorno

```bash
python -c "import config; print(config.resumen())"
python -c "import state, schemas"
python -c "import services.llm; print('llm OK')"
```

## Estado del proyecto

La implementación avanza por pasos definidos en `../plan.json`. El paso actual y lo que falta se
consultan ahí. Los requisitos verificables están en `../spec.md` y la fuente de verdad del producto en
`../intent.md`.

## Estructura

```
cotizador-examenes/
├── main.py          grafo START → END (se agrega en el paso 03)
├── config.py        .env + parámetros centralizados
├── state.py         estado compartido del grafo
├── schemas.py       modelos de dominio (Pydantic)
├── nodes/           un nodo del grafo por archivo
├── tools/           las 4 herramientas del agente
├── agents/          subagentes LLM (identificador, interpretador, recepcionista)
├── services/        LLM, embeddings, Redis, búsqueda, simulador, ingesta
├── prompts/         un prompt por llamada al LLM (y bloques de seguridad)
├── data/            datos de prueba versionados (se cargan, no se generan)
├── scripts/         solo desarrollo: generar documentos, capturar instantánea, ingesta
└── resultados/      salidas de la última corrida
```
