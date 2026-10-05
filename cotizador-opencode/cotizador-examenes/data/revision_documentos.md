# Revisión manual de los documentos de centro (A1) y de la unión búsqueda ↔ documento (A2)

Los documentos de `data/documentos/` son ficticios (DA-05, [P-10]). Antes de la ingesta se
revisan a mano con esta lista de chequeo. Estado: **aprobado**.

## Lista de chequeo por documento (A1)

| Centro | Archivo | Información general | Políticas sin contradicción | Contrato de títulos | Precios y requisitos | Aviso de datos simulados | Resultado |
|---|---|---|---|---|---|---|---|
| Centro Oftalmológico MiVisión | `centro-oftalmologico-mivision.pdf` | OK | OK | OK (GLA-A1, FO-A1, CV-A1) | OK | OK | Aprobado |
| Clínica Oftalmológica Talca | `clinica-oftalmologica-talca.pdf` | OK | OK | OK (GLA-B2, FO-B2, CV-B2) | OK | OK | Aprobado |
| Óptica y Oftalmología Maule | `optica-oftalmologia-maule.pdf` | OK | OK | OK (FO-C1, REF-C1) | OK | OK | Aprobado |
| Centro de Especialidades Visuales Lircay | `centro-especialidades-visuales-lircay.pdf` | OK | OK | OK (INT-E1) | OK | OK | Aprobado |

Notas de la revisión:

* **Contrato de títulos:** cada examen comienza con `Examen: <nombre> | Código: <código>` seguido de
  `Descripción:`, `Propósito:`, `Preparación:`, `Requisitos:`, `Precio:` (y luego `Horario de atención:`
  y `Anticipación mínima:`, que la ingesta puede ignorar). Verificado en los cuatro documentos.
* **Mismo nombre, distinto propósito:** `Curvimetría` en MiVisión mide la **graduación** (CV-A1) y en
  Clínica Talca mide la **curvatura de la córnea** (CV-B2). Los propósitos los distinguen, como exige
  RF-11 y el caso G12.
* **No contradicciones:** MiVisión anuncia presión ocular, fondo de ojo y curvimetría, y los realiza.
  Óptica Maule declara explícitamente que **no** realiza controles de glaucoma ni tonometría.
* **Lircay** ofrece una evaluación integral ambigua a propósito (candidata al veredicto `dudoso`, G13).

## Unión búsqueda ↔ documento por teléfono (A2)

El `centro_id` es el teléfono normalizado (solo dígitos, con código de país). Debe coincidir entre la
instantánea de búsqueda y el documento, o el centro "no contesta" sin motivo real.

| Centro | Teléfono (documento) | Teléfono (instantánea) | `centro_id` | Coincide |
|---|---|---|---|---|
| Centro Oftalmológico MiVisión | +56 71 222 1111 | +56 71 222 1111 | 56712221111 | Sí |
| Clínica Oftalmológica Talca | +56 71 223 2222 | +56 71 223 2222 | 56712232222 | Sí |
| Óptica y Oftalmología Maule | +56 71 224 3333 | +56 71 224 3333 | 56712243333 | Sí |
| Centro de Especialidades Visuales Lircay | +56 71 225 4444 | +56 71 225 4444 | 56712254444 | Sí |
| Centro Visual Norte (sin documento) | — | +56 71 226 5555 | 56712265555 | N/A (no contesta, RF-38) |

Los teléfonos son ficticios y se verifican solo por consistencia interna; no se contrastan con fuentes
públicas reales para no asociar precios y agendas inventados a una clínica real (C10).
