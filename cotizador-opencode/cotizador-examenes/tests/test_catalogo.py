import unittest
from unittest.mock import Mock, patch

from langchain_core.messages import HumanMessage

import main
from nodes.catalogo import nodo_catalogo
from schemas import ExamenCentro, SalidaRouter, Solicitud
from services.catalogo import consultar_catalogo, _metadatos


class CatalogoTests(unittest.TestCase):
    def test_ciudad_desde_direccion_y_nombre_comercial(self):
        fragmentos = [{"codigo_examen": "general", "texto":
                      "Nombre comercial: Oncomed.\nDirección: Calle 123, Providencia, Santiago."}]
        self.assertEqual(_metadatos(fragmentos, "123"), ("Oncomed", "Santiago"))

    def test_no_confunde_titulo_catalogo_con_nombre_del_centro(self):
        texto = ("Catálogo de exámenes\nDatos simulados\npágina 1\n"
                 "Centro Oftalmológico MiVisión\nDatos simulados\nCiudad: Talca · Especialidad: Oftalmología")
        self.assertEqual(_metadatos([{"codigo_examen": "general", "texto": texto}], "123"),
                         ("Centro Oftalmológico MiVisión", "Talca"))
        self.assertEqual(_metadatos([], "123"), ("Centro 123", None))

    def test_catalogo_lee_solo_centros_cargados_y_filtra_ciudad(self):
        client = Mock()
        client.scan_iter.return_value = [b"cotizador:examenes:123", b"cotizador:examenes:123"]
        examen = ExamenCentro(centro_id="123", codigo="TAC-1", nombre="TAC")
        with patch("services.catalogo.redis_store.cliente", return_value=client), \
             patch("services.catalogo.ingesta.cargar_examenes", return_value=[examen]) as cargar, \
             patch("services.catalogo.redis_store.obtener_fragmentos", return_value=[
                 {"codigo_examen": "general", "texto": "Nombre comercial: Centro.\nCiudad: Santiago", "fuente": "centro.pdf"}]):
            catalogo = consultar_catalogo("santiago")
            self.assertEqual(len(catalogo), 1)
            self.assertEqual(catalogo[0]["examenes"][0]["codigo"], "TAC-1")
            cargar.assert_called_once_with(client, "123")
            self.assertEqual(consultar_catalogo("Talca"), [])

    def test_catalogo_vacio_y_redis_caido_tienen_respuesta_breve(self):
        with patch("nodes.catalogo.consultar_catalogo", return_value=[]):
            salida = nodo_catalogo({"solicitud": Solicitud(ciudad="Talca")})
            self.assertIn("Talca", salida["messages"][0].content)
        with patch("nodes.catalogo.consultar_catalogo", side_effect=RuntimeError("detalle interno")):
            salida = nodo_catalogo({})
            self.assertNotIn("detalle interno", salida["messages"][0].content)
            self.assertEqual(salida["motivo_parada"], "catalogo_no_disponible")

    def test_grafo_catalogo_no_pide_prevision_ni_ejecuta_herramientas(self):
        router = Mock()
        router.invoke.return_value = SalidaRouter(ruta="catalogo")
        with patch("services.llm.llm_estructurado", return_value=router), \
             patch("nodes.catalogo.consultar_catalogo", return_value=[]) as catalogo, \
             patch.object(main, "nodo_agente") as agente, \
             patch.object(main, "nodo_respuesta_directa") as directo:
            app = main.build_graph()
            salida = app.invoke({"messages": [HumanMessage(content="¿Qué exámenes tienes y en qué ciudad?")]},
                                {"configurable": {"thread_id": "catalogo-test"}})
            catalogo.assert_called_once_with(None)
            agente.assert_not_called()
            directo.assert_not_called()
            self.assertEqual(salida["ruta"], "catalogo")


if __name__ == "__main__":
    unittest.main()
