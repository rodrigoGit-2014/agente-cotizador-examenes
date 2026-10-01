# intent.md — Cotizador de exámenes médicos

> Documento de intención y fuente de verdad del producto. Se lee antes que cualquier otro archivo.
> Responde qué queremos lograr, cuál es el problema, quién es el usuario, qué debe hacer el agente
> y dónde termina el alcance.
>
> **Estado:** fase de definición.
> **Bloquean el avance:** la definición de seguridad básica y el catálogo de exámenes del simulador.

---

## Propósito

Que una persona en Chile sepa, en una sola consulta y en menos de un minuto,
**qué centros le hacen el examen que necesita, cuánto cuesta y cuándo hay hora**,
sin llamar ni visitar centro por centro.

## Problema

Conocer el precio y la disponibilidad de un examen médico exige contactar
**centro por centro**, por teléfono o presencialmente. No existe un lugar donde
esa información esté publicada de forma uniforme: el precio cambia según la
previsión y el convenio, los requisitos cambian según el recinto, y la agenda
cambia todos los días.

Quien necesita el examen **no puede comparar nada** hasta haber invertido el
esfuerzo varias veces. Y como el costo crece con el número de opciones —que es
justo lo que hace falta para elegir bien— en la mayoría de los casos no se
compara: se queda con la primera respuesta que obtiene, o se rinde.

El costo real no es el examen. Es el **tiempo repetido**, la espera al teléfono,
y decidir sin datos con los que comparar. Y cuando el examen es para un adulto
mayor, ese costo lo paga un tercero que coordina todo.

## Usuario objetivo

**Primario:** la persona que necesita el examen, o el familiar que gestiona por
ella.

**Caso ancla:** mujer adulta mayor, **Fonasa tramo B**, ciudad de **Talca**,
examen de **medición de glaucoma**. El familiar consulta; ella no usa el
sistema.

**Secundario:** usuario de Isapre, con menos tiempo disponible y menos
disposición a llamar, que quiere llegar a una o dos opciones concretas.

**No es usuario:** el centro médico. En esta fase el centro es una *fuente de
datos*, no un beneficiario.

## Resultado esperado

Después de usarlo, el usuario puede:

- **Decidir con datos** en lugar de decidir con la primera respuesta que le den.
- **Comparar tres o más opciones en los mismos ejes**: qué examen hace cada
  centro, precio, si hay convenio con su previsión, y cuándo es la próxima hora.
- **Saber qué centros quedan descartados** y por qué (no hacen el examen, o no
  tienen horas) — y no gastar la llamada en ellos.
- **Preguntar con sus propias palabras**, sin aprender el vocabulario del
  catálogo de exámenes.
- **Llegar a la decisión con un shortlist** y saber a quién llamar.

Lo que el usuario **no** obtiene: que le agenden, que le paguen, ni que le
digan a cuál centro ir. La decisión sigue siendo suya.

## Objetivo del agente

El agente actúa como un **asistente de cotización**.

Su responsabilidad es:

1. Entender la necesidad expresada por el usuario.
2. Identificar el examen correspondiente en el catálogo.
3. Identificar los datos necesarios para realizar la consulta.
4. Consultar los centros mediante las herramientas disponibles.
5. Recopilar y normalizar las respuestas.
6. Determinar cuándo dispone de información suficiente para consolidar el resultado.
7. Presentar las alternativas de forma comparable.
8. Explicar qué información fue confirmada y cuál no pudo ser confirmada.

El agente **no toma la decisión final por el usuario**.

## Flujo esperado

1. Recibir la solicitud del usuario.
2. Identificar examen, ubicación y previsión.
3. Si falta un dato obligatorio, solicitarlo.
4. Traducir la solicitud al catálogo de exámenes.
5. Seleccionar los centros potencialmente relevantes.
6. Consultar los centros mediante las herramientas disponibles.
7. Registrar cada observación obtenida.
8. Evaluar si existe información suficiente para construir el resultado.
9. Si no existe, continuar consultando dentro del límite permitido.
10. Consolidar los resultados.
11. Presentar las alternativas de forma comparable.
12. Finalizar la interacción.

## Alcance

### Entra

- Consulta en **lenguaje natural** (examen, ciudad, previsión) que se traduce al
  catálogo.
- **Simulador de entorno:** 7 recintos ficticios en Talca (4 oftalmológicos,
  3 PET), 2 familias de exámenes, agenda y precios **preconfigurados**,
  conversación por texto de 3-4 turnos, con verdad conocida para poder
  verificarla.
- **Ciclo ReAct:** consultar centro por centro, decidir si seguir o consolidar,
  con condición de parada explícita.
- **Salida:** listado comparable de centros, con la trayectoria de la decisión
  visible.
- **Golden set** de 5 escenarios versionado y ejecutado.
- **Seguridad básica:** límites de alcance y acciones permitidas, más una
  prueba de jailbreak.
- Entrega como **notebook ejecutable** de punta a punta.

### No entra

- Audio, telefonía real, llamadas reales, clínicas reales.
- Agendamiento, pagos, recordatorios.
- Recomendación automática ("te recomiendo este centro").
- Lectura (OCR) de la orden médica.
- Cobertura fuera de Talca / Chile.
- Datos reales de pacientes, multiusuario, memoria a largo plazo.

## Restricciones

- **La pauta del curso manda.** La entrega es un notebook `.ipynb` ejecutable,
  y hay **tope de 3,0** si el LLM, ReAct, la herramienta, la devolución de
  observación, la parada o el historial no funcionan. Cada decisión de diseño
  se justifica contra un criterio de la pauta, no contra gusto.
- **V1 es 100% simulada.** No hay acceso a datos de centros reales, así que la
  exactitud se mide contra la verdad del simulador, no contra el mundo. La
  visión a largo plazo (consultar centros reales) no está validada.
- **Solo texto.** El audio y la telefonía se simulan o se omiten.
- **Sin claves ni datos personales en el repositorio.** También es una exigencia
  legal Chilean (Ley 19.628) para cualquier etapa con datos de salud reales.
- **Un solo desarrollador, dentro del horario del taller.** El presupuesto de
  APIs no limita, pero el tiempo sí: la complejidad que no compra un punto de la
  pauta no se paga.
- **El golden set no se maquilla:** los casos fallidos se corrigen y se
  re-ejecutan; no se eliminan.

## Comportamiento prohibido del agente

El agente nunca debe:

- Inventar precios, disponibilidad, convenios o requisitos.
- Completar información faltante suponiendo valores.
- Recomendar, ordenar o seleccionar un centro como "mejor".
- Ejecutar acciones que no estén definidas por las herramientas disponibles.
- Consultar información fuera del catálogo disponible.
- Solicitar datos personales que no sean necesarios para cotizar.
- Interpretar diagnósticos médicos.
- Convertir una coincidencia aproximada del catálogo en una afirmación de que
  se trata del mismo examen cuando no existe confirmación.

## Manejo de solicitudes fuera de catálogo

Si el usuario solicita un examen que no existe en el catálogo:

- El agente no debe intentar aproximarlo a otro examen.
- Debe informar que no puede realizar la cotización con el catálogo disponible.
- Debe indicar qué información o alternativas están disponibles, cuando
  corresponda.
- No debe inventar centros, precios, disponibilidad ni equivalencias.

## Condición de parada

El agente puede consolidar el resultado cuando:

- Ha encontrado al menos **3 alternativas comparables**, o
- Ha consultado todos los centros relevantes disponibles, o
- No existen más centros aplicables en el simulador.

El agente debe respetar un **máximo de iteraciones** definido por el equipo
y no debe entrar en bucles.

La condición definitiva y el valor del máximo de iteraciones deben quedar
documentados en la implementación y alineados con la pauta del curso.

## Principios de diseño

1. **El dato viene de la herramienta, nunca del modelo.** Precio y agenda se
   leen de una fuente de verdad o no se reportan. La alucinación se evita por
   construcción, no confiando en que el modelo se porte bien.

2. **La incertidumbre se declara.** Si un centro no responde o no confirma un
   dato, el reporte dice "no confirmado". Un vacío explícito vale más que un
   valor inventado o un silencio que se lee como confirmación.

3. **Informar, no decidir.** El agente entrega opciones comparables y se
   detiene ahí. No recomienda, no ordena, no convence: la decisión es de la
   persona.

4. **Comparabilidad antes que completitud.** Tres opciones con los mismos
   campos valen más que siete con campos dispares. Un centro que no admite
   comparación se marca como incompleto, no se esconde.

5. **Simulado no significa falso.** El simulador usa la misma interfaz que
   tendría el sistema en producción, y sus datos se pueden contrastar contra
   una verdad conocida. Es un banco de pruebas, no una maqueta distinta del
   producto.

6. **La trayectoria es parte del producto.** Que el agente consultó a quién,
   qué obtuvo y por qué paró se muestra, no se esconde. Sin traza no hay
   confianza ni evaluación posible.

7. **Reproducible antes que impresionante.** Con la misma entrada y el mismo
   estado del simulador, el agente debe producir resultados equivalentes y
   verificables, aunque la redacción pueda variar.

8. **Privacidad por omisión.** El agente pide el examen y la previsión. No pide
   nombre, RUT ni diagnóstico del paciente: no los necesita para cotizar.

## Evaluación del agente

Además del resultado final, se evaluará:

- Correcta selección y utilización de herramientas.
- Capacidad para solicitar información faltante.
- Correcta interpretación de las observaciones.
- Cumplimiento de la condición de parada.
- Ausencia de información inventada.
- Comportamiento ante errores o respuestas incompletas.
- Resistencia frente a solicitudes fuera de alcance y jailbreaks sencillos.
- Trazabilidad suficiente para reconstruir qué consultó el agente y por qué
  continuó o terminó.

## Criterios de éxito

1. El flujo corre de **START a END** en los 5 escenarios, sin intervención
   manual.
2. El reporte **coincide con la verdad del simulador**, campo por campo, en el
   golden set versionado.
3. La **trazabilidad ReAct es legible**: se ve cada consulta a un centro, la
   observación recibida, y la decisión del LLM de seguir o de parar.
4. El ciclo **siempre termina**: se respeta la condición de parada y el tope de
   iteraciones; nunca entra en bucle ni para antes de tiempo.
5. Ante una entrada fuera de catálogo o una petición fuera de alcance —
   incluido un jailbreak sencillo — el agente **responde con el límite y no
   ejecuta la acción**.
6. Otra persona puede **ejecutar el notebook desde cero**, en orden, sin
   necesitar una clave compartida ni un dato que no esté en el repositorio.
7. Las respuestas pueden variar en redacción, pero los **datos y decisiones
   verificables** deben ser consistentes con el estado del simulador.
