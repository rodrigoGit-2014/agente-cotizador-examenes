# Arquitectura del proyecto

Este proyecto desarrolla agentes de inteligencia artificial utilizando Python, LangGraph y LangChain.

El proyecto activo es **`agente-colombia/`** (agente de turismo colombiano). Su especificación completa — flujo del router, integraciones y estructura de carpetas — vive en `opencode/agents/implementator.md` y es la fuente de verdad. Este archivo solo recoge las reglas que aplican a cualquier agente de este repositorio.

## Inicio

**Detecta primero el sistema operativo** y usa el intérprete que corresponda. No asumas ninguno de los dos: en macOS/Linux `python.exe` no existe, y en Windows `python3` puede no estar en el PATH.

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

Una vez creado el entorno, el intérprete del proyecto es `.venv/bin/python` en macOS/Linux y `.venv\Scripts\python.exe` en Windows. Usa siempre ese, no el del sistema, para instalar y ejecutar.

Equivalencias rápidas:

| | macOS / Linux | Windows |
|---|---|---|
| Intérprete del sistema | `python3` | `python.exe` |
| Activar el entorno | `source .venv/bin/activate` | `.venv\Scripts\activate` |
| Intérprete del entorno | `.venv/bin/python` | `.venv\Scripts\python.exe` |
| Separador de rutas | `/` | `\` (usa `pathlib.Path` en el código para no depender de esto) |

## Reglas obligatorias

* Directorio base del proyecto: `agente-colombia/`.
* `main.py` contiene la construcción completa del grafo desde `START` hasta `END`, y nada de lógica de negocio.
* Los nodos se implementan en `nodes/`.
* Las herramientas en `tools/`.
* Los agentes especializados en `agents/`.
* Los servicios y APIs en `services/`.
* Los prompts se mantienen separados del código, en `prompts/{nodo}_prompt.py` — un archivo por cada nodo que use el LLM.
* Las configuraciones se centralizan en `config.py`.
* Las credenciales de APIs y MCPs viven en el `.env` de la raíz. **`config.py` es el único archivo que lee variables de entorno.**

## Integraciones

Las credenciales se obtienen del `.env` existente. Nunca exponer, imprimir ni escribir credenciales directamente en el código, en los logs ni en los prompts.

No modificar el `.env` sin autorización.

No inventar imports ni clases. Si no hay certeza de que un símbolo existe en la versión instalada, verificarlo antes de usarlo.

## Desarrollo

Priorizar código modular, simple, mantenible y ejecutable. Sin sobreingeniería.

# Agentes

| Agente | Qué hace | ¿Edita código? |
|---|---|---|
| `implementator` | Construye y corrige `agente-colombia/` | **Sí** — es el único |
| `test-code` | Ejecuta el agente y comprueba que funciona | No |
| `validator` | Banco de 50 preguntas + harness; mide si el agente acierta | No (solo `validacion/`) |
| `review` | Revisa calidad, seguridad y arquitectura del código | No |
| `notebook` | Genera el notebook para estudiar el agente paso a paso | No (solo `notebooks/`) |

Solo el `implementator` toca el código del agente. Los demás reportan, y sus hallazgos se aplican **siempre** a través de él.

# Plan de trabajo

El proyecto **no se construye de una sola vez**. Se construye por pasos, uno por invocación, siguiendo `plan.json` en la raíz del repositorio.

`plan.json` es la fuente de verdad de qué está hecho y qué falta. Cada paso tiene un único campo mutable, `estado`, con **solo dos valores**: `pendiente` o `hecho`.

```
01-estructura-base        crear el proyecto y las carpetas
02-grafo-minimo           router + conversacional (ya ejecutable)
03-modo-debug             trazas
04-api-ciudades           rama 2.3
05-mcp-informacion        rama 2.2
06-itinerario-excel       rama 2.4
07-retirar-placeholder    cerrar el grafo con las 4 ramas reales
08-robustez               casos límite
09-documentacion          README final
10-validacion-50-preguntas  (validator)
11-notebook-estudio         (notebook)
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
@implementator          → hace el primer paso pendiente
@implementator 04-api-ciudades   → hace ese paso concreto
```

Después de cada paso, si quieres comprobarlo: `@test-code`. Solo prueba lo que ya está `hecho`; lo pendiente lo marca `N/A`, no como fallo.

Cuando el paso `09-documentacion` esté hecho, se desbloquean `@validator` y `@notebook`.

## Ciclo recomendado por paso

1. `@implementator` — hace el siguiente paso pendiente y lo marca `hecho`.
2. `@test-code` — confirma que lo construido funciona y que no rompió lo anterior.
3. Si falla, `test-code` llama al `implementator` con el error literal (máx. 3 ciclos).
4. Repite hasta agotar los pasos del `implementator`.
5. `@validator` — las 50 preguntas: ¿acierta el router? ¿consulta MCP y API cuando toca?
6. `@review` — calidad, seguridad y arquitectura. Los hallazgos **Bloqueantes** vuelven al `implementator`.
7. `@notebook` — genera el notebook de estudio con el código ya final.

`test-code` responde *¿funciona?*, el `validator` responde *¿lo hace bien?*, y el `notebook` va al final para documentar el código tal como quedó.

## Flujo de validación

El `validator` es el circuito de calidad (paso `10`) y vive en `agente-colombia/validacion/`:

* `preguntas.xlsx` — 50 preguntas repartidas entre las 4 ramas del router, con la rama esperada y si debe pasar por MCP, API y/o generar Excel. **Es un banco estable: no se regenera entre ejecuciones**, para poder comparar una corrida con la siguiente.
* `run_validacion.py` — pasa las 50 por el agente y captura el **paso a paso** de cada una (`astream` con `stream_mode="updates"`), no solo la respuesta final.
* `resultados_{fecha}.xlsx` — informe con hojas `Detalle`, `Resumen` y `Fallos`.

Para que esto funcione, `main.py` debe exponer el grafo compilado como símbolo importable; el bucle de consola vive dentro de `if __name__ == "__main__":`.
