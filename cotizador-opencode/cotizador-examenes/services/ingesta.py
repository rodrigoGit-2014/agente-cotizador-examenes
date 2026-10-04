"""Ingesta de documentos de centro (`spec.md` §5.9).

PDF -> texto -> limpieza -> fragmentos por sección -> embeddings -> Redis del curso.
También extrae, por código, la lista de exámenes de cada centro.

Soporta dos formatos de documento:
- **Contrato:** cada examen empieza con `Examen: <nombre> | Código: <código>`.
- **Por secciones:** el de `prompt_createdfile.md` (`Identificación`, `Descripción`, ...).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import config
from schemas import ExamenCentro, Fragmento

# --- Extracción de texto y limpieza --------------------------------------------

def extraer_texto(path: Path) -> str:
    from pypdf import PdfReader

    lector = PdfReader(str(path))
    return "\n".join((pagina.extract_text() or "") for pagina in lector.pages)


def limpiar(texto: str) -> str:
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    texto = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", texto)  # une palabras cortadas
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def _resumen(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip()


# --- Identificador del centro ---------------------------------------------------

def extraer_centro_id(texto: str) -> str | None:
    m = re.search(r"Tel[eé]fono\s*:\s*(\+?[\d\s\-()]{6,})", texto)
    if not m:
        return None
    digitos = re.sub(r"\D", "", m.group(1))
    return digitos or None


# --- Extracción de exámenes -----------------------------------------------------

PATRON_CONTRATO = re.compile(
    r"Examen\s*:\s*(?P<nombre>[^|\n]+?)\s*\|\s*C[oó]digo\s*:\s*(?P<codigo>\S+)"
)
_CAMPOS = "Descripción|Propósito|Preparación|Requisitos|Precio|Horario de atención|Anticipación mínima"


def _campo(bloque: str, etiqueta: str) -> str:
    m = re.search(
        rf"{etiqueta}\s*:\s*(.+?)(?=\n\s*(?:{_CAMPOS})\s*:|\Z)", bloque, re.DOTALL
    )
    return _resumen(m.group(1)) if m else ""


def _examenes_contrato(texto: str) -> list[dict]:
    coincidencias = list(PATRON_CONTRATO.finditer(texto))
    salida = []
    for i, m in enumerate(coincidencias):
        inicio = m.start()
        fin = coincidencias[i + 1].start() if i + 1 < len(coincidencias) else len(texto)
        bloque = texto[m.end():fin]
        salida.append(
            {
                "codigo": m.group("codigo").strip().rstrip("."),
                "nombre": _resumen(m.group("nombre")),
                "descripcion": _campo(bloque, "Descripción"),
                "proposito": _campo(bloque, "Propósito"),
                "inicio": inicio,
                "fin": fin,
            }
        )
    return salida


def _inicio_seccion(ancla: int, texto: str) -> int:
    """Última línea numerada (`4 Título`) antes del ancla `<n>.1 Identificación`."""
    inicio = ancla
    for m in re.finditer(r"(?m)^\s*\d+\s+\S.+$", texto[:ancla]):
        inicio = m.start()
    return inicio


def _examenes_secciones(texto: str) -> list[dict]:
    anclas = [m.start() for m in re.finditer(r"(?m)^\s*\d+\.1\s+Identificaci[oó]n\s*$", texto)]
    inicios = [_inicio_seccion(a, texto) for a in anclas]
    salida = []
    for i, inicio in enumerate(inicios):
        fin = inicios[i + 1] if i + 1 < len(inicios) else len(texto)
        bloque = texto[inicio:fin]
        if "Código interno del centro" not in bloque:
            continue  # la subsección de la información general no es un examen
        m_cod = re.search(r"C[oó]digo interno del centro\s*:\s*([^\n\.]+)", bloque)
        m_nom = re.search(r"Nombre com[uú]n\s*:\s*([^\n\.]+)", bloque)
        m_titulo = re.match(r"\s*\d+\s+(.+)", bloque)
        m_desc = re.search(r"Descripci[oó]n\s*\n(.*?)(?=\n\s*\d+\.\d+\s)", bloque, re.DOTALL)
        descripcion = _resumen(m_desc.group(1)) if m_desc else ""
        proposito = ""
        m_prop = re.search(r"(Sirve para[^.]*\.)", descripcion)
        if m_prop:
            proposito = m_prop.group(1).strip()
        elif descripcion:
            proposito = descripcion
        codigo = (m_cod.group(1).strip().rstrip(".") if m_cod else "") or f"SIN-COD-{i+1}"
        nombre = (m_nom.group(1).strip().rstrip(".") if m_nom else "") or (
            _resumen(m_titulo.group(1)) if m_titulo else f"Examen {i+1}"
        )
        salida.append(
            {
                "codigo": codigo,
                "nombre": nombre,
                "descripcion": descripcion,
                "proposito": proposito,
                "inicio": inicio,
                "fin": fin,
            }
        )
    return salida


def extraer_examenes(texto: str) -> list[dict]:
    if PATRON_CONTRATO.search(texto):
        return _examenes_contrato(texto)
    return _examenes_secciones(texto)


# --- Fragmentación --------------------------------------------------------------

def fragmentar(texto: str, centro_id: str, examenes: list[dict], fuente: str) -> list[Fragmento]:
    general = texto[: examenes[0]["inicio"]] if examenes else texto
    m_pol = re.search(r"Pol[ií]ticas del centro", general)
    if m_pol:
        info_txt, pol_txt = general[: m_pol.start()].strip(), general[m_pol.start():].strip()
    else:
        info_txt, pol_txt = general.strip(), ""

    frags: list[Fragmento] = []
    if info_txt:
        frags.append(
            Fragmento(centro_id=centro_id, codigo_examen="general",
                      seccion="informacion_general", texto=info_txt, fuente=fuente)
        )
    if pol_txt:
        frags.append(
            Fragmento(centro_id=centro_id, codigo_examen="general",
                      seccion="politicas", texto=pol_txt, fuente=fuente)
        )
    for ex in examenes:
        frags.append(
            Fragmento(centro_id=centro_id, codigo_examen=ex["codigo"], seccion="examen",
                      texto=texto[ex["inicio"]:ex["fin"]].strip(), fuente=fuente)
        )
    return frags


# --- Análisis por documento -----------------------------------------------------

def analizar_pdf(path: Path) -> tuple[str | None, list[ExamenCentro], list[Fragmento]]:
    texto = limpiar(extraer_texto(path))
    centro_id = extraer_centro_id(texto)
    if not centro_id:
        return None, [], []
    crudos = extraer_examenes(texto)
    examenes = [
        ExamenCentro(
            centro_id=centro_id,
            codigo=e["codigo"],
            nombre=e["nombre"],
            descripcion=e["descripcion"],
            proposito=e["proposito"],
        )
        for e in crudos
    ]
    fragmentos = fragmentar(texto, centro_id, crudos, fuente=path.name)
    return centro_id, examenes, fragmentos


def analizar_carpeta(directorio: Path | None = None):
    directorio = directorio or config.DOCUMENTOS_DIR
    examenes: list[ExamenCentro] = []
    fragmentos: list[Fragmento] = []
    for pdf in sorted(Path(directorio).glob("*.pdf")):
        _, exs, frags = analizar_pdf(pdf)
        examenes.extend(exs)
        fragmentos.extend(frags)
    return examenes, fragmentos


# --- Lista de exámenes en Redis -------------------------------------------------

def clave_examenes(centro_id: str) -> str:
    return f"cotizador:examenes:{centro_id}"


def guardar_examenes(client, examenes: list[ExamenCentro]) -> None:
    por_centro: dict[str, list[dict]] = {}
    for e in examenes:
        por_centro.setdefault(e.centro_id, []).append(e.model_dump())
    for cid, items in por_centro.items():
        client.set(clave_examenes(cid), json.dumps(items, ensure_ascii=False))


def cargar_examenes(client, centro_id: str) -> list[ExamenCentro]:
    crudo = client.get(clave_examenes(centro_id))
    if not crudo:
        return []
    datos = json.loads(crudo)
    return [ExamenCentro(**d) for d in datos]


# --- Pipeline completo ----------------------------------------------------------

def _hash_fragmentos(fragmentos: list[Fragmento]) -> str:
    h = hashlib.sha1()
    for f in sorted(fragmentos, key=lambda x: (x.centro_id, x.codigo_examen, x.seccion)):
        h.update(f"{f.centro_id}|{f.codigo_examen}|{f.seccion}|{f.texto}".encode("utf-8"))
    return h.hexdigest()


def ingestar(directorio: Path | None = None, forzar: bool = False) -> dict:
    """Carga los documentos de `data/documentos/` en el Redis del curso. Idempotente."""
    from services import embeddings, redis_store

    examenes, fragmentos = analizar_carpeta(directorio)
    if not fragmentos:
        return {"fragmentos": 0, "examenes": 0, "cargado": False, "motivo": "sin documentos"}

    client = redis_store.cliente()
    huella = _hash_fragmentos(fragmentos)
    if not forzar and client.get("cotizador:ingesta_hash") == huella:
        return {"fragmentos": len(fragmentos), "examenes": len(examenes),
                "cargado": False, "motivo": "ya cargado"}

    redis_store.asegurar_indice(client, config.DIMENSIONES)
    client.delete(config.INDICE_CENTROS)  # recarga limpia si cambió
    redis_store.asegurar_indice(client, config.DIMENSIONES)

    vectores = embeddings.embeber([f.texto for f in fragmentos])
    for f, v in zip(fragmentos, vectores):
        f.embedding = v
    escritos = redis_store.cargar_fragmentos(client, fragmentos, config.DIMENSIONES)
    guardar_examenes(client, examenes)
    client.set("cotizador:ingesta_hash", huella)
    return {"fragmentos": escritos, "examenes": len(examenes), "cargado": True}
