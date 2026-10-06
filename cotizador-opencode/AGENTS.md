# Arquitectura del proyecto

Este proyecto desarrolla el **Cotizador de exámenes médicos**, un agente de inteligencia artificial
construido con Python, LangGraph y LangChain (LLM vía OpenAI u OpenCode Zen, RAG sobre el Redis del curso).

El proyecto activo es **`cotizador-examenes/`**. Su especificación completa — flujo del grafo, router,
herramientas, simulador, ingesta y estructura de carpetas — vive en `opencode/agents/implementator.md`
y es la fuente de verdad de la implementación. Los requisitos de producto viven en `spec.md` (diseño
verificable) e `intent.md` (fuente de verdad del producto). Este archivo solo recoge las reglas que
aplican a cualquier paso del proyecto.

## Inicio

**Detecta primero el sistema operativo** y usa el intérprete que corresponda. No asumas ninguno de los
dos: en macOS/Linux `python.exe` no existe, y en Windows `python3` puede no estar en el PATH.

### macOS / Linux

```bash
python3 --version          # adapta las librerías a esta versión
python3 -m venv .venv      # crea el entorno
source .venv/bin/activate  # actívalo y úsalo para todo
```

### Windows

```powershell
python.exe --version          # adapta las librerías a esta versión
python.exe -m venv .venv      # crea el entorno
.venv\Scripts\activate        # actívalo y úsalo para todo
```

Una vez creado el entorno, el intérprete del proyecto es `.venv/bin/python` en macOS/Linux y
`.venv\Scripts\python.exe` en Windows. Usa siempre ese, no el del sistema, para instalar y ejecutar.

Equivalencias rápidas:

| | macOS / Linux | Windows |
|---|---|---|
| Intérprete del sistema | `python3` | `python.exe` |
| Activar el entorno | `source .venv/bin/activate` | `.venv\Scripts\activate` |
| Intérprete del entorno | `.venv/bin/python` | `.venv\Scripts\python.exe` |
| Separador de rutas | `/` | `\` (usa `pathlib.Path` en el código para no depender de esto) |

## Reglas obligatorias

* Directorio base del proyecto: `cotizador-examenes/`.
* `main.py` contiene la construcción completa del grafo desde `START` hasta `END`, y nada de lógica de negocio.
* Los nodos se implementan en `nodes/`.
* Las herramientas del agente (las 4 del contrato) en `tools/`.
* Los subagentes LLM especializados (identificador, interpretador, recepcionista) en `agents/`.
* Los servicios e integraciones (LLM OpenAI/OpenCode, embeddings, Redis, búsqueda, simulador, ingesta) en `services/`.
* Los prompts se mantienen separados del código, en `prompts/{nodo}_prompt.py` — un archivo por cada
  llamada al LLM. Los bloques de seguridad compartidos viven en `prompts/seguridad.py`.
* Las configuraciones se centralizan en `config.py`.
* Las credenciales (OpenAI, OpenCode, Redis y, si aplica, el buscador en vivo) viven en el `.env` de la raíz.
  **`config.py` es el único archivo que lee variables de entorno.**
* Los datos de prueba son archivos versionados en `data/`; **nada se genera durante la ejecución** del
  agente ni del notebook.

## Integraciones

Las credenciales se obtienen del `.env` existente. Nunca exponer, imprimir ni escribir credenciales
directamente en el código, en los logs ni en los prompts.

No modificar el `.env` sin autorización.

No inventar imports ni clases. Si no hay certeza de que un símbolo existe en la versión instalada,
verificarlo antes de usarlo.

## Desarrollo

Priorizar código modular, simple, mantenible y ejecutable. Sin sobreingeniería.

# Agentes

| Agente | Qué hace | ¿Edita código? |
|---|---|---|
| `implementator` | Construye y corrige `cotizador-examenes/` | **Sí** — es el único |
| `test-code` | Ejecuta el agente y comprueba que funciona | No |
| `validator` | Golden set + pruebas de seguridad; mide si el agente acierta | No (solo `validacion/`) |
| `review` | Revisa calidad, seguridad y arquitectura del código | No |
| `notebook` | Genera el notebook de entrega del agente | No (solo `notebooks/`) |

Solo el `implementator` toca el código del agente. Los demás reportan, y sus hallazgos se aplican
**siempre** a través de él.

# Plan de trabajo

El proyecto **no se construye de una sola vez**. Se construye por pasos, uno por invocación, siguiendo
`plan.json` en la raíz del repositorio.

`plan.json` es la fuente de verdad de qué está hecho y qué falta. Cada paso tiene un único campo
mutable, `estado`, con **solo dos valores**: `pendiente` o `hecho`.

```
01-estructura-base         proyecto, config, estado y dependencias
02-datos-simulador         PDFs, web snapshot, eventos, escenarios y ciudades (F1)
03-grafo-minimo            router + respuesta directa + consolidación (ya ejecutable)
04-ingesta-simulador       Redis/RAG, llamada simulada, eventos e interpretación (F2)
05-react-herramientas      las 4 herramientas + ciclo ReAct + parada y tope (F3)
06-seguridad-privacidad    bloques, datos personales, contenido externo, síntomas
07-verificador             verificador de salida sobre reporte y texto (F5)
08-historial               checkpointer y reutilización entre turnos (RF-47)
09-robustez                casos límite y manejo de errores
10-documentacion           README y ficha final
11-validacion-golden-set   (validator) golden set G01–G16 + S1–S6 + dos corridas
12-notebook-estudio        (notebook) notebook de entrega (prueba multi-turno)
```

## Reglas del plan

* **Un paso por invocación.** El agente hace el paso, lo verifica, lo marca `hecho` y **para**.
* Un paso solo se marca `hecho` si **su verificación pasó de verdad**, ejecutada. Un plan que miente no sirve.
* Cada paso deja el proyecto **ejecutable**. Nunca a medias.
* Solo el agente dueño de un paso cambia su `estado`. Nadie toca los pasos de otro.
* Nadie reescribe el plan. Si falta un paso o el orden está mal, se le dice al usuario y él decide.
* Tras editar `plan.json`, validar que sigue siendo JSON correcto.

## Cómo ejecutarlo

Invocas al `implementator` una vez por paso:

```
@implementator                    → hace el primer paso pendiente
@implementator 05-react-herramientas   → hace ese paso concreto
```

Después de cada paso, si quieres comprobarlo: `@test-code`. Solo prueba lo que ya está `hecho`; lo
pendiente lo marca `N/A`, no como fallo.

Cuando el paso `10-documentacion` esté hecho, se desbloquean `@validator` y `@notebook`.

## Ciclo recomendado por paso

1. `@implementator` — hace el siguiente paso pendiente y lo marca `hecho`.
2. `@test-code` — confirma que lo construido funciona y que no rompió lo anterior.
3. Si falla, `test-code` llama al `implementator` con el error literal (máx. 3 ciclos).
4. Repite hasta agotar los pasos del `implementator`.
5. `@validator` — golden set G01–G16 y pruebas S1–S6: ¿acierta el router? ¿usa las herramientas correctas?
6. `@review` — calidad, seguridad y arquitectura. Los hallazgos **Bloqueantes** vuelven al `implementator`.
7. `@notebook` — genera el notebook de entrega con el código ya final.

`test-code` responde *¿funciona?*, el `validator` responde *¿lo hace bien?*, y el `notebook` va al final
para documentar el código tal como quedó.

## Flujo de validación

El `validator` es el circuito de calidad (paso `11`) y vive en `cotizador-examenes/validacion/`:

* `golden_set.json` — casos G01–G16, cada uno referenciando un escenario, con solo los campos que se
  comparan (ver `spec.md` §7.2). **Es un banco estable: no se regenera entre ejecuciones**, para poder
  comparar una corrida con la siguiente.
* `seguridad.json` — pruebas S1–S6 (ver `spec.md` §7.4).
* `run_golden.py` — pasa los casos por el agente, captura el **paso a paso** de cada uno
  (`astream` con `stream_mode="updates"`) y compara contra el `esperado`.
* `run_seguridad.py` — ejecuta S1–S6 y verifica límites, argumentos y transcripción.
* `resultados_{fecha}.{json,xlsx}` — informe por campo y por dimensión, con las hojas `Detalle`,
  `Resumen` y `Fallos`.

Para que esto funcione, `main.py` debe exponer el grafo compilado como símbolo importable; el bucle de
consola vive dentro de `if __name__ == "__main__":`.
