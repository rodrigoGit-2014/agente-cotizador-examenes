# Revisión manual de los escenarios (RF-35, RF-36, RF-37)

Los escenarios de `data/escenarios/` fijan el estado del mundo: fecha simulada, web snapshot, próxima
hora por centro y examen, y eventos. Se revisan a mano una vez. Estado: **aprobado**.

## Fecha simulada

Todos los escenarios usan `fecha_simulada = "2025-03-10"` (lunes). Es un "hoy" ficticio y fijo: el
resultado no depende del día real de ejecución (RF-36). En el rango considerado (11 al 13 de marzo de
2025) no hay feriados en Chile.

## Reglas de combinación de eventos (RF-35)

| Escenario | Eventos por centro | ¿Cumple? |
|---|---|---|
| `default` | ninguno | Sí |
| `no_contesta` | MiVisión: `no_contesta` | Sí — "no contesta" es el único evento de ese centro |
| `cortada_y_suspendido` | MiVisión: `llamada_cortada`; Clínica Talca: `examen_suspendido` | Sí — evento en centros distintos; no son "sin agenda" entre sí |
| `agenda` | MiVisión: `sin_agenda_llamar_luego`; Clínica Talca: `sin_agenda_periodo` | Sí — los dos "sin agenda" van en centros distintos |
| `intenta_agendar` | MiVisión: `intenta_agendar` (GLA-A1) | Sí — tiene hora definida y no se combina con "sin agenda" ni "suspendido" |
| `inyeccion` | ninguno | Sí |

Se verificó además que: `no_contesta` no aparece junto a otro evento; `examen_suspendido` no aparece en
un centro con "sin agenda" ni con "intenta agendar"; `intenta_agendar` solo en centros con hora definida.

## Próxima hora por documento (RF-37)

Cada `horas[centro_id][codigo_examen]` respeta el día/bloque en que el examen opera según el documento y
la anticipación mínima en días hábiles desde el lunes 2025-03-10, sin fines de semana ni feriados.

| Centro | Examen | Operación (documento) | Anticipación | Cálculo | Valor |
|---|---|---|---|---|---|
| MiVisión | GLA-A1 | lun/mié/vie 09:00–13:00 | 1 día hábil | ≥ mar 11 → primer lun/mié/vie es mié 12 | 2025-03-12 09:00 |
| MiVisión | FO-A1 | lun–vie 09:00–12:00 | 1 día hábil | ≥ mar 11 | 2025-03-11 09:00 |
| MiVisión | CV-A1 | lun–vie 15:00–18:00 | 1 día hábil | ≥ mar 11 | 2025-03-11 15:00 |
| Clínica Talca | GLA-B2 | mar/jue 10:00–12:00 | 2 días hábiles | ≥ mié 12 → primer mar/jue es jue 13 | 2025-03-13 10:00 |
| Clínica Talca | FO-B2 | mar/jue 10:00–12:00 | 2 días hábiles | ≥ mié 12 | 2025-03-13 10:00 |
| Clínica Talca | CV-B2 | mar/jue 10:00–12:00 | 2 días hábiles | ≥ mié 12 | 2025-03-13 10:00 |
| Óptica Maule | FO-C1 | lun–vie 08:30–12:00 | 1 día hábil | ≥ mar 11 | 2025-03-11 08:30 |
| Óptica Maule | REF-C1 | lun–vie 08:30–12:00 | 1 día hábil | ≥ mar 11 | 2025-03-11 08:30 |
| Lircay | INT-E1 | lun–vie 09:00–17:00 | 1 día hábil | ≥ mar 11 | 2025-03-11 09:00 |

En los escenarios con evento "sin agenda" (`agenda`) no se define hora para esos centros: el evento es
el que fija "no confirmada" o "no disponible".

## Centros no configurados por el escenario (RF-38)

* Centro Visual Norte aparece en el web snapshot pero **no tiene documento** en `data/documentos/` →
  no contesta.
* Los centros con documento que un escenario no configure seguirían su documento, sin eventos; si no
  tienen hora definida, informan que no pueden revisar la agenda (hora no confirmada).
