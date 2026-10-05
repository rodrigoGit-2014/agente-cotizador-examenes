"""Redis del curso como vector store (`spec.md` §5.9).

Índice `cotizador_centros_v1` (prefijo `cotizador:frag`) sobre hashes, con RediSearch.
La conexión es perezosa: solo falla al usarse si falta `REDIS_URL`.
"""

from __future__ import annotations

from array import array
import re

import config

_AVISO = "Falta REDIS_URL en el .env."


def cliente():
    if not config.REDIS_URL:
        raise RuntimeError(_AVISO)
    from redis import Redis

    return Redis.from_url(config.REDIS_URL, decode_responses=False)


def indice_existe(client) -> bool:
    try:
        client.ft(config.INDICE_CENTROS).info()
        return True
    except Exception:
        return False


def crear_indice(client, dimensiones: int) -> None:
    from redis.commands.search.field import TagField, TextField, VectorField
    from redis.commands.search.index_definition import IndexDefinition, IndexType

    schema = (
        TagField("centro_id"),
        TagField("codigo_examen"),
        TextField("seccion"),
        TextField("texto"),
        TagField("fuente"),
        VectorField(
            "embedding",
            "FLAT",
            {"TYPE": "FLOAT32", "DIM": dimensiones, "DISTANCE_METRIC": "COSINE"},
        ),
    )
    client.ft(config.INDICE_CENTROS).create_index(
        schema,
        definition=IndexDefinition(
            prefix=[config.PREFIJO_FRAGMENTOS], index_type=IndexType.HASH
        ),
    )


def asegurar_indice(client, dimensiones: int) -> None:
    if indice_existe(client):
        return
    crear_indice(client, dimensiones)
    # RediSearch tarda en indexar; esperar brevemente hasta que el índice responda.
    import time

    for _ in range(20):
        try:
            client.ft(config.INDICE_CENTROS).info()
            return
        except Exception:
            time.sleep(0.1)


def _clave(i: int) -> str:
    return f"{config.PREFIJO_FRAGMENTOS}:{i}"


def contar_fragmentos(client, centro_id: str | None = None) -> int:
    if not indice_existe(client):
        return 0
    from redis.commands.search.query import Query

    consulta = f"@centro_id:{{{re.escape(centro_id)}}}" if centro_id else "*"
    q = Query(consulta).paging(0, 0)
    return client.ft(config.INDICE_CENTROS).search(q).total


def cargar_fragmentos(client, fragmentos, dimensiones: int) -> int:
    """Carga fragmentos (con `embedding`) como hashes. Devuelve cuántos escribió."""
    pipe = client.pipeline()
    for i, fr in enumerate(fragmentos):
        mapping = {
            "centro_id": fr.centro_id,
            "codigo_examen": fr.codigo_examen,
            "seccion": fr.seccion,
            "texto": fr.texto,
            "fuente": fr.fuente,
            "embedding": array("f", fr.embedding or []).tobytes(),
        }
        pipe.hset(_clave(i), mapping=mapping)
    pipe.execute()
    return len(fragmentos)


def buscar_fragmentos(
    client,
    vector: list[float],
    centro_id: str,
    codigo_examen: str | None = None,
    top_k: int = config.TOP_K_FRAGMENTOS,
) -> list[dict]:
    from redis.commands.search.query import Query

    filtros = [f"@centro_id:{{{re.escape(centro_id)}}}"]
    if codigo_examen:
        filtros.append(f"(@codigo_examen:{{{re.escape(codigo_examen)}}}|@codigo_examen:{{general}})")
    prefijo = " ".join(filtros)
    q = (
        Query(f"({prefijo})=>[KNN {top_k} @embedding $vec AS score]")
        .sort_by("score")
        .return_fields("texto", "seccion", "codigo_examen", "fuente", "score")
        .dialect(2)
    )
    res = client.ft(config.INDICE_CENTROS).search(
        q, query_params={"vec": array("f", vector).tobytes()}
    )
    salida = []
    for doc in res.docs:
        d = doc if isinstance(doc, dict) else doc.__dict__
        score = d.get("score")
        salida.append(
            {
                "texto": d.get("texto", ""),
                "seccion": d.get("seccion", ""),
                "codigo_examen": d.get("codigo_examen", ""),
                "fuente": d.get("fuente", ""),
                "similitud": (1 - float(score)) if score is not None else None,
            }
        )
    return salida


def obtener_fragmentos(
    client, centro_id: str, codigo_examen: str | None = None, limite: int = 50
) -> list[dict]:
    """Recupera fragmentos por filtro, sin vector (para la recepcionista y la interpretación)."""
    from redis.commands.search.query import Query

    filtros = [f"@centro_id:{{{re.escape(centro_id)}}}"]
    if codigo_examen:
        filtros.append(f"(@codigo_examen:{{{re.escape(codigo_examen)}}}|@codigo_examen:{{general}})")
    q = (
        Query(" ".join(filtros))
        .paging(0, limite)
        .return_fields("texto", "seccion", "codigo_examen", "fuente")
    )
    res = client.ft(config.INDICE_CENTROS).search(q)
    salida = []
    for doc in res.docs:
        d = doc if isinstance(doc, dict) else doc.__dict__
        salida.append(
            {
                "texto": d.get("texto", ""),
                "seccion": d.get("seccion", ""),
                "codigo_examen": d.get("codigo_examen", ""),
                "fuente": d.get("fuente", ""),
            }
        )
    return salida
