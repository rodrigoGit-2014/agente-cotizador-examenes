"""Catálogo leído de Redis: exámenes y ubicación documentada de cada centro."""

import re

from services import ciudades, ingesta, redis_store


def _metadatos(fragmentos: list[dict], centro_id: str) -> tuple[str, str | None]:
    texto = "\n".join(f.get("texto", "") for f in fragmentos if f.get("codigo_examen") == "general")
    nombre = re.search(r"Nombre comercial\s*:\s*([^\n]+)", texto, re.IGNORECASE)
    encabezados = re.findall(r"(?m)^\s*([^\n]+)\nDatos simulados", texto)
    nombre_centro = (nombre.group(1) if nombre else encabezados[-1] if encabezados
                     else f"Centro {centro_id}").strip().rstrip(".")
    ciudad = re.search(r"Ciudad\s*:\s*([^\n·•|]+)", texto, re.IGNORECASE)
    if ciudad:
        return nombre_centro, ciudad.group(1).strip().rstrip(".")
    direccion = re.search(r"Direcci[oó]n\s*:\s*([^\n]+)", texto, re.IGNORECASE)
    if direccion:
        candidata = direccion.group(1).rsplit(",", 1)[-1].strip().rstrip(".")
        if ciudades.es_ciudad_chile(candidata):
            return nombre_centro, candidata
    return nombre_centro, None


def consultar_catalogo(ciudad: str | None = None) -> list[dict]:
    client = redis_store.cliente()
    centros = []
    for clave in sorted(set(client.scan_iter(match="cotizador:examenes:*"))):
        clave = clave.decode("utf-8") if isinstance(clave, bytes) else clave
        centro_id = clave.rsplit(":", 1)[-1]
        examenes = ingesta.cargar_examenes(client, centro_id)
        if not examenes:
            continue
        fragmentos = redis_store.obtener_fragmentos(client, centro_id, "general")
        nombre, ciudad_centro = _metadatos(fragmentos, centro_id)
        if ciudad and ciudades._normalizar(ciudad_centro or "") != ciudades._normalizar(ciudad):
            continue
        centros.append({
            "centro_id": centro_id,
            "centro": nombre,
            "ciudad": ciudad_centro,
            "examenes": [e.model_dump() for e in examenes],
            "fuentes": sorted({f["fuente"] for f in fragmentos if f.get("fuente")}),
        })
    return sorted(centros, key=lambda c: (c["ciudad"] or "", c["centro"]))
