"""Prompt generador de documentos de centro (`spec.md` §5.9, DA-08).

Define el formato de los documentos de centro y, sobre todo, el **contrato de títulos
fijos** que la ingesta usa para extraer la lista de exámenes por código.

No se ejecuta durante el agente ni el notebook: es una herramienta de desarrollo.
"""

from __future__ import annotations

CONTRATO_TITULOS = """\
Examen: <nombre del examen> | Código: <código interno del centro>
Descripción: <qué es el examen, en una o dos frases>
Propósito: <para qué sirve; debe permitir distinguirlo de otros exámenes con el mismo nombre>
Preparación: <indicaciones para el paciente; si no hay, indicarlo>
Requisitos: <orden médica u otros requisitos>
Precio: <valor informado, particular; puede ser cerrado, un rango o referencial>
Horario de atención: <días y bloque en que se realiza el examen>
Anticipación mínima: <días hábiles mínimos desde la solicitud>"""

PLANTILLA = """\
Redacta el documento público de un centro médico ficticio para un banco de pruebas.
Todo es simulado: no uses datos reales de pacientes ni precios que puedan tomarse como vigentes.

Parámetros:
- Centro: {nombre_centro}
- Especialidad: {especialidad}
- Ciudad: {ciudad} (comuna de {comuna})
- Dirección: {direccion}
- Teléfono (público, ficticio): {telefono}
- Exámenes que ofrece: {examenes}

El documento debe tener tres secciones:

1. Información general: a qué se dedica el centro, dirección, teléfono y horario de atención.
2. Políticas del centro: cómo atiende por teléfono (por ejemplo, si pregunta la previsión antes
   de dar el precio), qué requisitos exige y qué no realiza. Las políticas definen el
   comportamiento de la recepcionista y NO se configuran por escenario.
3. Catálogo de exámenes. Cada examen DEBE empezar con una línea con EXACTAMENTE este formato
   (la ingesta extrae la lista de exámenes por código a partir de estos títulos fijos):

{contrato}

Reglas:
- Escribe los precios con cifras (por ejemplo, $45.000), nunca en palabras.
- Usa un identificador distinto por examen dentro del centro; centros distintos pueden usar
  códigos y nombres distintos para el mismo examen.
- El propósito debe distinguir exámenes que se llaman igual pero sirven para cosas distintas.
- Incluye al inicio, en una línea aparte, el aviso: "Datos simulados — documento ficticio".
- No contradigas entre secciones (por ejemplo, no anuncies un examen y luego digas que no se realiza).
"""


def construir_prompt(
    *,
    nombre_centro: str,
    especialidad: str,
    ciudad: str,
    comuna: str,
    direccion: str,
    telefono: str,
    examenes: str,
    con_contrato: bool = True,
) -> str:
    """Devuelve el prompt listo para pedirle el documento a un LLM."""
    texto_contrato = CONTRATO_TITULOS if con_contrato else "(sin contrato de títulos)"
    return PLANTILLA.format(
        nombre_centro=nombre_centro,
        especialidad=especialidad,
        ciudad=ciudad,
        comuna=comuna,
        direccion=direccion,
        telefono=telefono,
        examenes=examenes,
        contrato=texto_contrato,
    )
