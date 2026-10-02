# Objetivo

Quiero que generes un **documento en formato LaTeX (`.tex`)** que represente la información completa de un centro oftalmológico ubicado en la ciudad de **Talca, Chile**.

El documento combina **datos reales mínimos del centro** con **información completamente ficticia**, siguiendo estrictamente las reglas definidas a continuación.

> **Aviso para quien genera el documento:** las reglas de las secciones 1 y 2 son instrucciones internas. La distinción entre dato real y dato ficticio **no se escribe en el documento**: el `.tex` debe presentar todos los datos como los datos del centro, sin marcar, explicar ni declarar su origen.

---

# 1. Investigación web obligatoria

Antes de generar el documento debes realizar una búsqueda en Internet para identificar **un centro oftalmológico real ubicado en Talca, Chile**.

Utiliza fuentes públicas disponibles en la web.

Del centro real solamente puedes reutilizar los siguientes datos:

1. Nombre del centro.
2. Dirección.
3. Teléfono.

No debes reutilizar ningún otro dato real encontrado en Internet. Si durante la investigación encuentras información real sobre horarios, precios, servicios, convenios, WhatsApp, correos, profesionales, políticas o cualquier otro elemento, **descártala**: no debe aparecer en el documento.

### Regla de separación (instrucción interna)

**Datos que pueden ser reales:**

* nombre;
* dirección;
* teléfono.

**Datos que deben ser ficticios:**

* WhatsApp;
* correo electrónico;
* horarios;
* disponibilidad;
* precios;
* convenios;
* condiciones de atención;
* requisitos;
* preparación;
* duración;
* políticas;
* catálogo de exámenes;
* protocolos de atención;
* comportamiento conversacional;
* ejemplos de conversaciones;
* cualquier otro dato no incluido explícitamente entre los tres datos reales permitidos.

Estos tres datos reales se incorporan al documento **como los datos del centro**, sin ninguna marca, etiqueta, caja, color, nota al pie, encabezado o advertencia que los distinga del resto.

---

# 2. Lo que NO debe aparecer en el documento

Queda prohibido incluir en el `.tex`:

* Cualquier información o referencia a **"datos que sí son reales"**, "datos reales", "datos verificados en la web", "fuentes consultadas", "fuente web" o equivalentes.
* Cualquier información o referencia a **"datos ficticios"**, "información ficticia", "documento ficticio", "contenido ficticio", "simulado", "inventado", "de prueba" o equivalentes.
* Cajas, etiquetas, colores, marcas de agua, encabezados, pies de página o notas al pie cuyo propósito sea **distinguir o clasificar los datos según su origen** (real versus ficticio).
* Toda sección de tipo **"Qué es este documento y cómo hay que leerlo"**, es decir: propósito del documento, función dentro de un proyecto, para qué sirve, cómo se debe leer, cómo se generó.
* Una sección que explique la **regla de separación entre información real y ficticia**.
* Una sección de **convenciones de marcado** o leyenda de colores/etiquetas.
* Un **glosario del documento** o de sus metadatos.
* Una sección de **fuentes consultadas** o de **verificación de calidad** del documento.
* **Avisos, disclaimers o advertencias** sobre la relación del documento con el centro real.
* El sufijo **"(ficticio)"** o equivalentes en títulos, subtítulos, celdas, cajas, columnas o notas.
* Frases del tipo "este dato fue inventado", "no corresponde a la realidad", "el número no es real", "dominio reservado", "el buzón no existe", "profesional ficticio", "ningún profesional real", etc.

El documento debe leerse **como una fuente de datos del centro, nada más**: información general, políticas, catálogo de exámenes, disponibilidad, precios, protocolos de atención, comportamiento de atención y casos de prueba.

---

# 3. Información general del centro

Crea una sección con la información general del establecimiento.

Debe contener como mínimo:

### Identificación

* Nombre del centro.
* Dirección.
* Teléfono.
* Datos comerciales internos (nombre comercial, razón social, RUT, código de registro), sin ningún comentario sobre su origen.

### Resto de la información

* WhatsApp.
* Correo electrónico.
* Horarios.
* Días de atención.
* Horarios diferenciados, si corresponde, para determinados exámenes.
* Canales disponibles para consultas.
* Modalidades de atención.
* Anticipación recomendada para solicitar una hora.
* Condiciones generales de atención.
* Política de cancelación.
* Política de modificación de hora.
* Condiciones para pacientes que llegan atrasados.
* Documentación requerida.
* Órdenes médicas.
* Entrega de resultados.

---

# 4. Políticas y reglas del centro

Crea un conjunto de políticas para que el documento pueda utilizarse como una fuente realista de prueba. Incluye, como mínimo:

## 4.1 Política de cotización

Define:

* qué información necesita el centro para entregar un precio;
* cuándo necesita conocer la previsión;
* cuándo puede entregar un precio particular;
* qué ocurre si el usuario no indica su previsión;
* qué información puede quedar pendiente de confirmación.

## 4.2 Política de disponibilidad

Define:

* cómo se informa la disponibilidad;
* qué significa una hora disponible;
* cuánto tiempo se mantiene una hora;
* qué ocurre si una hora deja de estar disponible;
* qué información debe entregar el centro al consultar disponibilidad.

## 4.3 Política de reserva

La reserva estará fuera del alcance del agente del cotizador. Sin embargo, define:

* qué datos solicitaría el centro para reservar;
* en qué momento podría solicitar nombre;
* qué datos de contacto podría solicitar;
* qué información sería necesaria para confirmar una hora.

El agente del cotizador **no debe realizar reservas**.

## 4.4 Política de datos personales

Define que durante una simple cotización:

* no se requiere RUT;
* no se requieren datos personales sensibles;
* no se debe solicitar información innecesaria;
* los datos personales solamente podrían solicitarse en una etapa de reserva.

No utilices datos personales de personas reales como parte del contenido.

---

# 5. Catálogo de exámenes

Crea exactamente **3 exámenes oftalmológicos convencionales**.

Los exámenes deben ser plausibles y habituales en un centro oftalmológico, pero toda la información específica del centro debe ser creada para este documento.

Para cada examen incluye:

### Identificación

* Código.
* Nombre técnico.
* Nombre común.
* Posibles formas coloquiales en que un usuario podría solicitarlo.
* Categoría.

### Descripción

* Qué es.
* Para qué sirve.
* Qué información permite obtener.
* En qué situaciones una persona podría solicitarlo.

### Requisitos

* Si requiere orden médica.
* Si requiere ayuno.
* Si requiere preparación previa.
* Si requiere suspender o modificar alguna actividad.
* Consideraciones sobre lentes de contacto.
* Si requiere acompañante.
* Si existe alguna consideración especial para adultos mayores.
* Otras condiciones relevantes.

### Atención

* Duración aproximada.
* Modalidad.
* Horarios disponibles.
* Días disponibles.
* Anticipación requerida para solicitar hora.
* Capacidad diaria, si es relevante.

### Precios

Incluye:

* precio particular;
* precio Fonasa;
* precio Isapre;
* precio mediante convenio.

No hagas que todos los exámenes tengan necesariamente las mismas condiciones de precio. El comportamiento debe ser suficientemente variado.

### Resultados

Indica:

* qué tipo de resultado se entrega;
* formato del resultado;
* plazo de entrega;
* si incluye informe;
* si incluye imágenes;
* si existe alguna recomendación posterior.

### Recomendaciones

Incluye:

* recomendaciones antes del examen;
* recomendaciones durante el examen;
* recomendaciones después del examen;
* situaciones en que el paciente debería consultar previamente al centro.

### Conducción y acompañamiento

Indica explícitamente si:

* el paciente puede conducir después;
* podría recomendarse acompañante;
* existe alguna condición que modifique esta recomendación.

---

# 6. Variabilidad de la información

No diseñes los tres exámenes utilizando exactamente la misma estructura lógica.

La información debe presentar variabilidad. Por ejemplo:

* un examen puede no requerir orden médica;
* otro puede requerirla;
* uno puede tener preparación especial;
* otro puede no requerir preparación;
* uno puede tener disponibilidad todos los días;
* otro puede tener disponibilidad limitada;
* uno puede requerir acompañante solamente en determinadas circunstancias;
* otro puede no requerirlo.

El objetivo es generar una fuente suficientemente rica para probar la capacidad de razonamiento y adaptación.

---

# 7. Formato LaTeX

El resultado final debe ser un documento `.tex` completo y compilable.

Utiliza una estructura profesional, por ejemplo:

* `\documentclass`;
* paquetes necesarios;
* portada;
* tabla de contenidos;
* secciones;
* subsecciones;
* tablas;
* cajas, cuando aporten claridad al contenido del centro (por ejemplo, advertencias de preparación o resúmenes de precios), pero **nunca** para clasificar los datos según su origen;
* ejemplos de conversaciones;
* tablas de precios;
* tablas de disponibilidad;
* casos de prueba.

Evita utilizar paquetes innecesarios. El documento debe compilar correctamente en un entorno LaTeX estándar.

Finalmente, guarda el resultado como:

`centro_oftalmologico_talca_ficticio.tex`

---

# 8. Criterios de calidad

Estos criterios se verifican para decidir si el documento está listo. **No deben escribirse dentro del documento.**

* existe un centro oftalmológico real de Talca;
* nombre, dirección y teléfono provienen de una fuente web pública;
* esos son los únicos datos reales utilizados;
* todo el resto de la información fue creada para este documento;
* existen exactamente tres exámenes;
* los tres exámenes contienen información suficiente para una cotización;
* existen precios, disponibilidad, requisitos y recomendaciones;
* existen políticas;
* no hay datos personales de personas reales;
* la información es consistente entre las distintas secciones;
* el documento compila correctamente;
* **el documento no menciona en ninguna parte que un dato sea real o ficticio, ni incluye leyendas, cajas, colores, encabezados o secciones que los clasifiquen**;
* **el documento no incluye una sección que explique qué es el documento, para qué sirve, cómo leerlo, cómo se generó, de dónde provienen los datos, ni su propósito o alcance**.
