# Placeholders de la plantilla

Este directorio es una **plantilla de agente**. Todos los archivos están escritos
con la lógica completa (agentes, plan por pasos, grafo, integraciones, validación
y notebook), pero cada dato propio de un problema concreto fue reemplazado por un
**placeholder** escrito entre doble llave, del estilo `{{PROJECT_NAME}}`.

## Cómo se usa

1. Copia este directorio al proyecto nuevo.
2. Reemplaza **todos** los placeholders por los valores del problema.
3. Elimina los bloques que no apliquen (por ejemplo, el MCP si el proyecto no lo usa)
   y sus variables asociadas.
4. Empieza a invocar al `implementator`, un paso por invocación.

Para verificar que no quedó ninguno sin resolver:

```bash
grep -rn '{{' . --include='*.md' --include='*.json' --include='*.example' \
  | grep -v 'placeholder.md'
```

## Placeholders por grupo

### Proyecto

| Placeholder | Descripción | Ejemplo |
|---|---|---|
| `{{PROJECT_NAME}}` | Nombre legible del agente | `Nombre del agente` |
| `{{PROJECT_DIR}}` | Directorio base, con barra final | `nombre-del-agente/` |
| `{{DOMAIN}}` | Dominio o tema que resuelve el agente | `tema del agente` |
| `{{INPUT_DESCRIPTION}}` | Qué recibe el agente | `texto del usuario` |
| `{{OUTPUT_DESCRIPTION}}` | Qué entrega el agente | `respuesta del agente, o el archivo de la rama de salida` |
| `{{INTEGRATIONS_SUMMARY}}` | Resumen corto de las integraciones usadas | `MCP + API REST + archivo de salida` |

### Stack y LLM

| Placeholder | Descripción | Ejemplo |
|---|---|---|
| `{{PYTHON_VERSION}}` | Versión de Python del proyecto | `3.12` |
| `{{LLM_PROVIDER}}` | Proveedor del modelo | `Proveedor del modelo` |
| `{{LLM_PACKAGE}}` | Paquete de LangChain del proveedor | `paquete-langchain-del-proveedor` |
| `{{LLM_CLASS}}` | Clase del modelo | `ClaseDelModelo` |
| `{{LLM_API_KEY_ENV}}` | Variable de entorno de la credencial | `PROVEEDOR_API_KEY` |
| `{{LLM_MODEL_ENV}}` | Variable de entorno del id del modelo | `PROVEEDOR_MODEL` |
| `{{HTTP_CLIENT}}` | Cliente HTTP del proyecto | `httpx` |
| `{{SUBAGENT_MODEL}}` | Modelo de los subagentes de OpenCode | `proveedor/modelo` |
| `{{SUBAGENT_STEPS_IMPLEMENTATOR}}` | Presupuesto de pasos del `implementator` | `120` |
| `{{SUBAGENT_STEPS_TEST}}` | Presupuesto de pasos de `test-code` | `60` |
| `{{SUBAGENT_STEPS_VALIDATOR}}` | Presupuesto de pasos de `validator` | `80` |
| `{{SUBAGENT_STEPS_REVIEW}}` | Presupuesto de pasos de `review` | `40` |
| `{{SUBAGENT_STEPS_NOTEBOOK}}` | Presupuesto de pasos de `notebook` | `60` |

### Grafo

| Placeholder | Descripción | Ejemplo |
|---|---|---|
| `{{N_BRANCHES}}` | Número de ramas del router | `4` |
| `{{BRANCHES_TABLE}}` | Bloque: tabla de ramas (ver más abajo) | — |
| `{{BRANCHES_FLOW}}` | Bloque: árbol del flujo (ver más abajo) | — |
| `{{BRANCHES_SAMPLES}}` | Bloque: una entrada de ejemplo por rama | — |

### MCP (si aplica)

| Placeholder | Descripción | Ejemplo |
|---|---|---|
| `{{MCP_SERVER_NAME}}` | Nombre del servidor MCP | `nombre-del-servidor` |
| `{{MCP_URL_ENV}}` | Variable de entorno de la URL del MCP | `MCP_URL` |
| `{{MCP_TRANSPORT}}` | Transporte del MCP | `streamable_http` |
| `{{MCP_PACKAGE}}` | Paquete cliente del MCP | `paquete-cliente-mcp` |
| `{{MCP_TOOLS}}` | Herramientas que expone el servidor | `herramienta_1, herramienta_2, ...` |
| `{{MCP_DISCOVERY_STEP}}` | Primer paso recomendado por el servidor para descubrir recursos | `listar_recursos` |

### API REST (si aplica)

| Placeholder | Descripción | Ejemplo |
|---|---|---|
| `{{API_NAME}}` | Nombre de la API | `nombre-de-la-api` |
| `{{API_BASE_URL}}` | URL base | `https://api.ejemplo/v1` |
| `{{API_ENDPOINTS}}` | Endpoints que consume la rama | `GET /recurso/{id}` |
| `{{API_AUTH}}` | Tipo de autenticación | `ninguna` |
| `{{API_HEADERS}}` | Cabeceras requeridas | `accept: application/json` |

### Rama de salida (si aplica)

| Placeholder | Descripción | Ejemplo |
|---|---|---|
| `{{OUTPUT_DIR}}` | Carpeta donde se guarda el archivo generado | `salidas/` |
| `{{OUTPUT_BRANCH}}` | Etiqueta de la rama que genera el archivo | `rama-de-salida` |
| `{{OUTPUT_ARTIFACT}}` | Qué archivo genera la rama, en términos generales | `un archivo generado por la rama de salida` |

### Debug

| Placeholder | Descripción | Ejemplo |
|---|---|---|
| `{{DEBUG_ENV_VAR}}` | Variable de entorno que activa el modo debug | `DEBUG` |
| `{{DEBUG_FLAG}}` | Flag de línea de comandos equivalente | `--debug` |

### Validación

| Placeholder | Descripción | Ejemplo |
|---|---|---|
| `{{VALIDATION_SIZE}}` | Tamaño del banco estable de preguntas | `50` |
| `{{VALIDATION_DISTRIBUTION}}` | Reparto del banco entre ramas | `12/13/13/12` |

### Plan

| Placeholder | Descripción | Ejemplo |
|---|---|---|
| `{{PLAN_STEPS_SUMMARY}}` | Bloque: resumen de los pasos del plan | — |
| `{{PLAN_NOTES}}` | Nota libre sobre el plan | `Plantilla: conserva solo los pasos de integración que el problema necesite` |
| `{{INTEGRATION_API_NOMBRE}}` | Nombre del paso de integración con API REST | `Añadir la API REST` |
| `{{INTEGRATION_MCP_NOMBRE}}` | Nombre del paso de integración con MCP | `Añadir el MCP` |
| `{{INTEGRATION_SALIDA_NOMBRE}}` | Nombre del paso de la rama de salida | `Añadir el archivo de salida` |

## Bloques que se expanden

Estos placeholders no son una palabra: se reemplazan por un fragmento completo.

### `{{BRANCHES_TABLE}}`

Tabla markdown con una fila por rama. La rama `conversacional` no usa integraciones;
las demás indican cuáles usan.

```markdown
| rama | descripción | integraciones |
|---|---|---|
| <etiqueta-1> | <qué hace> | ninguna |
| <etiqueta-2> | <qué hace> | MCP |
| <etiqueta-3> | <qué hace> | API REST |
| <etiqueta-N> | <qué hace> | MCP + API REST + archivo de salida |
```

### `{{BRANCHES_FLOW}}`

Árbol de texto del grafo, con las ramas numeradas.

```text
1. Input usuario
2. Router (clasifica la intención en una de estas <N_BRANCHES>)
   2.1 <etiqueta-1>
   2.2 <etiqueta-2>
   ...
3. Consolidar respuestas y formatearlas con el LLM
4. Retornar respuesta al usuario
```

### `{{BRANCHES_SAMPLES}}`

Tabla con **una entrada representativa por rama**, usada por `test-code`, `validator`
y `notebook`.

```markdown
| rama | entrada representativa |
|---|---|
| <etiqueta-1> | "<entrada>" |
| <etiqueta-2> | "<entrada>" |
```

### `{{PLAN_STEPS_SUMMARY}}`

Listado en bloque de código de los pasos del plan, con su id y su propósito.

```text
01-estructura-base        crear el proyecto y las carpetas
02-grafo-minimo           router + rama conversacional (ya ejecutable)
03-modo-debug             trazas
04-integracion-api        ramas que usan la API REST
05-integracion-mcp        ramas que usan el MCP
06-integracion-salida     rama que genera el archivo de salida
07-retirar-placeholder    cerrar el grafo con las ramas reales
08-robustez               casos límite
09-documentacion          README final
10-validacion             (validator)
11-notebook-estudio       (notebook)
```

## Reglas

* No dejes ningún placeholder sin resolver en el proyecto final.
* Si el problema no usa MCP, API o archivo de salida, **elimina** el paso del plan,
  la variable del `.env.example` y el bloque correspondiente; no lo dejes vacío.
* Mantén el nombre del placeholder tal cual (mayúsculas y guiones bajos) para poder
  encontrarlos con `grep`.
* Los archivos `opencode.json`, `opencode.docs` y `opencode/examples/implementator.md`
  son genéricos: no contienen placeholders.
