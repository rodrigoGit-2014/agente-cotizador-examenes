# Objetivo

Quiero que generes un **documento en formato LaTeX (`.tex`)** que represente la información completa de un **centro de salud que realiza exámenes**, ubicado en Chile, según los parámetros de la sección 0.

El documento combina **datos reales mínimos del centro** con **información completamente ficticia**, siguiendo estrictamente las reglas definidas a continuación.

> **Aviso para quien genera el documento:** las reglas de las secciones 0, 1, 2, 6 y 8 son instrucciones internas. La distinción entre dato real y dato ficticio **no se escribe en el documento**: el `.tex` debe presentar todos los datos como los datos del centro, sin marcar, explicar ni declarar su origen.

---

# 0. Parámetros

Los parámetros se toman del mensaje del usuario. Por ejemplo: *"un centro radiológico ubicado en Santiago, Ñuñoa"* o *"un centro oftalmológico en Talca, con estos exámenes: …"*.

| Parámetro | Obligatorio | Ejemplo | Si no se indica |
|---|---|---|---|
| Especialidad del centro | Sí | oftalmología, radiología, laboratorio clínico | Pregúntala antes de comenzar |
| Ciudad | Sí | Talca, Santiago | Pregúntala antes de comenzar |
| Comuna o sector | No | Ñuñoa | Cualquier comuna de la ciudad |
| Centro específico | No | nombre de un centro concreto | Elige un centro real de la especialidad en esa ciudad |
| Exámenes | No | lista de exámenes, por nombre o por descripción | Crea 3 exámenes habituales de la especialidad (ver sección 5) |

Si falta un parámetro obligatorio, **pregunta antes de generar**. No supongas la especialidad ni la ciudad.

En el resto de este prompt, "la especialidad", "la ciudad" y "la comuna" se refieren a estos parámetros.

---

# 1. Investigación web obligatoria

Antes de generar el documento debes realizar una búsqueda en Internet para identificar **un centro real de la especialidad, ubicado en la ciudad (y en la comuna, si se indicó)**. Si se indicó un centro específico, búscalo a él.

Utiliza fuentes públicas disponibles en la web.

Del centro real solamente puedes reutilizar los siguientes datos:

1. Nombre del centro.
2. Dirección.
3. Teléfono.

El teléfono debe escribirse **exactamente como aparece en la fuente pública**, en formato internacional (por ejemplo, `+56 71 223 2252`), porque se usa para identificar al centro.

Si no encuentras un centro real que cumpla los parámetros, **no generes el documento**: informa que no lo encontraste y sugiere ampliar la comuna o la ciudad. No inventes un centro.

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
* Cualquier mención a un **agente, cotizador, asistente, simulador, sistema automatizado** o a quien consulta el documento. El documento habla solo del centro y de sus pacientes.
* **Patrones de comportamiento conversacional** del centro (por ejemplo, listas de formas de responder, códigos de patrón o guiones de atención telefónica).
* **Ejemplos de conversaciones** o diálogos, y respuestas esperadas de quien consulta.
* **Listas de comportamientos que un tercero no debe seguir**, errores típicos o fallos posibles.
* **Esquemas de datos**, listas de campos, tipos de dato o formatos de salida de una cotización.
* **Casos de prueba**, expectativas o criterios de evaluación.
* **Horas o fechas concretas de agenda** (por ejemplo, "el próximo cupo es el jueves 12 a las 09:30"). El documento define reglas de horario y anticipación, no cupos disponibles en una fecha determinada.
* **Referencias a contenido que no existe en el documento**, como "los ejemplos de este documento", "ver anexo" o "como se muestra más abajo", si ese contenido no está.

El documento debe leerse **como una fuente de datos del centro, nada más**: información general, políticas, catálogo de exámenes, reglas de disponibilidad, precios y protocolos de atención.

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

Crea un conjunto de políticas del centro. Incluye, como mínimo:

## 4.1 Política de cotización

Define:

* qué información necesita el centro para entregar un precio;
* cuándo necesita conocer la previsión;
* cuándo puede entregar un precio particular;
* qué ocurre si el paciente no indica su previsión;
* qué información puede quedar pendiente de confirmación.

## 4.2 Política de disponibilidad

Define:

* cómo se informa la disponibilidad;
* qué significa una hora disponible;
* cuánto tiempo se mantiene una hora;
* qué ocurre si una hora deja de estar disponible;
* qué información debe entregar el centro al consultar disponibilidad.

## 4.3 Política de reserva

Define, desde el punto de vista del centro:

* qué datos solicita el centro para reservar;
* en qué momento solicita el nombre del paciente;
* qué datos de contacto solicita;
* qué información es necesaria para confirmar una hora.

## 4.4 Política de datos personales

Define que durante una simple cotización:

* no se requiere RUT;
* no se requieren datos personales sensibles;
* no se solicita información innecesaria;
* los datos personales solamente se solicitan en la etapa de reserva.

No utilices datos personales de personas reales como parte del contenido.

---

# 5. Catálogo de exámenes

### Qué exámenes incluir

* **Si el usuario entregó una lista de exámenes**, inclúyelos. Si un examen se entregó con una descripción o un propósito, respétalos: el examen del documento debe ser ese examen, no otro con un nombre parecido.
* **Si no la entregó**, crea **3 exámenes habituales de la especialidad**, plausibles para un centro de ese tipo.

Cada examen lleva un **código interno del centro**, único dentro del documento, con el formato que prefieras (por ejemplo, `OFT-GLU-002`). No es necesario que coincida con códigos de otros centros.

Toda la información específica del centro para cada examen (requisitos, precios, horarios, preparación, etc.) debe ser creada para este documento.

### Descripción precisa de cada examen

La descripción de cada examen se usa para decidir si corresponde a lo que necesita un paciente, por lo que debe ser **inequívoca**:

* di con precisión qué se mide o se observa y para qué sirve, de modo que no pueda confundirse con otro examen de nombre parecido (por ejemplo, distingue claramente una medición de la graduación de una medición de la curvatura de la córnea);
* el nombre técnico, el nombre común, las formas coloquiales y la descripción deben referirse al mismo examen;
* no incluyas formas coloquiales que correspondan a otro examen.

### Estructura de cada examen

Para cada examen, usa **exactamente los siguientes títulos de subsección, en este orden**: Identificación, Descripción, Requisitos, Atención, Precios, Resultados, Recomendaciones, Conducción y acompañamiento.

### Identificación

* Código interno del centro.
* Nombre técnico.
* Nombre común.
* Posibles formas coloquiales en que un paciente podría solicitarlo.
* Categoría.

### Descripción

* Qué es.
* Para qué sirve.
* Qué información permite obtener.
* En qué situaciones una persona podría solicitarlo.

### Requisitos

* Si requiere orden médica, y si eso cambia según la modalidad de pago.
* Si requiere ayuno.
* Si requiere preparación previa.
* Si requiere suspender o modificar alguna actividad o medicamento.
* Consideraciones propias de la especialidad (por ejemplo, lentes de contacto en oftalmología; embarazo, implantes metálicos, medio de contraste o claustrofobia en radiología).
* Si requiere acompañante.
* Si existe alguna consideración especial para adultos mayores.
* Otras condiciones relevantes.

Cada requisito debe tener una justificación clínica plausible para ese examen. No agregues requisitos que no tengan sentido para el examen (por ejemplo, ayuno donde no aplica).

### Atención

* Duración aproximada.
* Modalidad.
* Horarios disponibles.
* Días disponibles.
* Anticipación requerida para solicitar hora.
* Capacidad diaria, si es relevante.

### Precios

Incluye, en una tabla:

* precio particular;
* precio Fonasa;
* precio Isapre;
* precio mediante convenio.

Escribe los montos siempre en el mismo formato (por ejemplo, `$ 45.000`). No hagas que todos los exámenes tengan necesariamente las mismas condiciones de precio. El comportamiento debe ser suficientemente variado.

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

Al final del catálogo puedes incluir una **tabla resumen comparativa** de los exámenes, sin comentarios sobre errores posibles ni sobre cómo interpretarla.

---

# 6. Variabilidad de la información (instrucción interna)

No diseñes los exámenes utilizando exactamente la misma estructura lógica.

La información debe presentar variabilidad. Por ejemplo:

* un examen puede no requerir orden médica;
* otro puede requerirla siempre;
* otro puede requerirla solo según la modalidad de pago;
* uno puede tener preparación especial;
* otro puede no requerir preparación;
* uno puede tener disponibilidad todos los días;
* otro puede tener disponibilidad limitada;
* uno puede requerir acompañante solamente en determinadas circunstancias;
* otro puede no requerirlo.

Esta sección es una instrucción para quien genera el documento: no escribas en el `.tex` que la información fue diseñada con variabilidad ni para qué.

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
* tablas de precios;
* tablas de horarios y reglas de disponibilidad.

El texto del PDF compilado debe poder **extraerse sin errores** (copiar y pegar debe producir las mismas palabras). Para eso:

* usa `\usepackage[T1]{fontenc}`, `\usepackage{lmodern}` y `\usepackage[utf8]{inputenc}`;
* incluye `\usepackage{cmap}` antes de `fontenc` y `\pdfgentounicode=1` con `\input{glyphtounicode}`;
* desactiva las ligaduras tipográficas (por ejemplo, con `\usepackage{microtype}` y `\DisableLigatures{encoding = *, family = *}`), para que palabras como "confirmar" o "firma" no pierdan letras al extraer el texto;
* escribe las letras acentuadas y la ñ **directamente como caracteres UTF-8 precompuestos** (á, é, í, ó, ú, ü, ñ). No uses comandos de acento como `\'u` o `\~n`, ni combines una letra con un acento separado.

Evita utilizar paquetes innecesarios. El documento debe compilar correctamente en un entorno LaTeX estándar con `pdflatex`.

Guarda el resultado con este nombre, en minúsculas, sin tildes y con guiones bajos:

`centro_<especialidad>_<ciudad>_<comuna>.tex` (omite `<comuna>` si no se indicó).

Por ejemplo: `centro_oftalmologia_talca.tex` o `centro_radiologia_santiago_nunoa.tex`.

---

# 8. Revisión de consistencia antes de entregar (instrucción interna)

Antes de entregar el documento, revísalo completo y corrige todo lo que no cumpla. Esta revisión **no se escribe dentro del documento**.

### Datos repetidos

Todo dato que aparezca en más de una sección debe ser **idéntico** en todas. Revisa en especial:

* precios por modalidad (detalle del examen, políticas y tabla resumen);
* exigencia de orden médica por examen y por modalidad (sección de órdenes médicas, requisitos, precios y tabla resumen);
* recomendación u obligación de acompañante, también para menores de edad (requisitos, conducción y acompañamiento, y tabla resumen): si una sección dice que algo "se requiere", ninguna otra puede decir que "se sugiere" o "no se exige";
* días, horarios y anticipación de cada examen (información general, horarios diferenciados, atención y tabla resumen);
* duración, plazo de resultados e inclusión de imágenes.

La tabla resumen se construye **al final**, copiando los valores del detalle de cada examen, nunca al revés.

### Coherencia lógica

* Toda justificación que mencione un número debe coincidir con los números del documento (por ejemplo, si una política dice que dos precios difieren en menos de cierto monto, la diferencia real debe cumplirlo).
* Las condiciones no deben anularse entre sí (por ejemplo, no exigir orden médica para una modalidad que no cubre el examen y se cobra como particular, si el particular no exige orden).
* El nombre técnico de cada examen debe ser coherente con su descripción y con la técnica real que describe.
* No debe haber referencias a contenido que no existe en el documento.

### Ortografía

* Todas las palabras llevan sus tildes correctas (por ejemplo, "común", "imágenes", "ningún", "sábados", "recién", "último").
* No hay palabras repetidas ni errores de tipeo.

---

# 9. Criterios de calidad

Estos criterios se verifican para decidir si el documento está listo. **No deben escribirse dentro del documento.**

* los parámetros obligatorios (especialidad y ciudad) fueron indicados por el usuario o preguntados;
* existe un centro real de la especialidad en la ciudad (y comuna, si se indicó);
* nombre, dirección y teléfono provienen de una fuente web pública, y el teléfono está escrito tal como aparece en ella;
* esos son los únicos datos reales utilizados;
* todo el resto de la información fue creada para este documento;
* los exámenes son los indicados por el usuario, respetando su descripción si se entregó, o son 3 exámenes habituales de la especialidad;
* cada examen tiene un código interno único dentro del documento;
* la descripción de cada examen es inequívoca y coherente con su nombre técnico, su nombre común y sus formas coloquiales;
* cada examen usa los mismos títulos de subsección, en el mismo orden;
* los exámenes contienen información suficiente para una cotización;
* existen precios, reglas de disponibilidad, requisitos y recomendaciones;
* existen políticas;
* no hay datos personales de personas reales;
* se cumplió la revisión de consistencia de la sección 8;
* el documento compila correctamente y su texto se extrae sin letras perdidas ni acentos duplicados;
* el documento no contiene patrones conversacionales, ejemplos de conversaciones, esquemas de campos, casos de prueba ni horas concretas de agenda;
* el documento no menciona agentes, cotizadores, simuladores ni a quien lo consulta;
* **el documento no menciona en ninguna parte que un dato sea real o ficticio, ni incluye leyendas, cajas, colores, encabezados o secciones que los clasifiquen**;
* **el documento no incluye una sección que explique qué es el documento, para qué sirve, cómo leerlo, cómo se generó, de dónde provienen los datos, ni su propósito o alcance**.