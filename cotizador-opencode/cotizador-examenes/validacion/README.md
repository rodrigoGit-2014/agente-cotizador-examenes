# Evidencia de validación

Corrida ejecutada con el `.venv` del proyecto y el Redis del curso, posterior a los ajustes de
estabilidad (precio determinista, validación de hora, verificador y prompt de identificación).

## Banco de pruebas

- `golden_set.json` — 16 casos (G01–G16) con expectativa por campo. Es un **banco estable**: no se
  regenera entre corridas.
- `seguridad.json` — 6 pruebas (S1–S6).
- `run_golden.py` / `run_seguridad.py` — arneses reproducibles; capturan el paso a paso del grafo.

## Informes versionados

| Informe | Corrida | Resultado |
|---|---|---|
| `resultados_20261006-112407.xlsx` | previa (antes del ajuste del prompt de identificación) | 15/16 (falló G05) |
| `resultados_20261006-120838.xlsx` | **final** | **16/16** |
| `seguridad_20261006-121332.xlsx` | **final** | **6/6** |

La corrida final del golden set no tiene fallos; la corrida previa se conserva como evidencia del
ciclo corregir → reejecutar.

## Cómo repetirlo

```bash
python validacion/run_golden.py     # -> validacion/resultados_{fecha}.xlsx
python validacion/run_seguridad.py  # -> validacion/seguridad_{fecha}.xlsx
```
