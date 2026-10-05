"""Contenido de los documentos de centro de prueba (Talca, oftalmología).

En el flujo real, este contenido lo produce un LLM guiado por
`prompts/prompt_generador_centro_examenes.py` y se revisa a mano (`data/revision_documentos.md`).
Aquí se deja escrito y versionado para que el banco de pruebas sea reproducible sin depender
de ninguna llamada al LLM.

Todos los centros son ficticios (DA-05, [P-10]). El `centro_id` es el teléfono normalizado
(solo dígitos, con código de país) y debe coincidir con el del web snapshot de búsqueda.
"""

from __future__ import annotations

CENTROS = [
    {
        "centro_id": "56712221111",
        "archivo": "centro-oftalmologico-mivision.pdf",
        "nombre": "Centro Oftalmológico MiVisión",
        "especialidad": "Oftalmología",
        "ciudad": "Talca",
        "comuna": "Talca",
        "direccion": "Av. San Miguel 1234, Talca",
        "telefono": "+56 71 222 1111",
        "informacion_general": (
            "Centro oftalmológico dedicado al diagnóstico y control de enfermedades de la visión. "
            "Cuenta con tecnólogos médicos y médicos oftalmólogos. "
            "Horario de atención: lunes a viernes de 09:00 a 18:00; sábado de 09:00 a 13:00."
        ),
        "politicas": [
            "Para informar un precio por teléfono, se pregunta primero si la atención es particular, "
            "Fonasa o Isapre.",
            "Los exámenes se realizan con orden médica vigente; la orden puede ser de otro profesional.",
            "Los valores informados corresponden a atención particular; el copago depende de la "
            "previsión del paciente.",
            "El centro no realiza cirugías ni entregas de lentes.",
        ],
        "examenes": [
            {
                "codigo": "GLA-A1",
                "nombre": "Medición de la presión intraocular",
                "descripcion": "Examen que mide la presión dentro del ojo mediante tonómetro de contacto.",
                "proposito": "Controlar y vigilar a pacientes con sospecha o diagnóstico de glaucoma.",
                "preparacion": "No requiere preparación. No suspender las gotas indicadas por su médico.",
                "requisitos": "Orden médica.",
                "precio": "$45.000",
                "horario": "lunes, miércoles y viernes, 09:00 a 13:00",
                "anticipacion": "1 día hábil",
            },
            {
                "codigo": "FO-A1",
                "nombre": "Fondo de ojo",
                "descripcion": (
                    "Examen que permite observar la retina y el nervio óptico con dilatación de la pupila."
                ),
                "proposito": "Evaluar la salud de la retina y del nervio óptico.",
                "preparacion": (
                    "Se dilata la pupila; se recomienda asistir con acompañante y no conducir después "
                    "del examen. Duración aproximada: 20 minutos."
                ),
                "requisitos": "Orden médica.",
                "precio": "$35.000",
                "horario": "lunes a viernes, 09:00 a 12:00",
                "anticipacion": "1 día hábil",
            },
            {
                "codigo": "CV-A1",
                "nombre": "Curvimetría",
                "descripcion": (
                    "Medición de la graduación (refracción) del ojo para determinar la receta de lentes."
                ),
                "proposito": (
                    "Determinar la graduación para la confección o actualización de lentes ópticos."
                ),
                "preparacion": "Se recomienda no usar lentes de contacto el día del examen.",
                "requisitos": "No requiere orden médica.",
                "precio": "$25.000",
                "horario": "lunes a viernes, 15:00 a 18:00",
                "anticipacion": "1 día hábil",
            },
        ],
    },
    {
        "centro_id": "56712232222",
        "archivo": "clinica-oftalmologica-talca.pdf",
        "nombre": "Clínica Oftalmológica Talca",
        "especialidad": "Oftalmología",
        "ciudad": "Talca",
        "comuna": "Talca",
        "direccion": "Calle 1 Sur 567, Talca",
        "telefono": "+56 71 223 2222",
        "informacion_general": (
            "Clínica de especialidad oftalmológica. Los exámenes se agendan por teléfono. "
            "Horario de atención: lunes a viernes de 10:00 a 19:00."
        ),
        "politicas": [
            "Todos los exámenes requieren orden médica vigente.",
            "El precio informado es de atención particular; para Fonasa e Isapre el valor se "
            "confirma en caja.",
            "No se realizan exámenes sin orden médica.",
        ],
        "examenes": [
            {
                "codigo": "GLA-B2",
                "nombre": "Tonometría de aplanación",
                "descripcion": "Medición de la presión intraocular con tonómetro de aplanación.",
                "proposito": (
                    "Pesquisar y controlar el glaucoma mediante la medición de la presión del ojo."
                ),
                "preparacion": "No requiere preparación.",
                "requisitos": "Orden médica.",
                "precio": "$42.000",
                "horario": "martes y jueves, 10:00 a 12:00",
                "anticipacion": "2 días hábiles",
            },
            {
                "codigo": "FO-B2",
                "nombre": "Fondo de ojo",
                "descripcion": "Observación del fondo del ojo con dilatación pupilar.",
                "proposito": "Evaluar la retina y el nervio óptico.",
                "preparacion": (
                    "Se dilata la pupila; se sugiere asistir con acompañante y no conducir después."
                ),
                "requisitos": "Orden médica.",
                "precio": "$38.000",
                "horario": "martes y jueves, 10:00 a 12:00",
                "anticipacion": "2 días hábiles",
            },
            {
                "codigo": "CV-B2",
                "nombre": "Curvimetría",
                "descripcion": "Medición de la curvatura de la córnea (queratometría).",
                "proposito": (
                    "Evaluar la curvatura corneal para la adaptación de lentes de contacto."
                ),
                "preparacion": "No usar lentes de contacto durante las 24 horas previas.",
                "requisitos": "Orden médica.",
                "precio": "$30.000",
                "horario": "martes y jueves, 10:00 a 12:00",
                "anticipacion": "2 días hábiles",
            },
        ],
    },
    {
        "centro_id": "56712243333",
        "archivo": "optica-oftalmologia-maule.pdf",
        "nombre": "Óptica y Oftalmología Maule",
        "especialidad": "Oftalmología",
        "ciudad": "Talca",
        "comuna": "Talca",
        "direccion": "2 Norte 890, Talca",
        "telefono": "+56 71 224 3333",
        "informacion_general": (
            "Óptica con servicio de exámenes oftalmológicos básicos. "
            "Horario de atención: lunes a viernes de 08:30 a 18:00."
        ),
        "politicas": [
            "No se realizan controles de glaucoma ni tonometría.",
            "Los exámenes se realizan con o sin orden médica; el precio informado es particular.",
        ],
        "examenes": [
            {
                "codigo": "FO-C1",
                "nombre": "Examen de fondo de ojo",
                "descripcion": "Observación de la retina y del nervio óptico.",
                "proposito": "Observar la retina y el nervio óptico.",
                "preparacion": "No requiere preparación ni acompañante.",
                "requisitos": "No requiere orden médica.",
                "precio": "$28.000",
                "horario": "lunes a viernes, 08:30 a 12:00",
                "anticipacion": "1 día hábil",
            },
            {
                "codigo": "REF-C1",
                "nombre": "Medición de la graduación",
                "descripcion": "Medición de la refracción para receta de lentes.",
                "proposito": "Determinar la graduación para la confección de lentes.",
                "preparacion": "No usar lentes de contacto el día del examen.",
                "requisitos": "No requiere orden médica.",
                "precio": "$20.000 a $24.000",
                "horario": "lunes a viernes, 08:30 a 12:00",
                "anticipacion": "1 día hábil",
            },
        ],
    },
    {
        "centro_id": "56712254444",
        "archivo": "centro-especialidades-visuales-lircay.pdf",
        "nombre": "Centro de Especialidades Visuales Lircay",
        "especialidad": "Oftalmología",
        "ciudad": "Talca",
        "comuna": "Talca",
        "direccion": "Av. Lircay 1500, Talca",
        "telefono": "+56 71 225 4444",
        "informacion_general": (
            "Centro de especialidades visuales. Realiza evaluaciones generales y derivaciones. "
            "Horario de atención: lunes a viernes de 09:00 a 17:00."
        ),
        "politicas": [
            "La evaluación integral la realiza un tecnólogo médico; el precio depende de los módulos "
            "que se realicen.",
            "El centro no informa un valor único por la evaluación integral.",
        ],
        "examenes": [
            {
                "codigo": "INT-E1",
                "nombre": "Evaluación oftalmológica integral",
                "descripcion": (
                    "Evaluación general de la visión que puede incluir, según criterio del profesional, "
                    "medición de la presión ocular, fondo de ojo y refracción."
                ),
                "proposito": (
                    "Evaluación general de la salud visual; no es un examen específico de glaucoma."
                ),
                "preparacion": "No requiere preparación.",
                "requisitos": "Orden médica sugerida.",
                "precio": "Referencial desde $50.000",
                "horario": "lunes a viernes, 09:00 a 17:00",
                "anticipacion": "1 día hábil",
            },
        ],
    },
]


def centro_por_id(centro_id: str) -> dict | None:
    for centro in CENTROS:
        if centro["centro_id"] == centro_id:
            return centro
    return None
