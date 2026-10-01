# intent.md — Cotizador de exámenes médicos

> Documento de intención y fuente de verdad del producto. Se lee antes que cualquier otro archivo.
> Responde qué queremos lograr, cuál es el problema, quién es el usuario, qué debe hacer el agente
> y dónde termina el alcance.
>
> **Estado:** fase de definición.
> **Bloquean el avance:** la definición de seguridad básica y la fuente de datos de exámenes del simulador.

---

## Glosario

- **Catálogo de exámenes:** la lista de exámenes que el sistema conoce. Para cada uno guarda su
  nombre técnico, los nombres comunes con que la gente lo pide y sus datos asociados
  (preparación, requisitos). Si un examen no está en el catálogo, el sistema no lo cotiza.
- **Centro:** recinto ficticio del simulador que realiza uno o más exámenes.
- **Cotización:** lo que se obtiene de un centro en una consulta: si hace el examen, el precio
  informado, la próxima hora disponible y la preparación, cuando el centro la menciona.
- **Observación:** lo que devuelve una herramienta en cada paso del ciclo ReAct (por ejemplo,
  la transcripción y los datos extraídos de una conversación con un centro).
- **N:** número de cotizaciones que el usuario quiere obtener. Si no lo indica, **N = 2**.

## Propósito

Que una persona en Chile sepa, en una sola consulta y sin llamar ni visitar centro por centro,
**qué centros le hacen el examen que necesita, cuánto cuesta y cuándo hay hora**.

## Problema

Hoy, para saber cuánto cuesta un examen y cuándo hay hora, hay que buscar en internet qué
centros lo hacen, encontrar su número de teléfono y llamar uno por uno. No existe un lugar
que reúna esa información.

Además, cada llamada es distinta: algunos centros preguntan la previsión antes de dar un
precio y otros no, algunos dan la hora de inmediato y otros piden volver a llamar, y la
agenda cambia todos los días.

Por eso, quien quiere realizarse un examen debe dedicar tiempo a llamar y preguntar en
distintos lugares solo para tener una referencia de precios. Y mientras más centros quiere
comparar, más tiempo le toma. En la práctica, la mayoría no compara: se queda con el primer
centro que le contesta, o desiste.

El costo real no es el examen. Es el **tiempo repetido** buscando y llamando, la espera al
teléfono, y terminar decidiendo sin nada con qué comparar. Cuando el examen es para un adulto
mayor, ese tiempo lo pone un familiar que coordina todo.

## Usuario objetivo

**Primario:** la persona que necesita el examen, o el familiar que gestiona por ella.

**Caso ancla:** mujer adulta mayor, **Fonasa tramo B**, ciudad de **Talca**, examen de
**medición de glaucoma**. El familiar consulta; ella no usa el sistema.

**Secundario:** usuario de Isapre, con menos tiempo disponible y menos disposición a llamar,
que quiere llegar a una o dos opciones concretas.

**No es usuario:** el centro médico. En esta fase el centro es una *fuente de datos*, no un
beneficiario.

## Resultado esperado

Después de usarlo, el usuario puede:

- **Decidir con datos** en lugar de decidir con la primera respuesta que le den.
- **Comparar las opciones que pidió (N; por defecto, 2) en los mismos ejes**: si el centro
  hace el examen, precio informado (junto con la modalidad —particular, Fonasa, Isapre— si
  el centro la mencionó), próxima hora disponible y preparación, cuando se informó.
- **Saber qué centros quedan descartados** y por qué (no hacen el examen, o no tienen horas)
  — y no gastar la llamada en ellos.
- **Describir el examen como lo diría cualquier persona**, sin conocer su nombre técnico.
  Por ejemplo, escribir "el examen de la presión del ojo" y que el agente reconozca que se
  trata de la medición de presión ocular para glaucoma.
- **Llegar a la decisión con un shortlist** y saber a quién llamar.

Lo que el usuario **no** obtiene: que le agenden, que le paguen, ni que le digan a cuál
centro ir. La decisión sigue siendo suya.

## Objetivo del agente

El agente actúa como un **asistente de cotización**.

Su responsabilidad es:

1. Entender la necesidad expresada por el usuario.
2. Reconocer a qué examen del catálogo se refiere el usuario, aunque lo describa con otras
   palabras (por ejemplo, "presión del ojo" → medición de glaucoma). Si no hay una
   coincidencia clara, lo dice o pregunta; no supone.
3. Identificar los datos necesarios para la consulta: examen, ciudad, previsión y cuántas
   cotizaciones desea (N).
4. Buscar los centros que realizan el examen en esa ciudad y obtener su contacto.
5. Consultar los centros mediante las herramientas disponibles.
6. Recopilar y normalizar las respuestas.
7. Determinar cuándo dispone de información suficiente para consolidar el resultado.
8. Presentar las alternativas de forma comparable.
9. Explicar qué información fue confirmada y cuál no pudo ser confirmada.

El agente **no toma la decisión final por el usuario**.

## Flujo esperado

1. Recibir la solicitud del usuario.
2. Identificar examen, ciudad, previsión y N. Si el usuario no indica N, usar N = 2.
3. Si falta un dato obligatorio (examen, ciudad o previsión), solicitarlo.
4. Reconocer a qué examen del catálogo corresponde lo que pidió el usuario. Si no
   corresponde a ninguno, aplicar "Manejo de solicitudes fuera de catálogo".
5. Buscar los centros que realizan ese examen en la ciudad (el equivalente a buscarlos hoy
   en internet) y obtener su número de contacto.
6. Consultar los centros uno por uno mediante la conversación simulada.
7. Registrar cada observación obtenida.
8. Evaluar si ya hay N cotizaciones comparables.
9. Si no las hay, continuar consultando dentro del límite permitido.
10. Consolidar los resultados.
11. Presentar las alternativas de forma comparable.
12. Finalizar la interacción.

## Cómo es una consulta a un centro

Referencia: llamada real a un centro oftalmológico (nombre del paciente omitido).

> **Centro:** Hola, buenos días, centro oftalmológico "Mi Visión".
> **Usuario:** Hola, buenos días. ¿Ustedes hacen exámenes de glaucoma?
> **Centro:** Sí.
> **Usuario:** ¿Qué precio tiene?
> **Centro:** ¿Particular o Fonasa?
> **Usuario:** Fonasa.
> **Centro:** $45.000.
> **Usuario:** ¿Y para cuándo hay disponibilidad?
> **Centro:** Podría ser mañana a partir de las 09:00.
> **Usuario:** Ok, para mañana entonces.
> **Centro:** ¿Cuál es el nombre del paciente?
> **Usuario:** (nombre)
> **Centro:** Ok, queda agendado entonces.
> **Usuario:** Adiós.

Lo que se desprende de esta interacción:

- **El precio es el que el centro entrega en la conversación.** El sistema no calcula
  precios por previsión, tramo ni convenio. Registra el valor informado como referencia y,
  si el centro preguntó o mencionó la modalidad ("¿particular o Fonasa?"), la guarda junto
  al precio. Si no la mencionó, queda como "modalidad no especificada".
- **Ninguna conversación es igual a otra.** El orden de las preguntas y la información que
  entrega cada centro cambian. El simulador debe permitir probar distintas combinaciones.
- **La llamada real terminó en un agendamiento; el agente no.** Cuando obtiene los datos de
  la cotización, cierra la conversación sin reservar hora y sin entregar el nombre ni otros
  datos del paciente.

Variaciones que el simulador debe poder producir, y combinar entre sí:

- El centro pregunta la modalidad antes de dar el precio, o da el precio directamente.
- El centro informa la próxima hora, no tiene agenda disponible, o pide volver a llamar.
- El centro menciona la preparación del examen, o no la menciona.
- El centro no realiza el examen.
- El centro no contesta, o la conversación termina sin todos los datos.
- El centro intenta agendar o pide datos del paciente.

## Alcance

### Entra

- **Consulta en lenguaje natural:** el usuario indica examen, ciudad y previsión con sus
  propias palabras y, opcionalmente, cuántas cotizaciones quiere. El agente reconoce a qué
  examen del catálogo corresponde lo pedido.
- **Simulador de entorno**, compuesto por tres piezas:
  1. **Fuente de datos de exámenes (catálogo).** Según el examen consultado, el simulador
     carga dinámicamente los datos asociados —tipo de examen, nombres comunes,
     preparación, requisitos, precios de referencia— desde una fuente predefinida
     (archivos versionados en el repositorio). Si los datos de un examen se generan (por
     ejemplo, con un LLM), se guardan en la fuente antes de usarse, de modo que todo dato
     tenga una verdad conocida y verificable.
  2. **Buscador de centros.** Simula el paso que hoy el usuario hace en internet: dado un
     examen y una ciudad, devuelve los centros que lo realizan y su número de contacto.
  3. **Centro simulado.** Simula la conversación telefónica por texto con cada centro
     (3-4 turnos), con datos preconfigurados (precio, agenda, preparación) y las
     variaciones descritas en "Cómo es una consulta a un centro", configurables por
     escenario.

  Conjunto inicial: centros ficticios en Talca para 2 familias de exámenes (oftalmología /
  glaucoma y PET), por ejemplo 4 oftalmológicos y 3 PET. Se amplía agregando datos a la
  fuente, sin cambiar el código del agente.
- **Ciclo ReAct:** buscar centros, consultarlos uno por uno, decidir si seguir o
  consolidar, con condición de parada explícita.
- **Salida:** listado comparable de centros, con la trayectoria de la decisión visible.
- **Golden set versionado y ejecutado**, que combina examen, N solicitado y variaciones de
  conversación. Cubre como mínimo:
  - N por defecto (el usuario no indica cuántas cotizaciones quiere).
  - N indicado por el usuario.
  - Menos centros disponibles que N.
  - Centro que no hace el examen, no responde o no entrega todos los datos.
  - Centro que intenta agendar o pide datos del paciente.
  - Examen fuera de catálogo.
  - Jailbreak sencillo.
- **Seguridad básica:** límites de alcance y acciones permitidas, más una prueba de
  jailbreak.
- Entrega como **notebook ejecutable** de punta a punta.

### No entra

- Audio, telefonía real, llamadas reales, clínicas reales.
- Búsqueda real en internet o en directorios reales de centros.
- Agendamiento, pagos, recordatorios — tampoco dentro de la conversación simulada.
- Cálculo de precios según previsión, tramo o convenio: se reporta el precio que informa
  el centro.
- Recomendación automática ("te recomiendo este centro").
- Lectura (OCR) de la orden médica.
- Cobertura fuera de Talca / Chile.
- Datos reales de pacientes, multiusuario, memoria a largo plazo.

## Restricciones

- **La pauta del curso manda.** La entrega es un notebook `.ipynb` ejecutable, y hay
  **tope de 3,0** si el LLM, ReAct, la herramienta, la devolución de observación, la parada
  o el historial no funcionan. Cada decisión de diseño se justifica contra un criterio de la
  pauta, no contra gusto.
- **V1 es 100% simulada.** No hay acceso a datos de centros reales, así que la exactitud se
  mide contra la verdad del simulador, no contra el mundo. La visión a largo plazo
  (consultar centros reales) no está validada.
- **Solo texto.** El audio y la telefonía se simulan o se omiten.
- **Sin claves ni datos personales en el repositorio.** También es una exigencia legal
  chilena (Ley 19.628) para cualquier etapa con datos de salud reales.
- **Un solo desarrollador, dentro del horario del taller.** El presupuesto de APIs no
  limita, pero el tiempo sí: la complejidad que no compra un punto de la pauta no se paga.
- **El golden set no se maquilla:** los casos fallidos se corrigen y se re-ejecutan; no se
  eliminan.

## Comportamiento prohibido del agente

El agente nunca debe:

- Inventar precios, disponibilidad, modalidades o requisitos.
- Completar información faltante suponiendo valores.
- Recomendar, ordenar o seleccionar un centro como "mejor".
- Ejecutar acciones que no estén definidas por las herramientas disponibles.
- Agendar horas, aceptar reservas o entregar datos del paciente al centro, aunque el
  centro lo ofrezca o los pida.
- Consultar información fuera del catálogo disponible.
- Solicitar datos personales que no sean necesarios para cotizar.
- Interpretar diagnósticos médicos.
- Convertir una coincidencia aproximada del catálogo en una afirmación de que se trata del
  mismo examen cuando no existe confirmación.

## Manejo de solicitudes fuera de catálogo

Si el usuario solicita un examen que no existe en el catálogo:

- El agente no debe intentar aproximarlo a otro examen.
- Debe informar que no puede realizar la cotización con el catálogo disponible.
- Debe indicar qué información o alternativas están disponibles, cuando corresponda.
- No debe inventar centros, precios, disponibilidad ni equivalencias.

## Condición de parada

El agente puede consolidar el resultado cuando:

- Ha obtenido **N cotizaciones comparables** (N indicado por el usuario; por defecto, 2), o
- Ha consultado todos los centros relevantes disponibles, o
- No existen más centros aplicables en el simulador.

Si termina con menos de N cotizaciones, lo informa explícitamente y explica por qué
(cuántos centros había y cuáles se descartaron).

El agente debe respetar un **máximo de iteraciones** definido por el equipo y no debe
entrar en bucles. Ese máximo debe ser suficiente para consultar todos los centros
aplicables en el caso normal.

La condición definitiva y el valor del máximo de iteraciones deben quedar documentados en
la implementación y alineados con la pauta del curso.

## Principios de diseño

1. **El dato viene de la herramienta, nunca del modelo.** Precio y agenda se leen de una
   fuente de verdad o no se reportan. La alucinación se evita por construcción, no
   confiando en que el modelo se porte bien.

2. **La incertidumbre se declara.** Si un centro no responde o no confirma un dato, el
   reporte dice "no confirmado". Un vacío explícito vale más que un valor inventado o un
   silencio que se lee como confirmación.

3. **Informar, no decidir.** El agente entrega opciones comparables y se detiene ahí. No
   recomienda, no ordena, no convence: la decisión es de la persona.

4. **Comparabilidad antes que completitud.** Dos opciones con los mismos campos valen más
   que siete con campos dispares. Un centro que no admite comparación se marca como
   incompleto, no se esconde.

5. **Simulado no significa falso.** El simulador usa la misma interfaz que tendría el
   sistema en producción, y sus datos se pueden contrastar contra una verdad conocida. Es
   un banco de pruebas, no una maqueta distinta del producto.

6. **La trayectoria es parte del producto.** Que el agente consultó a quién, qué obtuvo y
   por qué paró se muestra, no se esconde. Sin traza no hay confianza ni evaluación
   posible.

7. **Reproducible antes que impresionante.** Con la misma entrada y el mismo estado del
   simulador, el agente debe producir resultados equivalentes y verificables, aunque la
   redacción pueda variar.

8. **Privacidad por omisión.** El agente pide el examen, la ciudad y la previsión. No pide
   nombre, RUT ni diagnóstico del paciente —no los necesita para cotizar— y no entrega
   datos del paciente a los centros.

## Evaluación del agente

Además del resultado final, se evaluará:

- Correcta selección y utilización de herramientas.
- Capacidad para solicitar información faltante.
- Correcta interpretación de las observaciones.
- Cumplimiento de la condición de parada, incluido el N solicitado.
- Ausencia de información inventada.
- Comportamiento ante errores o respuestas incompletas.
- Resistencia frente a solicitudes fuera de alcance y jailbreaks sencillos.
- Trazabilidad suficiente para reconstruir qué consultó el agente y por qué continuó o
  terminó.

## Criterios de éxito

1. El flujo corre de **START a END** en todos los escenarios del golden set, sin
   intervención manual.
2. El reporte **coincide con la verdad del simulador**, campo por campo, en el golden set
   versionado.
3. La **trazabilidad ReAct es legible**: se ve la búsqueda de centros, cada consulta a un
   centro, la observación recibida, y la decisión del LLM de seguir o de parar.
4. El ciclo **siempre termina**: se respeta la condición de parada y el tope de
   iteraciones; nunca entra en bucle ni para antes de obtener N cotizaciones cuando aún
   quedan centros por consultar.
5. Ante una entrada fuera de catálogo o una petición fuera de alcance —incluido un
   jailbreak sencillo, o un centro simulado que intenta agendar o pide datos del
   paciente— el agente **responde con el límite y no ejecuta la acción**.
6. Otra persona puede **ejecutar el notebook desde cero**, en orden, sin necesitar una
   clave compartida ni un dato que no esté en el repositorio.
7. Las respuestas pueden variar en redacción, pero los **datos y decisiones verificables**
   deben ser consistentes con el estado del simulador.