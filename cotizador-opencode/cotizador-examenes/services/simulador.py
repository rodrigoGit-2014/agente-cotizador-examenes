"""Llamada simulada (`spec.md` §5.8).

Llamador (código) ⇄ recepcionista (LLM). Los eventos "no contesta" y "llamada cortada" los
resuelve el código; los demás los representa la recepcionista y el código garantiza su efecto.
"""

from __future__ import annotations

from agents import interpretador_cotizacion, recepcionista
from schemas import Centro, Cotizacion, Escenario, Preparacion, Precio, ProximaHora, Reserva

PALABRAS_PREVISION = ("particular", "fonasa", "isapre", "previsi")
PALABRAS_AGENDA = ("agendar", "reserv", "anotar", "nombre")


def _asking_prevision(texto: str) -> bool:
    t = texto.lower()
    return any(p in t for p in PALABRAS_PREVISION)


def _ofrece_agendar(texto: str) -> bool:
    t = texto.lower()
    return any(p in t for p in PALABRAS_AGENDA)


def _tras_turno(escenario: Escenario, centro_id: str) -> int:
    for e in escenario.eventos.get(centro_id, []):
        if e.evento == "llamada_cortada" and e.tras_turno:
            return e.tras_turno
    return 2


def _truncar(transcripcion: list[dict], tras_turno: int) -> list[dict]:
    vistos = 0
    for i, t in enumerate(transcripcion):
        if t["hablante"] == "centro":
            vistos += 1
            if vistos >= tras_turno:
                return transcripcion[: i + 1]
    return transcripcion


def _conversar(centro: Centro, nombre_examen: str, prevision: str, hora: str,
               eventos: list[str], fragmentos: list[dict]) -> list[dict]:
    contexto = {
        "centro": centro.nombre,
        "fragmentos": fragmentos,
        "hora": hora,
        "eventos": eventos,
    }
    trans: list[dict] = []

    def dice(hablante: str, texto: str) -> None:
        trans.append({"hablante": hablante, "texto": texto})

    def centro_habla() -> str:
        t = recepcionista.responder(contexto, trans)
        trans.append({"hablante": "centro", "texto": t})
        return t

    dice("llamador", f"Hola, buenos días. ¿Realizan {nombre_examen}?")
    centro_habla()

    dice("llamador", "¿Qué precio tiene?")
    r = centro_habla()
    if _asking_prevision(r):
        if prevision in ("Fonasa", "Isapre", "particular"):
            dice("llamador", f"Es {prevision}.")
        else:
            dice("llamador", "No lo sé; ¿me puede dar el valor particular?")
        centro_habla()

    dice("llamador", "¿Para cuándo hay disponibilidad?")
    r = centro_habla()
    if "intenta_agendar" in eventos or _ofrece_agendar(r):
        dice("llamador", "No, por ahora solo estoy cotizando.")
        centro_habla()

    dice("llamador", "¿Requiere alguna preparación?")
    centro_habla()
    dice("llamador", "Muchas gracias, eso era todo. Adiós.")
    return trans


def _no_contesta(centro: Centro, codigo: str, nombre: str, eventos: list[str]) -> Cotizacion:
    return Cotizacion(
        centro_id=centro.centro_id,
        centro=centro.nombre,
        codigo_examen=codigo,
        nombre_examen_centro=nombre,
        contesto=False,
        realiza="no_confirmado",
        precio=Precio(),
        proxima_hora=ProximaHora(estado="no_confirmada", detalle="no contesta"),
        preparacion=Preparacion(),
        eventos_aplicados=eventos,
    )


def _aplicar_eventos(cot: Cotizacion, eventos: list[str]) -> None:
    if "sin_agenda_llamar_luego" in eventos:
        cot.proxima_hora = ProximaHora(estado="no_confirmada", detalle="el centro pidió volver a llamar")
    if "sin_agenda_periodo" in eventos:
        cot.proxima_hora = ProximaHora(estado="no_disponible", detalle="sin horas en el período")
    if "examen_suspendido" in eventos:
        cot.realiza = "no_temporalmente"
    if "intenta_agendar" in eventos:
        cot.reserva = Reserva(ofrecida=True, aceptada=False)


def ejecutar_llamada(
    *,
    centro: Centro,
    codigo_examen: str,
    nombre_examen_centro: str,
    prevision: str,
    escenario: Escenario,
    fragmentos: list[dict],
) -> Cotizacion:
    eventos = [e.evento for e in escenario.eventos.get(centro.centro_id, [])]

    if "no_contesta" in eventos:
        return _no_contesta(centro, codigo_examen, nombre_examen_centro, eventos)

    hora = escenario.horas.get(centro.centro_id, {}).get(codigo_examen, "")
    fuente = [f.get("texto", "") for f in fragmentos] + [hora]

    trans = _conversar(centro, nombre_examen_centro, prevision, hora, eventos, fragmentos)
    if recepcionista.validar_fidelidad(trans, fuente):
        trans = _conversar(centro, nombre_examen_centro, prevision, hora, eventos, fragmentos)

    if "llamada_cortada" in eventos:
        trans = _truncar(trans, _tras_turno(escenario, centro.centro_id))

    cotizacion = interpretador_cotizacion.interpretar(
        trans,
        centro_id=centro.centro_id,
        centro=centro.nombre,
        codigo_examen=codigo_examen,
        nombre_examen_centro=nombre_examen_centro,
        eventos=eventos,
    )
    _aplicar_eventos(cotizacion, eventos)
    return cotizacion
