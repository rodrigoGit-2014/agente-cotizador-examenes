"""Recorrido narrado del cotizador para el notebook de entrega (bloque 11).

Toda la lógica de la demostración vive aquí. La celda del notebook define su propia función
`main()` (con el prompt del usuario) y llama a `correr_recorrido(...)`.

El mapa del sistema se genera desde el grafo compilado, así que refleja cualquier cambio en
los nodos o conexiones. Para probar otra consulta, pásala a `correr_recorrido("...")`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Permite importar los módulos del proyecto tanto desde el notebook como al correr este archivo.
RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

# Frases para traducir a lenguaje simple lo que pide el agente.
PLAN = {
    "buscar_centros": "buscar centros en tu ciudad",
    "identificar_examen": "revisar en cada centro si hacen el examen",
    "consultar_centro": "llamar al siguiente centro de la lista",
    "consultar_documentos": "revisar la información publicada del centro",
}

_CENTRO_RE = re.compile(r"^\s*\d{1,2}\s*[).]\s*\*\*|^\s*\*\*\s*\d{1,2}\s*[).]")
_SECCION_RE = re.compile(
    r"^\s*\*\*\s*(?:Coincidencia[s]?\s+dudosa[s]?|Descartad[oa]s?|Centro[s]?\s+descartad[oa]s?)\b"
)


# --- Formato de datos ------------------------------------------------------------

def _centro(centros: dict, cid: str) -> str:
    c = centros.get(cid)
    if c is None:
        return cid
    return f"{c.nombre}" + (f" — tel. {c.telefono}" if c.telefono else "")


def _precio(p) -> str:
    if p.tipo == "no_confirmado" or (p.valor is None and p.desde is None):
        return "no confirmado por el centro" + (f" ({p.texto})" if p.texto else "")
    if p.tipo == "rango" and p.desde and p.hasta:
        return f"entre ${p.desde:,.0f} y ${p.hasta:,.0f}".replace(",", ".")
    if p.valor is not None:
        extra = "" if p.tipo == "cerrado" else f" ({p.tipo})"
        return f"${p.valor:,.0f}".replace(",", ".") + extra
    return p.tipo


def _hora(h) -> str:
    if h.estado == "confirmada" and h.valor:
        return f"{h.valor} (confirmada, no reservada)"
    if h.estado == "no_confirmada":
        return "no confirmada" + (f": {h.detalle}" if h.detalle else "")
    if h.estado == "no_disponible":
        return "sin horas" + (f": {h.detalle}" if h.detalle else "")
    return h.estado


def _prep(p) -> str:
    return p.texto if (p.estado == "informada" and p.texto) else "no informada o no confirmada"


def _motivo(m) -> str:
    return {
        "N_alcanzado": "ya reuní el número de cotizaciones que pediste",
        "centros_agotados": "ya no quedaban centros por consultar",
        "sin_centros": "no encontré centros en esa ciudad",
        "sin_coincidencias": "no encontré centros que hicieran ese examen",
        "ninguno_contesta": "ninguno de los centros contestó",
        "tope_iteraciones": "llegué al máximo de intentos permitidos",
        "respuesta_info_publicada": "era una consulta de información publicada",
    }.get(m, m or "sin motivo registrado")


def _formatear_respuesta(texto: str) -> str:
    """Da formato de lectura a la respuesta final del LLM.

    El modelo suele devolver los datos casi en un párrafo: los encabezados de cada centro quedan
    pegados al texto anterior. Aquí se separa cada encabezado en su propia línea y se indentan
    los detalles por niveles (centro vs. detalle).
    """
    texto = re.sub(r"(?<![\w*])\s*(\d{1,2}\s*[).]\s*\*\*)", r"\n\n\1", texto)       # "1. **Centro**"
    texto = re.sub(r"\*\*\s*\d{1,2}\s*[).]", lambda m: "\n\n" + m.group(0), texto)     # "**1) Centro**"
    texto = re.sub(
        r"\*\*\s*(?:Coincidencia[s]?\s+dudosa[s]?|Descartad[oa]s?|Centro[s]?\s+descartad[oa]s?)\b",
        lambda m: "\n\n" + m.group(0),
        texto,
    )
    texto = texto.replace(" - **", "\n- **")  # campos en línea: " - **Precio:**"

    lineas = []
    for linea in texto.split("\n"):
        limpia = linea.strip()
        if not limpia:
            lineas.append("")
        elif _CENTRO_RE.match(limpia) or _SECCION_RE.match(limpia):
            lineas.append("   " + limpia)                # encabezado de centro o sección
        elif limpia.startswith(("-", "•")) or limpia.startswith("* "):
            lineas.append("       " + limpia)            # detalle del centro
        else:
            lineas.append("   " + limpia)                # párrafo normal
    salida = []
    for l in lineas:
        if l == "" and (not salida or salida[-1] == ""):
            continue
        salida.append(l)
    return "\n".join(salida).strip("\n")


# --- Secciones del recorrido -----------------------------------------------------

def _mostrar_mapa(app) -> None:
    """Muestra el grafo como imagen, generado desde el propio grafo compilado."""
    print("\n" + "=" * 78)
    print(" MAPA DEL SISTEMA (nodos y conexiones del grafo)")
    print("=" * 78)
    try:
        from IPython.display import Image, display

        display(Image(app.get_graph().draw_mermaid_png()))
    except Exception as exc:  # sin IPython o sin red: mostrar el código mermaid
        print(f"(no se pudo renderizar la imagen: {exc})")
        print(app.get_graph().draw_mermaid())


def _preparar_redis() -> None:
    """Deja lista la base de documentos y RAG en Redis (idempotente).

    Se invoca sola para que el usuario no tenga que ejecutar la ingesta a mano. Si los
    documentos ya estaban cargados, no vuelve a embeberlos; solo avisa cuando carga algo.
    """
    try:
        from services import ingesta

        resultado = ingesta.ingestar()
        if resultado.get("cargado"):
            print(f"(Preparé la base de documentos: {resultado.get('fragmentos', 0)} fragmentos, "
                  f"{resultado.get('examenes', 0)} exámenes.)")
    except Exception as exc:  # Redis caído, falta de embeddings, etc.: se informa y se sigue
        print(f"(No pude preparar la base de documentos: {exc})")


def _nuevo_hilo() -> dict:
    """Un hilo nuevo: evita que el checkpointer reutilice estado de una corrida anterior."""
    import time

    return {"configurable": {"thread_id": f"notebook-{time.time_ns()}"}}


def _recorrer(app, consulta: str, escenario_id: str, hilo: dict) -> tuple[dict, list[str]]:
    """Ejecuta un turno del grafo narrando el paso a paso. Devuelve (estado_final, nodos)."""
    from langchain_core.messages import HumanMessage

    entrada = {"messages": [HumanMessage(content=consulta)], "escenario_id": escenario_id}

    centros: dict = {}
    documentos_vistos: set = set()
    centros_llamados: set = set()
    cotizaciones_vistas: dict = {}
    n_objetivo = None
    solicitud_actual = None
    busqueda_args: dict = {}
    nodos: list[str] = []
    pasos_impresos: dict = {}
    contador = [0]
    rechazos_previos = 0

    def titulo(clave, texto):
        # Numera los pasos en el orden en que ocurren: 1, 2, 3... sin huecos.
        if clave in pasos_impresos:
            return
        contador[0] += 1
        pasos_impresos[clave] = contador[0]
        print(f"\nPASO {contador[0]} — {texto}")

    for chunk in app.stream(entrada, hilo, stream_mode="updates"):
        for nodo, upd in chunk.items():
            nodos.append(nodo)

            if nodo == "router":
                sol = upd.get("solicitud")
                solicitud_actual = sol
                ruta = upd.get("ruta")
                faltan = []
                if sol is not None:
                    if not sol.necesidad:
                        faltan.append("qué examen necesitas")
                    elif sol.necesidad_ambigua:
                        faltan.append("precisar qué examen necesitas")
                    if not sol.ciudad:
                        faltan.append("en qué ciudad")
                    if sol.prevision.value == "no_indicada":
                        faltan.append("tu previsión (Fonasa, Isapre o particular)")
                titulo("p1", "🧭 Entiendo tu consulta")
                if ruta in ("cotizar", "info_publicada") and faltan:
                    print(f"   ⚠ Falta información para continuar: {', '.join(faltan)}.")
                    print("   → Te la pediré antes de cotizar.")
                elif ruta in ("cotizar", "info_publicada"):
                    n_objetivo = sol.N
                    detalle = f"«{sol.necesidad}» en {sol.ciudad}"
                    if sol.prevision.value != "no_indicada":
                        detalle += f", previsión {sol.prevision.value}"
                    print(f"   ✓ La consulta está completa: {detalle}.")
                else:
                    print("   → No hace falta cotizar; te respondo directamente.")

            elif nodo == "respuesta_directa":
                msg = upd["messages"][-1]
                titulo("directa", "💬 Te respondo directamente:")
                print("   " + str(msg.content).replace("\n", "\n   "))

            elif nodo == "agente":
                msg = upd["messages"][-1]
                pedidos = getattr(msg, "tool_calls", None) or []
                if pedidos:
                    cuenta = {}
                    for tc in pedidos:
                        nombre_tc = tc.get("name", "")
                        cuenta[nombre_tc] = cuenta.get(nombre_tc, 0) + 1
                        if nombre_tc == "buscar_centros":
                            busqueda_args = tc.get("args", {}) or {}
                    frases = []
                    for n, c in cuenta.items():
                        if n == "buscar_centros" and busqueda_args:
                            esp = busqueda_args.get("especialidad") or "tu examen"
                            ciu = busqueda_args.get("ciudad") or "tu ciudad"
                            frases.append(f"buscar centros de «{esp}» en «{ciu}»")
                        else:
                            frases.append(PLAN.get(n, n) + (f" ({c})" if c > 1 else ""))
                    print(f"\n🤔 Mi siguiente paso: {'; '.join(frases)}.")
                else:
                    comparables = sum(1 for c in cotizaciones_vistas.values() if c.es_comparable())
                    if n_objetivo and comparables >= n_objetivo:
                        print(f"\n✅ Ciclo de llamadas terminado: ya reuní {comparables} cotización(es) "
                              f"comparable(s), que es el número que pediste (N={n_objetivo}). "
                              "No llamo a más centros.")
                    else:
                        print("\n✅ Ciclo de llamadas terminado: no quedan más centros por llamar. "
                              "Paso a resumir.")

            elif nodo == "herramientas":
                if "centros" in upd:
                    nuevos_centros = upd.get("centros") or []
                    for c in nuevos_centros:
                        centros[c.centro_id] = c
                    esp = (busqueda_args.get("especialidad")
                           or getattr(solicitud_actual, "especialidad", None) or "tu examen")
                    ciu = (busqueda_args.get("ciudad")
                           or getattr(solicitud_actual, "ciudad", None) or "tu ciudad")
                    titulo("p2", f"🔎 Busco centros de «{esp}» en «{ciu}»")
                    if nuevos_centros:
                        print(f"   Encontré {len(nuevos_centros)} centros:")
                        for c in nuevos_centros:
                            extra = f" — {c.direccion}" if c.direccion else ""
                            print(f"      · {c.nombre}{extra}"
                                  + (f" — tel. {c.telefono}" if c.telefono else ""))
                    else:
                        print(f"   No encontré centros de esa especialidad en «{ciu}».")

                for cid, ident in (upd.get("identificaciones") or {}).items():
                    if cid in documentos_vistos:
                        continue
                    documentos_vistos.add(cid)
                    titulo("p3", "📄 Reviso el documento de cada centro en la base de datos (Redis)")
                    print(f"\n   Centro «{_centro(centros, cid)}»:")
                    if ident.veredicto == "sin_documento":
                        print("      ✗ No encontré un documento cargado para este centro.")
                    elif ident.veredicto == "coincide":
                        print(f"      ✓ Encontré su examen «{ident.nombre_examen_centro}»"
                              f" (código {ident.codigo_examen}) y coincide con lo que buscas.")
                    elif ident.veredicto == "dudoso":
                        print(f"      ? Encontré «{ident.nombre_examen_centro}», pero no es exactamente"
                              " lo que buscas → lo dejo como dudoso.")
                    else:
                        print("      ✗ Su documento no ofrece ese examen → lo descarto.")

                for cid, cot in (upd.get("cotizaciones") or {}).items():
                    if cid in centros_llamados:
                        continue
                    centros_llamados.add(cid)
                    cotizaciones_vistas[cid] = cot
                    titulo("p4", "📞 Llamo a los centros para cotizar (conversación simulada)")
                    print(f"\n   ☎ Llamando a «{_centro(centros, cid)}» por «{cot.nombre_examen_centro}»:")
                    if not cot.contesto:
                        print("      ✗ Nadie contestó la llamada.")
                        continue
                    for t in cot.transcripcion:
                        quien = "Tú" if t.hablante == "llamador" else "Recepción"
                        print(f"      ({quien}) {t.texto}")
                    print("      — Lo que logré registrar —")
                    print(f"      · Precio: {_precio(cot.precio)}")
                    print(f"      · Modalidad: {cot.modalidad}")
                    print(f"      · Próxima hora: {_hora(cot.proxima_hora)}")
                    print(f"      · Preparación: {_prep(cot.preparacion)}")
                    if cot.reserva.ofrecida:
                        print("      · Ofreció agendar la hora; no se aceptó (solo cotizamos).")

                rechazos = upd.get("rechazos", [])
                for r in rechazos[rechazos_previos:]:
                    accion = PLAN.get(r.get("herramienta"), r.get("herramienta"))
                    print(f"\n   ℹ️ Omití una acción ({accion}): {r.get('motivo')}.")
                rechazos_previos = len(rechazos)

            elif nodo == "consolidar":
                rep = upd.get("reporte")
                titulo("p5", "🧮 Consolido todo lo que encontré")
                print(f"   Terminé porque {_motivo(upd.get('motivo_parada'))}.")
                if rep is not None:
                    if rep.comparables:
                        print(f"   Opciones comparables ({len(rep.comparables)}):")
                        for c in rep.comparables:
                            print(f"      - {c.centro}: {c.nombre_examen_centro}, "
                                  f"{_precio(c.precio)}, hora {_hora(c.proxima_hora)}")
                    if rep.dudosos:
                        print(f"   Coincidencias dudosas ({len(rep.dudosos)}):")
                        for d in rep.dudosos:
                            print(f"      - {d.centro}: «{d.nombre_examen_centro}»")
                    if rep.descartados:
                        print(f"   Descartados ({len(rep.descartados)}):")
                        for d in rep.descartados:
                            print(f"      - {d.centro}: {d.motivo}")

            elif nodo == "responder":
                titulo("p6", "✍️ Redacto tu respuesta final")

            elif nodo == "verificador":
                ver = upd.get("verificacion") or {}
                titulo("p7", "🛡️ Reviso la respuesta antes de mostrártela")
                if ver.get("aprobado"):
                    print("   ✓ Todo en orden: sin recomendaciones ni datos inventados.")
                else:
                    for c in ver.get("correcciones", []):
                        print(f"   · Corrección aplicada: {c}")

    estado_final = app.get_state(hilo).values
    return estado_final, nodos


def _mostrar_checklist(estado_final: dict, nodos: list[str]) -> None:
    """Imprime el checklist de criterios de éxito con resultados reales o 'pendiente'."""
    print("\n" + "=" * 78)
    print(" CHECKLIST DE CRITERIOS DE ÉXITO")
    print("=" * 78)

    def criterio(simbolo, titulo_c, que_verifica, resultado):
        print(f"\n{simbolo} {titulo_c}")
        print(f"     Qué verifica: {que_verifica}")
        print(f"     Resultado: {resultado}")

    llego_al_final = bool(nodos) and nodos[-1] in ("verificador", "respuesta_directa")
    iteraciones = estado_final.get("iteraciones", 0)

    criterio(
        "✅" if llego_al_final else "❌",
        "Flujo de principio a fin",
        "que el agente recorra todo el proceso sin quedarse colgado y termine respondiendo.",
        f"{'PASÓ' if llego_al_final else 'NO PASÓ'} — último paso registrado: «{nodos[-1]}».",
    )
    criterio(
        "✅" if nodos else "❌",
        "Trazabilidad",
        "que quede registrada la trayectoria concreta de esta consulta (qué pasó, en qué orden), "
        "que es lo que exporta el informe de validación.",
        f"se registraron {len(nodos)} pasos del grafo.",
    )
    criterio(
        "✅" if iteraciones < 10 else "❌",
        "Límite de intentos",
        "que el agente no entre en bucle: el número de rondas está acotado por código (10).",
        f"{'PASÓ' if iteraciones < 10 else 'NO PASÓ'} — rondas usadas: {iteraciones} de 10.",
    )
    criterio(
        "⏳",
        "Datos iguales a la realidad del simulador",
        "que cada cotización coincida campo por campo con el simulador. No se puede comprobar aquí: "
        "lo corre el agente @validator.",
        "PENDIENTE — se verifica con validacion/run_golden.py (golden set G01–G16).",
    )
    criterio(
        "⏳",
        "Seguridad (datos personales y agendamiento)",
        "que el agente no pida ni filtre datos personales, no obedezca contenido externo y no agende. "
        "No se puede comprobar aquí: lo corre el agente @validator.",
        "PENDIENTE — se verifica con validacion/run_seguridad.py.",
    )
    print("\n" + "=" * 78)
    print(" Fin del recorrido.")
    print("=" * 78)


# --- Punto de entrada ------------------------------------------------------------

def correr_recorrido(consulta: str, escenario_id: str = "default",
                     preparar_redis: bool = True, hilo: dict | None = None) -> None:
    """Ejecuta y narra una consulta completa contra el agente."""
    from main import app

    print("=" * 78)
    print(" RECORRIDO COMPLETO DE UNA CONSULTA")
    print("=" * 78)
    print("\n👤 Tú dices:")
    print(f'   "{consulta}"')

    try:
        if preparar_redis:
            _preparar_redis()
        _mostrar_mapa(app)
        estado_final, nodos = _recorrer(app, consulta, escenario_id, hilo or _nuevo_hilo())

        print("\n" + "-" * 78)
        print(" RESPUESTA FINAL AL USUARIO")
        print("-" * 78)
        print(_formatear_respuesta(estado_final["messages"][-1].content))

        _mostrar_checklist(estado_final, nodos)
    except Exception as exc:
        print("\nNo se pudo ejecutar el recorrido (¿faltan credenciales/Redis?):", exc)


def correr_conversacion(consultas: list[str], escenario_id: str = "default",
                        preparar_redis: bool = True) -> None:
    """Ejecuta varios turnos en el MISMO hilo, reutilizando ciudad y previsión del historial.

    Redis se prepara una sola vez (idempotente), antes del primer turno.
    """
    from main import app

    print("=" * 78)
    print(f" CONVERSACIÓN DE PRUEBA — {len(consultas)} turnos en el mismo hilo")
    print("=" * 78)

    try:
        if preparar_redis:
            _preparar_redis()
        _mostrar_mapa(app)

        hilo = _nuevo_hilo()
        estado_final, nodos = {}, []
        for i, consulta in enumerate(consultas, 1):
            print("\n" + "#" * 78)
            print(f"# TURNO {i} de {len(consultas)}")
            print("#" * 78)
            print("\n👤 Tú dices:")
            print(f'   "{consulta}"')

            estado_final, nodos = _recorrer(app, consulta, escenario_id, hilo)

            print("\n" + "-" * 78)
            print(f" RESPUESTA FINAL AL USUARIO (turno {i})")
            print("-" * 78)
            print(_formatear_respuesta(estado_final["messages"][-1].content))

        _mostrar_checklist(estado_final, nodos)
    except Exception as exc:
        print("\nNo se pudo ejecutar la conversación (¿faltan credenciales/Redis?):", exc)
