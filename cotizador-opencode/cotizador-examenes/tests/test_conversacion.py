import contextlib
import io
import unittest
from unittest.mock import Mock, patch

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph.message import add_messages

import config
import main
from nodes.respuesta_directa import nodo_respuesta_directa
from nodes.router import nodo_router
from schemas import Centro, Prevision, Reporte, SalidaRouter, Solicitud
from services.historial import crear_memoria, historial_visible


def pedido(identificador="call_pendiente"):
    return AIMessage(content="", tool_calls=[
        {"name": "buscar_centros", "args": {}, "id": identificador, "type": "tool_call"}
    ])


class ConversacionTests(unittest.TestCase):
    def test_historial_excluye_pedidos_y_respuestas_de_herramientas(self):
        usuario = HumanMessage(content="TAC en Talca")
        final = AIMessage(content="No hay opciones confirmadas.")
        mensajes = [usuario, pedido(), ToolMessage(content="resultado", tool_call_id="call_pendiente"), final]
        self.assertEqual(historial_visible(mensajes), [usuario, final])
        llm = Mock()
        llm.invoke.return_value = SalidaRouter(ruta="respuesta_directa")
        with patch("services.llm.llm_estructurado", return_value=llm):
            salida = nodo_router({"messages": mensajes, "iteraciones": 10, "cotizaciones": {"anterior": None}})
        self.assertEqual(salida["iteraciones"], 0)
        self.assertEqual(salida["cotizaciones"], {})
        self.assertEqual(add_messages(mensajes, salida["messages"]), [usuario, final])
        self.assertFalse(any(getattr(m, "tool_calls", None) for m in llm.invoke.call_args.args[0]))

    def test_memoria_recupera_tipos_sin_avisos(self):
        memoria = crear_memoria()
        datos = {"solicitud": Solicitud(prevision=Prevision.fonasa),
                 "centros": [Centro(centro_id="56712221111", nombre="Centro de prueba")],
                 "reporte": Reporte(N=2)}
        with self.assertNoLogs("langgraph.checkpoint.serde.jsonplus", level="WARNING"):
            restaurados = memoria.serde.loads_typed(memoria.serde.dumps_typed(datos))
        self.assertEqual(restaurados["solicitud"].prevision, Prevision.fonasa)
        self.assertIsInstance(restaurados["centros"][0], Centro)
        self.assertIsInstance(restaurados["reporte"], Reporte)

    def test_tope_cierra_pedidos_y_otro_turno_sigue_funcionando(self):
        router = Mock()
        router.invoke.side_effect = [
            SalidaRouter(ruta="cotizar", necesidad="TAC", ciudad="Talca", prevision=Prevision.fonasa),
            SalidaRouter(ruta="respuesta_directa"),
        ]
        directo = Mock()
        directo.invoke.return_value = AIMessage(content="Puede seguir consultando.")
        vistos = []

        def agente(state):
            vistos.append(state["iteraciones"])
            return {"messages": [pedido("call_" + str(len(vistos)))]}

        def herramientas(state):
            return {"messages": [ToolMessage(content="resultado", tool_call_id="call_1")],
                    "iteraciones": config.MAX_ITERACIONES}

        with patch("services.llm.llm_estructurado", return_value=router), \
             patch("services.llm.llm_agente", return_value=directo), \
             patch.object(main, "nodo_agente", agente), \
             patch.object(main, "nodo_herramientas", herramientas), \
             patch.object(main, "nodo_responder", return_value={"messages": [AIMessage(content="Consulta terminada.")]}):
            app = main.build_graph()
            runtime = {"configurable": {"thread_id": "test"}}
            with self.assertNoLogs("langgraph.checkpoint.serde.jsonplus", level="WARNING"):
                primero = app.invoke({"messages": [HumanMessage(content="TAC en Talca con Fonasa")]}, runtime)
                respuestas = {m.tool_call_id for m in primero["messages"] if isinstance(m, ToolMessage)}
                self.assertEqual(respuestas, {"call_1", "call_2"})
                segundo = app.invoke({"messages": [HumanMessage(content="Hola")]}, runtime)
            self.assertEqual(segundo["iteraciones"], 0)
            self.assertEqual(segundo["messages"][-1].content, "Puede seguir consultando.")
            self.assertFalse(any(getattr(m, "tool_calls", None) for m in directo.invoke.call_args.args[0]))

    def test_respuesta_directa_tolera_fallo_del_proveedor(self):
        with patch("services.llm.llm_agente", side_effect=RuntimeError("ERROR TECNICO " * 500)):
            salida = nodo_respuesta_directa({"messages": [HumanMessage(content="Hola")], "ruta": "respuesta_directa"})
        texto = salida["messages"][-1].content
        self.assertNotIn("ERROR TECNICO", texto)
        self.assertLess(len(texto), 200)

    def test_consola_no_cierra_tras_un_error(self):
        app = Mock()
        app.invoke.side_effect = [RuntimeError("ERROR TECNICO " * 500),
                                 {"messages": [AIMessage(content="Segunda consulta respondida.")]}]
        salida = io.StringIO()
        with patch.object(main, "app", app), \
             patch("builtins.input", side_effect=["TAC", "Hola", "salir"]), \
             contextlib.redirect_stdout(salida):
            main._bucle_consola()
        self.assertEqual(app.invoke.call_count, 2)
        self.assertIn("Segunda consulta respondida.", salida.getvalue())
        self.assertNotIn("ERROR TECNICO", salida.getvalue())
        self.assertNotIn("Traceback", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
