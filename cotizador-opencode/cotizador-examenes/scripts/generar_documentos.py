"""Genera los PDF de los centros de prueba a partir de `contenido_centros.py`.

Herramienta de desarrollo: en el flujo real el contenido lo produce un LLM guiado por
`prompts/prompt_generador_centro_examenes.py` y se revisa a mano. Este script solo vuelca
ese contenido a PDF, con el aviso de datos simulados ([P-10]), para dejarlo versionado en
`data/documentos/`.

Uso (desde la raíz del proyecto, con el intérprete del .venv):
    python scripts/generar_documentos.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from xml.sax.saxutils import escape  # noqa: E402

from reportlab.lib.enums import TA_LEFT  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)
from reportlab.pdfgen import canvas as _canvas  # noqa: E402

import config  # noqa: E402
from contenido_centros import CENTROS  # noqa: E402

AVISO = "Datos simulados — documento ficticio. Precios y horarios de prueba, no vigentes."


def _estilos() -> dict:
    base = getSampleStyleSheet()
    return {
        "titulo": ParagraphStyle(
            "titulo", parent=base["Title"], fontName="Helvetica-Bold", fontSize=16, spaceAfter=4
        ),
        "aviso": ParagraphStyle(
            "aviso",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            textColor="#b00020",
            spaceAfter=10,
        ),
        "seccion": ParagraphStyle(
            "seccion",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "parrafo": ParagraphStyle(
            "parrafo", parent=base["Normal"], fontName="Helvetica", fontSize=10, leading=14, alignment=TA_LEFT
        ),
        "examen_titulo": ParagraphStyle(
            "examen_titulo",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            spaceBefore=10,
            spaceAfter=4,
        ),
        "campo": ParagraphStyle(
            "campo", parent=base["Normal"], fontName="Helvetica", fontSize=10, leading=14, leftIndent=10
        ),
    }


def _pie_de_pagina(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor("#777777")
    canvas.drawString(2 * cm, 1.2 * cm, AVISO)
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"página {doc.page}")
    canvas.restoreState()


def _parrafos_examen(examen: dict, estilos: dict) -> list:
    flujo = [
        Paragraph(escape(f"Examen: {examen['nombre']} | Código: {examen['codigo']}"), estilos["examen_titulo"]),
        Paragraph(escape(f"Descripción: {examen['descripcion']}"), estilos["campo"]),
        Paragraph(escape(f"Propósito: {examen['proposito']}"), estilos["campo"]),
        Paragraph(escape(f"Preparación: {examen['preparacion']}"), estilos["campo"]),
        Paragraph(escape(f"Requisitos: {examen['requisitos']}"), estilos["campo"]),
        Paragraph(escape(f"Precio: {examen['precio']}"), estilos["campo"]),
        Paragraph(escape(f"Horario de atención: {examen['horario']}"), estilos["campo"]),
        Paragraph(escape(f"Anticipación mínima: {examen['anticipacion']}"), estilos["campo"]),
    ]
    return flujo


def construir_documento(centro: dict, destino: Path, estilos: dict) -> None:
    doc = SimpleDocTemplate(
        str(destino),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=centro["nombre"],
        author="Banco de pruebas del cotizador",
    )

    flujo: list = [
        Paragraph(escape(centro["nombre"]), estilos["titulo"]),
        Paragraph(escape(AVISO), estilos["aviso"]),
        Paragraph(escape("Información general"), estilos["seccion"]),
        Paragraph(escape(centro["informacion_general"]), estilos["parrafo"]),
        Paragraph(escape(f"Dirección: {centro['direccion']}"), estilos["campo"]),
        Paragraph(escape(f"Teléfono: {centro['telefono']}"), estilos["campo"]),
        Paragraph(escape(f"Ciudad: {centro['ciudad']} · Especialidad: {centro['especialidad']}"), estilos["campo"]),
        Paragraph(escape("Políticas del centro"), estilos["seccion"]),
    ]
    for politica in centro["politicas"]:
        flujo.append(Paragraph(escape(f"• {politica}"), estilos["parrafo"]))
    flujo.append(Paragraph(escape("Catálogo de exámenes"), estilos["seccion"]))
    for examen in centro["examenes"]:
        flujo.extend(_parrafos_examen(examen, estilos))
        flujo.append(Spacer(1, 6))

    doc.build(flujo, onFirstPage=_pie_de_pagina, onLaterPages=_pie_de_pagina)


def main() -> None:
    estilos = _estilos()
    config.DOCUMENTOS_DIR.mkdir(parents=True, exist_ok=True)
    generados = []
    for centro in CENTROS:
        destino = config.DOCUMENTOS_DIR / centro["archivo"]
        construir_documento(centro, destino, estilos)
        generados.append((centro["nombre"], destino.name, len(centro["examenes"])))

    print(f"Documentos generados en {config.DOCUMENTOS_DIR}:")
    for nombre, archivo, n_examenes in generados:
        print(f"  - {archivo}  ({nombre}, {n_examenes} exámenes)")


if __name__ == "__main__":
    main()
