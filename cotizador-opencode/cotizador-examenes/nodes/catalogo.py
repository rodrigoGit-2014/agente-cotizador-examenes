"""Respuesta de catálogo sin cotizaciones, llamadas ni generación de datos."""

import json

from langchain_core.messages import AIMessage

from services.catalogo import consultar_catalogo


def nodo_catalogo(state: dict) -> dict:
    solicitud = state.get("solicitud")
    ciudad = solicitud.ciudad if solicitud else None
    try:
        centros = consultar_catalogo(ciudad)
    except Exception:
        return {"messages": [AIMessage(content="No pude consultar el catálogo en este momento. Puede intentarlo nuevamente.")],
                "motivo_parada": "catalogo_no_disponible"}
    if not centros:
        texto = (f"No hay exámenes documentados en el catálogo para {ciudad}." if ciudad
                 else "El catálogo no tiene exámenes cargados todavía.")
        return {"messages": [AIMessage(content=texto)], "motivo_parada": "catalogo_vacio"}
    lineas = ["En el catálogo de demostración tengo estos exámenes documentados:"]
    ultima_ciudad = None
    for centro in centros:
        ciudad_actual = centro["ciudad"] or "Ciudad no confirmada"
        if ciudad_actual != ultima_ciudad:
            lineas.extend(["", f"{ciudad_actual}:"])
            ultima_ciudad = ciudad_actual
        lineas.append(f"- {centro['centro']}:")
        for examen in centro["examenes"]:
            lineas.append(f"  - {examen['nombre']} (código {examen['codigo']}).")
    lineas.extend(["", "Este catálogo contiene datos simulados. La lista no confirma horas disponibles ni precios.",
                   "Puede indicar qué examen y ciudad le interesan para cotizar."])
    return {"messages": [AIMessage(content="\n".join(lineas))],
            "observaciones": [json.dumps(centros, ensure_ascii=False)], "motivo_parada": "catalogo_consultado"}
