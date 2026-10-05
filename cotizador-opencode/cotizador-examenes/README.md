# Cotizador de exámenes médicos

Asistente que permite a una persona en Chile saber, en una sola consulta, **qué centros hacen el
examen que necesita, cuánto cuesta y cuándo hay hora**, sin llamar centro por centro. Interpreta la
necesidad en palabras propias, busca centros de la especialidad en la ciudad, identifica en cada centro
el examen que corresponde por su **propósito**, consulta los centros mediante **llamadas simuladas** y
presenta las opciones de forma comparable. **Informa, no decide.**

V1 es un banco de pruebas: la búsqueda de centros es real (con instantánea versionada por defecto); los
centros, sus documentos, sus conversaciones, precios y agendas son simulados. La exactitud se mide
contra la verdad del simulador.

## Estado de la implementación

La implementación avanza por pasos definidos en `../plan.json`. Requisitos verificables en `spec.md`;
fuente de verdad del producto en `intent.md`.

## Flujo del grafo

```text
START ─► router ─┬─► respuesta_directa ────────────────────────────────────────► END
                 │      (saludo · qué puede hacer · límite · pedir datos)
                 └─► agente ⇄ herramientas
                          │  tope por código ─► consolidar
                          └──────────────────► consolidar ─► responder ─► verificador ─► END
```

Herramientas (las únicas que ve el LLM): `buscar_centros`, `identificar_examen`, `consultar_centro`,
`consultar_documentos`.

Las consultas de catálogo recorren `router → catalogo → END`. El nodo lee en Redis las
listas de exámenes y los fragmentos generales de los centros para mostrar nombre y ciudad.
No realiza llamadas ni confirma precios o agenda. Si la ciudad no está documentada, la
marca como no confirmada. Puede preguntarse «¿Qué exámenes tienes disponibles y en qué
ciudad?» o «¿Qué exámenes tienes en Santiago?». No hace falta recargar los documentos.

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
OPENAI_API_KEY=...           # clave de la API de OpenAI (LLM y embeddings)
OPENAI_MODEL=gpt-4.1-mini
OPENAI_EMBEDDINGS_MODEL=text-embedding-3-small
REDIS_URL=...                 # Redis del curso (vector store)
BUSQUEDA_API_KEY=            # opcional: solo para el modo en vivo (DA-02)
```

`config.py` es el único módulo que lee el `.env`. La implementación activa usa OpenAI; las referencias a Gemini en la especificación original describen el proveedor anterior. Se requiere una clave de la API de OpenAI con acceso y saldo disponibles. Los embeddings se solicitan a 768 dimensiones, igual que el índice Redis. Al cambiar de modelo se recargan los documentos porque los vectores anteriores no son intercambiables.

### Ficha del modelo y parámetros

| Parámetro | Valor | Dónde |
|---|---|---|
| `MODELO_LLM` | `OPENAI_MODEL` del `.env` | `config.py` |
| `MODELO_EMBEDDINGS` | `OPENAI_EMBEDDINGS_MODEL` del `.env` | `config.py` |
| `TEMPERATURA_AGENTE` / `TEMPERATURA_RECEPCIONISTA` | 0,0 / 0,1 | `config.py` |
| `N_POR_DEFECTO` | 2 | `config.py` |
| `K_MAX_CENTROS` | 6 | `config.py` |
| `MAX_ITERACIONES` | 10 | `config.py` |
| `BUSQUEDA_MODO` | `instantanea` (por defecto) · `en_vivo` | `config.py` |
| `ESCENARIO_POR_DEFECTO` | `default` | `config.py` |
| `INDICE_CENTROS` | `cotizador_centros_v1` (prefijo `cotizador:frag`) | `config.py` |

La condición de parada y el tope están implementados en `main.py` (`despues_agente`) y en
`tools/consultar_centro.py` (no se consulta si ya hay N comparables).

## Ejecución

El historial permite recordar el nombre que el usuario indique voluntariamente y resumir
sus consultas anteriores dentro de la misma sesión. El nombre no se envía a herramientas
ni centros. La memoria vive únicamente en el proceso: al cerrar el programa se pierde.
Preguntas como «¿cómo me llamo?» y «¿qué consultas he realizado?» se responden desde el
historial, sin cotizar ni buscar centros.

1. Cargar los documentos en el Redis del curso (una vez):

   ```bash
   python scripts/ingesta.py
   ```

2. Conversar con el agente:

   ```bash
   python main.py
   ```

## Datos de prueba

Todo dato de prueba está versionado en `data/` y **se carga, no se genera** durante la ejecución:

* `data/documentos/*.pdf` — un PDF por centro (incluye un centro de oncología en Santiago).
* `data/revision_documentos.md` — revisión manual de cada documento (A1) y unión teléfono ↔ documento (A2).
* `data/instantaneas/` — instantáneas de búsqueda (una normal y una con inyección de prueba).
* `data/eventos.json` — los seis eventos de conversación.
* `data/escenarios/` — escenarios (`default`, `no_contesta`, `cortada_y_suspendido`, `agenda`,
  `intenta_agendar`, `inyeccion`). Reglas de combinación y horas revisadas en `data/revision_escenarios.md`.
* `data/ciudades_chile.json` — lista versionada de ciudades de Chile.

Los scripts `scripts/generar_documentos.py` y `scripts/capturar_instantanea.py` son **solo de desarrollo**.

## Evaluación

* `validacion/golden_set.json` (G01–G16) y `validacion/seguridad.json` (S1–S6).
* `validacion/run_golden.py` y `validacion/run_seguridad.py` ejecutan el agente con
  `astream(..., stream_mode="updates")` y comparan contra lo esperado.
* `validacion/resultados_{fecha}.xlsx` con las hojas `Detalle`, `Resumen` y `Fallos`.

## Estructura

```
cotizador-examenes/
├── main.py              grafo START → END (sin lógica de negocio)
├── config.py            .env + parámetros centralizados
├── state.py             estado compartido del grafo
├── schemas.py           modelos de dominio (Pydantic)
├── nodes/               router, respuesta_directa, agente, herramientas, consolidar, responder, verificador
├── tools/               las 4 herramientas del agente
├── agents/              identificador, interpretador, recepcionista
├── services/            llm, embeddings, redis_store, ingesta, busqueda, simulador, ciudades, privacidad, sintomas
├── prompts/             un prompt por llamada al LLM + seguridad.py
├── data/                datos de prueba versionados
├── validacion/          golden set y pruebas de seguridad
├── notebooks/           notebook de entrega y estudio
└── scripts/             herramientas de desarrollo
```
