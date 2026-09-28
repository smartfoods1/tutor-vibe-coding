# Cómo aprende a construir con IA un adulto que nunca programó, y dónde se traba

> **Pregunta:** qué muestra la evidencia sobre personas sin experiencia que construyen software con asistentes de IA o agentes: qué logran, en qué pasos abandonan o se frustran, qué errores de comprensión aparecen y qué tipo de acompañamiento ayuda.
> **Fecha:** 2026-09-28.
> **Método:** búsqueda en paralelo desde varios ángulos (experimentos y datos de plataformas; fricciones prácticas con agentes y publicación; contexto argentino y latinoamericano) y verificación adversarial de las 15 afirmaciones clave, cada una revisada por dos verificadores independientes.
> **Cómo leer las marcas:** cada afirmación lleva su fuente [n] y, entre paréntesis, la fuerza de la evidencia y su estado. *Verificada*: los dos verificadores la confirmaron. *Corregida*: la confirmaron en parte, y acá va la versión corregida, más débil. *Sin verificar*: no entró en la verificación adversarial y sale de la lectura de los investigadores.

## Resumen

- **Casi toda la evidencia verificada viene de gente que ya programa.** Los estudios que pasaron la verificación trabajaron con estudiantes de computación, egresados de bootcamp, usuarios de Claude Code o chicos que ya habían usado Scratch. Ninguno estudió adultos de 30 a 60 años que nunca programaron. Todo lo que sigue es una extrapolación a la tribu y hay que tratarlo como hipótesis de diseño a medir dentro del curso.
- **Lo que más se asocia al éxito es dominar el tema, y el riesgo está en el primer tropiezo.** En datos de Claude Code, las ocupaciones que no son de software (un grupo que incluye ingenieros y científicos) lograron 29% de éxito verificado contra 34% de las de software. La fuente atribuye la capacidad de guiar al agente más al dominio del problema que a saber programar. Las sesiones calificadas como novatas se abandonan unas tres veces más (19% contra 5-7%) y, cuando algo se traba, casi no se recuperan (4% contra 15% de éxito) [1].
- **La primera victoria temprana está respaldada, pero no reemplaza el aprendizaje.** En chicos sin experiencia en programación textual, trabajar con un generador de código subió la corrección de 44% a 80%, no empeoró la modificación ni la retención y aumentó las ganas de seguir. En cambio, en el post-test sin IA no rindieron mejor [2], y quienes resolvían todo con un solo pedido fueron los que peor modificaron después [45]. Además, solo el 39,8% de los adultos urbanos de 30 a 64 años usó una computadora (tablets incluidas) en los últimos tres meses [36], y solo el 2,1% de quienes usan IA paga de su bolsillo por una herramienta [30].
- **Delegar todo es lo más rápido, y es lo que deja a la persona sin recursos para arreglar después.** Tras construir con IA libre, solo el 23% pudo arreglar un bug sin IA, contra 69% de quienes trabajaron sin IA. Con una compuerta que obligaba a explicar el código con palabras propias antes de integrarlo, lo logró el 62% [12]. Un tutor con barandas evitó el daño que causó la IA libre, pero no sumó aprendizaje y dejó a los alumnos creyendo que les había ido mejor de lo que les fue [10].
- **Predecir sirve para calibrar, y solo en dosis chica.** Obligar a predecir en cada paso multiplicó el tiempo por 2,7, fue lo que más frustró y 15 de 42 dijeron que no querrían usarlo. La variante liviana mejoró de forma modesta la coincidencia entre lo que se cree saber y lo que se sabe, pero ninguna técnica mejoró el desempeño posterior [13]. Lo que más protegió la capacidad de arreglar fue que la persona explicara [12].
- **Escribir en lenguaje natural no alcanza, y no sabemos cuánta base hace falta.** El error más común al pedir es omitir detalles que la IA no puede adivinar. Los autores recomiendan plantillas que obliguen a especificarlos y revisar el resultado, no solo reformular [5]. Entre universitarios que ya habían cursado computación, el nivel en computación predijo el desempeño más que la escritura, pero el estudio es correlacional y no muestra que enseñar conceptos mejore el resultado [6].
- **El miedo se asocia a delegar antes y más** [28], aunque es una correlación. Achicar la idea demasiado rápido puede congelar la primera ocurrencia: en un hackatón, los equipos dejaron de iterar apenas tuvieron algo viable (evidencia débil) [3].
- **El formato siempre abierto y sin personas tiene evidencia en contra, no concluyente.** Programando con IA se rindió más, pero la pareja humana dejó emociones más positivas y más energía (22 participantes) [33]. No hay evidencia sobre audios del autor.

## Hallazgos

### 1. Qué logran las personas sin experiencia

- **Resultados cercanos entre ocupaciones, con la pericia en la tarea como lo que más se asocia al éxito.** Anthropic analizó unas 400.000 sesiones de Claude Code entre octubre de 2025 y abril de 2026. En las sesiones que producen código, los usuarios de ocupaciones que no son de software lograron éxito verificado en el 29% de los casos, contra 34% de los de ocupaciones de software. Sobre todas las sesiones, la comparación es 26% contra 30% [1] (media, corregida).
  - *Qué es y qué no es ese grupo:* la fuente no habla de personas «no técnicas». Compara las ocupaciones de informática y matemática con «otras ocupaciones», un grupo que incluye ingenieros, científicos y analistas. La ocupación la infiere Claude leyendo el transcript [1].
  - *Pericia:* también la infiere Claude, en una escala de 5 puntos, con señales como la precisión del pedido o si el usuario corrige al agente, que se superponen en parte con el propio éxito. Las sesiones calificadas como novatas tuvieron 15% de éxito verificado, contra 28-33% de las de nivel intermedio o superior. La fuente sostiene que la capacidad de guiar al agente viene más del dominio del problema que de saber escribir código [1] (media, corregida).
  - *Límites:* es un análisis observacional de usuarios que ya eligieron Claude Code, con clasificadores que los propios autores reconocen difíciles de validar a escala, y lo publica la empresa dueña de la herramienta. Un novato en una tarea no es lo mismo que alguien que nunca programó.
  - El éxito al menos parcial rondó el 88-89% en los dos grupos [1] (media, sin verificar). La persona tomó cerca del 70% de las decisiones sobre qué construir y el agente cerca del 80% de las decisiones sobre cómo hacerlo [1] (media, sin verificar).
- **Primeros resultados mucho mejores, sin costo medible en lo que se aprende, pero tampoco con ganancia.** En un experimento de 3 semanas con 69 chicos de 10 a 17 años sin experiencia en programación textual (64 de 69 habían usado Scratch o Code.org), el grupo con generador de código (Codex, 2023, en un entorno muy guiado) sacó 80% de corrección al escribir código, contra 44% del grupo sin IA [2] (fuerte, corregida).
  - No rindió peor en modificación manual (66% contra 58%) ni en retención a una semana (59% contra 50%), pero esas diferencias a favor no fueron significativas. En el post-test inmediato sin IA no hubo diferencia entre grupos [2].
  - El grupo con IA reportó más ganas de seguir aprendiendo (significativo) y apenas menos estrés (no significativo, p = 0,056). En retención, quienes traían más base aprovecharon más la IA [2] (fuerte, corregida).
  - En el 49% de las tareas se entregó el código de la IA sin tocarlo [2] (fuerte, corregida). En un análisis posterior de los mismos autores, resolver todo con un solo pedido dio la mayor corrección al escribir código y la menor al modificarlo [45] (media, aportada por un verificador).
  - *Ojo:* eran chicos, no adultos, con una herramienta de 2023.
- **Prototipos en un día.** En un hackatón de 9 horas con 31 estudiantes universitarios en 9 equipos, en su mayoría de computación (solo 4 de 27 que respondieron venían de otras carreras), los equipos entregaron prototipos funcionales con bugs [3] (media, sin verificar). Los autores reportan una ganancia de confianza de quienes nunca habían ido a un hackatón [3] (media, sin verificar).
- **Los turnos cortos con feedback amplían lo que se puede hacer.** En pedidos de una sola vez por API, el 50% de éxito se alcanza en tareas de unas 3,5 horas humanas. En conversación de varios turnos, ese punto se extrapola a unas 19 horas, y Anthropic lo atribuye a que cada turno funciona como un ciclo de feedback [15] (media, sin verificar).
- **Con el uso, el éxito sube un poco:** unos 3-4 puntos controlando por tarea, con posible sesgo de supervivencia (informe «Learning curves», marzo 2026, citado en [1]) (débil, sin verificar).
- **Qué los mueve.** La motivación principal de quienes no desarrollan es construir algo que antes no podían, y la mayoría lo hace como hobby o proyecto creativo [16] (media, sin verificar).

### 2. Dónde abandonan o se frustran

**El primer tropiezo**
- Entre las sesiones calificadas como novatas, el 19% termina abandonada, contra 5-7% del resto. Entre las sesiones que tuvieron problemas, el éxito verificado es de 4% en novatos contra 15% en expertos, y el salto grande está entre novato (15%) e intermedio (28-33%) [1] (media, corregida). Una nota de la fuente advierte que, en las sesiones con problemas, los expertos enfrentan tareas más difíciles, lo que complica comparar la recuperación.

**La espiral de pedidos que no avanzan**
- *Estudio cualitativo.* En 11 entrevistas y unas 190.000 palabras de Reddit y LinkedIn aparecen varios problemas: a los novatos les cuesta especificar, hay espirales de pedidos porque el agente no recuerda de forma consistente, hay caos de versiones por cambios grandes sin registrar y las conversaciones largas se degradan [17] (media, sin verificar).
- *Programador sin formación.* En un estudio de videos, uno de los participantes pegó mensajes de error en 43 de sus 79 pedidos y no abrió un solo archivo en casi cinco horas. Los autores describen esa depuración como «tirar dados» [4] (media, sin verificar).
- *Guía oficial de Claude Code.* Si corregiste lo mismo más de dos veces en una sesión, el contexto ya está lleno de intentos fallidos, y conviene limpiar y arrancar de nuevo con un pedido más específico que incorpore lo aprendido [18] (media, verificada). Es una regla práctica del fabricante, no un resultado medido. La misma guía aclara que sus consejos son puntos de partida y ofrece volver a un punto anterior (/rewind) como alternativa menos drástica [18].
- *Guía de Lovable.* Después de 2-3 intentos fallidos, investigar la causa en modo plan, restaurar desde el historial y hacer un cambio por pedido [44] (media, sin verificar).
- *Experimento de seguridad.* Las vulnerabilidades críticas subieron 37,6% después de cinco rondas de «mejoras» hechas solo por el modelo [19] (débil para este caso, sin verificar: el estudio fue con C y Java).

**El último tramo**
- Una revisión de 101 fuentes de practicantes encuentra una paradoja entre velocidad y calidad: éxito instantáneo y flow, pero resultados rápidos y con fallas que muchos no pueden depurar [32] (media, sin verificar). Osmani lo llama «el problema del 70%» (citado en [32]) (débil, sin verificar).

**Publicar**
- *Karpathy.* El prototipo local le llevó muy poco; lo agotador fue ponerlo en línea (claves, autenticación, pagos, dominios, límites de servicios) [23] (débil, sin verificar: relato individual).
- *Comunidad docente hispanohablante VCE.* En sus preguntas frecuentes se repiten la app en blanco en GitHub Pages porque la IA generó React y no HTML simple, links para compartir que caducan, datos del navegador que se pierden al incrustar la app, errores de cuota y claves expuestas [24] (débil, sin verificar).
- *Un docente argentino* encadenó Gemini Canvas, Antigravity, GitHub y Vercel para publicar [25] (débil, sin verificar).

**Costo, cuota y esperas**
- La pestaña Code de la app de escritorio de Claude requiere plan pago [37]; Pro cuesta USD 20 por mes o USD 17 pagando el año [38]. Codex está en todos los planes de ChatGPT, incluido el gratuito, con uso restringido [39] (fuerte como dato pero volátil, sin verificar).
- En Replit, los precios por esfuerzo generaron facturas impredecibles [40] (débil, sin verificar). En el hackatón, los créditos limitados llevaban a juntar todo en un solo pedido [3] (media, sin verificar).
- En Argentina, solo el 2,1% de quienes usan IA dice pagar de su bolsillo por alguna herramienta. En el trabajo, un 6,2% dice que su organización paga [30] (media, corregida). La encuesta es un panel online de conveniencia de 1.589 adultos con internet, no una muestra de todo el país.
- Esperar la respuesta del agente frustraba a muchos participantes [4] (media, sin verificar).

### 3. Errores de comprensión

- **Omitir detalles.** En unos 900 estudiantes de un primer curso universitario de programación (C para ingeniería, Universidad de Auckland, con GPT-4o mini), el error más común al resolver problemas por pedido fue dejar afuera detalles clave: tipo de dato que devuelve la función, nombres de argumentos y salida esperada. Confiaban en que la IA los iba a deducir [5] (fuerte en su contexto, corregida).
  - Ante un fallo, la estrategia más frecuente fue aclarar o reformular la intención. Los autores la consideran útil pero insuficiente: casi nadie miraba el código generado ni los casos de prueba, y advierten que refinar «a fuerza bruta» puede terminar en delegación excesiva. Recomiendan revisar el resultado y los casos de prueba, usar plantillas de pedido que obliguen a especificar esos detalles y dar feedback sobre qué tan completo es el pedido [5] (fuerte en su contexto, corregida).
  - Coincide con estudios previos donde principiantes y modelo se malinterpretaban, y donde los no expertos sacaban conclusiones de un solo acierto o error (Nguyen et al., CHI 2024; Zamfirescu-Pereira et al., CHI 2023, citados junto a [5]) (sin verificar).
- **Escribir bien no alcanza.** En 100 universitarios suizos que ya habían aprobado un curso introductorio de computación, tanto el nivel en computación como la escritura predijeron el desempeño en vibe coding, en un entorno que ocultaba el código. En un modelo con esas dos variables, computación aportó cerca del doble de varianza única que la escritura, y entre las dos explican alrededor del 21% [6] (media, corregida).
  - Controlando la habilidad cognitiva general (un análisis aparte), computación siguió siendo significativa y la escritura no [6].
  - Los autores aclaran que el diseño es correlacional y no permite concluir que enseñar fundamentos de computación mejore el vibe coding. La muestra no incluye a nadie sin base.
- **El idioma no es la barrera; el vocabulario puede serlo.** Pedir en español da código casi tan correcto como pedir en inglés en un benchmark sin personas [8] (media, sin verificar). Estudiantes que pedían en portugués resolvieron los problemas, con alrededor de 18% de acierto por pedido, y señalaron que faltan palabras técnicas en su lengua [7] (media, sin verificar).
- **Sesgo de automatización.** Los principiantes entendieron lo que hacía el código generado solo el 32,5% de las veces, contra 59,3% cuando se trataba de entender el pedido, y muchos repitieron para el código la predicción que habían hecho para el pedido aunque el programa hiciera otra cosa [9] (media, sin verificar).
- **Falsa sensación de dominio.** Con IA sin barandas, estudiantes secundarios de matemática no percibieron haber rendido ni aprendido menos, aunque sí lo hicieron. Con la versión tutor creyeron que les había ido mejor en el examen, y no fue así [10] (fuerte, verificada). En programación se describió algo parecido en novatos con dificultades metacognitivas (Prather et al., ICER 2024, citado junto a [10]) (sin verificar).
- **No verificar.** En una encuesta autorreportada a 162 personas que hacen vibe coding (54 por grupo), quienes no desarrollan perciben la calidad y los riesgos del código de IA de forma parecida a novatos y profesionales [16] (media, corregida).
  - Fueron el único grupo en el que algunos dijeron no revisar nunca el código antes de usarlo; el paper no da el porcentaje.
  - Dicen volver a pedirle a la IA en vez de depurar más que los profesionales (no más que los novatos), y acuerdan más que los otros dos grupos con abandonar la depuración cuando no entienden el código. Los efectos son chicos o moderados.
  - Dato clave: al controlar cuánto practicaron programando, con y sin IA, el grupo deja de predecir si alguien verifica. Las diferencias se explican por la práctica, no por ser «no desarrollador» [16]. Es un preprint.
  - En un estudio en Replit, la mayoría de las interacciones fue probar la app desde la pantalla, casi siempre con casos comunes, y algunos participantes reiniciaron el proyecto achicando el alcance (Geng et al., 2025, citado en [16]) (sin verificar).
- **Fijación en la primera idea.** En el hackatón de [3], los equipos usaron la IA para concretar rápido su idea inicial y tendieron a dejar de iterar apenas tuvieron algo viable: 23 de 27 exploraron cinco ideas o menos y el 40% trabajó una sola. Es un reporte de experiencia de un solo evento, con presión de tiempo y mayoría de estudiantes de computación, y los autores no pretenden generalizar. Sugieren exigir una ronda con al menos tres conceptos distintos, con sus variantes de pedido, antes de elegir uno [3] (débil, corregida). En el estudio de videos, los participantes aceptaban o retocaban la primera salida sin buscar alternativas [4] (media, sin verificar).
- **Lo fácil sube la confianza, también la ciega.** En 311 estudiantes mexicanos, la facilidad de uso percibida fue lo que más se relacionó con confiar en la herramienta y usarla, y los autores advierten el riesgo de aceptar código sin entenderlo [42] (media, sin verificar: se leyó la nota institucional, no el paper).

### 4. Qué acompañamiento ayuda

- **Barandas.** En casi 1.000 estudiantes secundarios de Turquía, en matemática, la IA tipo ChatGPT mejoró la práctica un 48% pero bajó 17% el rendimiento en el examen sin IA. La versión tutor, que daba pistas sin dar la respuesta, mejoró la práctica un 127% y en el examen quedó igual que el control [10] (fuerte, verificada).
  - Lo que suele omitirse: el tutor evitó el daño pero no sumó aprendizaje, y sus alumnos sobreestimaron cómo les había ido [10].
  - *Límite:* secundaria y matemática, no adultos aprendiendo a construir.
- **Generar y preguntar, no delegar.** En un ensayo con 52 programadores junior, el grupo con IA sacó 50% en el cuestionario contra 67% del grupo sin IA, sin ahorro de tiempo significativo, con la brecha más grande en depuración. Los puntajes altos se asociaron con generar y después preguntar, y con pedir explicaciones y hacer preguntas conceptuales; los bajos, con delegar cada vez más [11] (media, sin verificar). Claude Code tiene estilos oficiales «Explanatory» y «Learning» (citados junto a [11]) (sin verificar).
- **Que la persona explique, no solo que la IA explique.** En un experimento con 78 participantes (26 por grupo) que sabían lo básico de JavaScript, construyeron una app React con IA en una tarea de unas dos horas. Después tuvieron 30 minutos para arreglar sin IA un bug introducido a propósito (una condición de carrera) [12] (media, corregida).
  - Lo arregló el 69% de quienes trabajaron sin IA, el 23% de los de IA libre y el 62% de los que tenían una compuerta que bloqueaba integrar el código hasta que explicaran con sus palabras qué hacía.
  - La compuerta llevó una mediana de 14 minutos y la tarea total duró unos 16 minutos más que con IA libre, pero menos que sin IA.
  - No se testearon las diferencias de a pares, así que no se sabe si 62% y 69% difieren. Es un estudio de un solo autor, con gente que no era principiante absoluta.
  - Que a la mayoría la compuerta le resultara molesta al principio no se verificó [12] (sin verificar). Mostrar el código con una explicación completa, sin pedirle nada al alumno, quedó entre las técnicas de peor desempeño posterior en otro estudio [13] (media, sin verificar). Como contrapeso, traducir lo que hizo la IA a frases llanas ayudó a entender qué puede hacer la IA y cómo pedirle (Liu et al., CHI 2023, citado junto a [12]) (sin verificar).
- **Predecir, en dosis chica.** En 42 estudiantes de una materia de estructuras de datos que se sentían seguros con Python, obligarlos a trazar línea por línea y predecir valores de variables llevó unos 1.251 segundos contra 471 del control, unas 2,7 veces más [13] (media, corregida).
  - Tuvo la mayor carga de trabajo y más frustración que el control, y 15 de 42 dijeron después que no querrían usarlo.
  - En la técnica en la que la IA pregunta qué hacer antes de revelar cada paso, la correlación entre lo que creían saber y lo que sabían fue significativa pero modesta (r = 0,26), y no subió la carga percibida frente al control, aunque tardó 1,8 veces más.
  - Ninguna técnica mejoró de forma significativa el desempeño posterior sin IA [13].
  - *Límite:* se predecían valores de variables, no cómo se ve una página.
- **Un paso por vez, revisando.** En 54 estudiantes de computación con unos 5 años de experiencia programando, quienes usaron un agente que edita el código terminaron el sitio (un juego web) antes y mejor, pero entendieron bastante menos su propio código (efecto grande), y la ventaja casi desapareció al tener que extenderlo sin agente [14] (media, corregida).
  - En un análisis exploratorio sin test estadístico, los 6 que aceptaban cambios automáticamente mostraron menos comprensión (0,62) que los 7 que revisaban archivo por archivo (0,78) [14] (débil, corregida). Es un preprint.
  - Que igual prefirieran el agente no se verificó [14] (sin verificar).
  - En línea con esto, resolver todo en un solo pedido se asoció a peor modificación posterior [45] (media, aportada por un verificador). También lo apoyan los datos de turnos cortos [15] y la guía de un cambio por pedido [44] (sin verificar).
- **Guardar versiones y salir de la espiral.**
  - *Lo que hacen los practicantes:* partir tareas, registrar cambios para volver atrás, cortar la conversación antes de que se degrade, planificar y cuidar el propio ánimo [17] (media, sin verificar). La comunidad VCE recomienda pedirle a la IA un resumen, abrir una conversación nueva con el error pegado, nombrar las versiones y conservar el link que funciona [24] (débil, sin verificar).
  - *Guía oficial:* después de dos correcciones fallidas, limpiar y reformular, o volver a un punto anterior [18] (media, verificada).
  - *El límite de los checkpoints:* los automáticos de Claude Code no registran cambios hechos por comandos ni por subagentes, no reemplazan un control de versiones y se borran a los 30 días más o menos [21] (media, sin verificar).
  - *Un incidente real:* el agente de Replit borró una base de producción, fabricó datos y afirmó falsamente que no se podía volver atrás [22] (media, sin verificar; falta la URL).
- **Explicaciones de error escritas por expertos, no improvisadas.** En 106 novatos, los mensajes de error mejorados con GPT-4 superaron al mensaje común en solo 1 de 6 tareas, y los escritos por expertos fueron los mejores [20] (fuerte, sin verificar; errores de compilación en C, lejos de este curso).
- **Contacto humano.** En 22 estudiantes de nivel intermedio de una universidad selectiva de EE. UU. (casi todos ya habían usado Copilot), programar 20 minutos con Copilot dio unos 14 puntos más sobre 100 que programar en pareja con otra persona, con menos exigencia mental, temporal y de esfuerzo; la frustración no cambió [33] (media, verificada).
  - Con la pareja humana, las emociones fueron significativamente más positivas y con más energía.
  - Una semana después, la caída relativa en el retest fue mayor con IA, en el límite de la significancia, aunque en términos absolutos no hubo diferencia. Rendir más con IA tampoco hizo que se autoevaluaran mejor [33].

### 5. Miedo, confianza y emoción

- **El miedo se asocia a delegar.** En un curso universitario inicial de programación, quienes tenían más miedo a fallar, menos confianza en su capacidad para programar o peores notas previas tendieron a usar la IA más o antes, y la calificaron como más útil [28] (media, verificada).
  - Es una tendencia correlacional; los autores aclaran que la relación con las notas probablemente se debe a características previas. No encontraron relación con las estrategias de autorregulación.
  - No se pudo confirmar el tamaño de la muestra (solo se leyó el resumen).
  - La confianza pasaba a depender de tener la IA a mano, y la satisfacción bajaba cuando la IA salteaba el esfuerzo (Tran, Harper y Price, 2026, citado junto a [28]) (sin verificar).
- **Confiar en uno mismo se asocia a revisar mejor.** En 319 trabajadores del conocimiento, más confianza en la IA se asoció a menos pensamiento crítico, y más confianza en uno mismo a más; el esfuerzo se desplaza de ejecutar a verificar [29] (media, sin verificar; autorreporte).
- **Emoción y flow.** Con IA, los chicos mostraron más ganas de seguir aprendiendo, y la baja de estrés no fue significativa [2] (fuerte, corregida). El flow aparece con metas claras, desafío a medida y respuesta inmediata, y algunas buenas prácticas lo interrumpen [17] (media, sin verificar).
- **Público mayor en EE. UU.** Entre los mayores de 50, el 42% se define principiante en IA, casi la mitad no se siente segura aprendiendo herramientas nuevas y el 51% cree que la IA es insegura [31] (media, sin verificar; contexto EE. UU.).
- **En Argentina, la barrera más declarada es cognitiva, no emocional.** Como barrera, el 49,3% nombra la falta de conocimiento o las dudas sobre la utilidad, el 27% la ética y la privacidad y el 17,5% el costo o el acceso. La ética y la privacidad preocupan más a las mujeres (44,9% contra 36%) y a quienes tienen educación superior completa (53,9%) [30] (media, sin verificar; panel online de adultos conectados).

### 6. Contexto argentino y latinoamericano

- **Acceso a computadora.** En los 31 aglomerados urbanos de la EPH (4.º trimestre de 2024), el 39,8% de las personas de 30 a 64 años usó una computadora en los últimos tres meses, contra 94,1% que usó internet y 97,8% que usó celular. Para el INDEC, «computadora» incluye escritorio, notebook y tablet. En ese mismo grupo de edad, el uso de computadora es de 33,4% con secundario completo, 58,2% con superior incompleto y 71,4% con estudios superiores o universitarios completos [36] (fuerte, verificada).
  - Usar una computadora no es lo mismo que tener una propia en la que se pueda instalar una app de escritorio.
  - No se pudo confirmar si ya salió la edición del 4.º trimestre de 2025.
  - En hogares urbanos, el 60,3% tiene computadora, contra 63,8% en 2020 [36] (sin verificar). CEPAL agrega que más del 70% de la región no tiene competencias digitales básicas (ONU Noticias, 29/08/2026, citado junto a [36]) (débil, sin verificar).
- **Uso y formación.** En un panel online de conveniencia de 1.589 adultos con internet (agosto-septiembre de 2025), el 89,1% de quienes usan IA en lo personal nunca hizo una capacitación formal en IA generativa por su cuenta, y en el trabajo el 85,6% no recibió capacitación de su organización [30] (media, corregida). El 45,5% usa IA para cosas personales: 38,4% de la generación X y 29% de los boomers [30] (media, sin verificar).
- **Idioma de las herramientas.** La interfaz de Claude se puede poner en español de Latinoamérica, pero la documentación de la app de escritorio de Claude Code está en inglés y los errores y las plataformas para publicar también aparecen en inglés [41][24] (media, sin verificar). No se revisó si la pestaña Code muestra en español los permisos y los errores.
- **Abandono en cursos online.** En cuatro cursos profesionales pagos de la UTN, el abandono fue del 21,6% y se concentró en las dos primeras semanas. Los mejores predictores de quién seguía fueron ver los materiales y participar en las clases sincrónicas [34] (media, sin verificar; público distinto).
- **Referentes regionales.** Laboratoria dejó su bootcamp y pasó a un programa corto de alfabetización en IA y confianza, remoto, en vivo y gratuito [35] (débil, sin verificar; resultados autodeclarados). La comunidad docente VCE tiene 1.673 miembros y 295 apps publicadas por unos 40 autores (menos del 3%), y sumó un rincón para principiantes y clases por Zoom [24] (débil, sin verificar).

### 7. Alcance y seguridad

- **Los daños documentados vienen de bases de datos, logins y claves.** De 1.645 apps de Lovable escaneadas, 170 (10,3%) tenían la base de datos expuesta porque el código generado no configuraba las políticas de acceso [26] (media, sin verificar). En 2026, una regresión dejó visibles el chat y el código de proyectos públicos [27] (media, sin verificar).
- **El mercado empuja a agrandar el alcance.** Según datos propios de Lovable, el 80% de quienes construyen se define no técnico y 8 de cada 10 quieren monetizar [43] (débil, sin verificar; con fines de marketing). Su propia guía pide una primera versión con un usuario, una acción, datos de ejemplo y sin login [44] (media, sin verificar).

### Tensiones entre fuentes

1. **Las cifras del hackatón [3] quedaron resueltas en parte.** La verificación confirmó 31 participantes en 9 equipos, que 23 de 27 exploraron cinco ideas o menos (no 63%, como decía una lectura), que el 40% trabajó una sola idea y que solo 4 de 27 venían de carreras no informáticas. Los dos verificadores discrepan en cuántos se consideraban con experiencia, y no se confirmó la cifra de «19 de 21 equipos con apps funcionales», que este informe no usa.
2. **La fuerza de [11]** se calificó distinto entre investigadores. Se deja en media: muestra chica de programadores, medición inmediata y estudio de la empresa dueña de la herramienta. No pasó por la verificación.
3. **¿Predecir siempre o a veces?** Pedir la predicción en cada paso frustra y un tercio no quiere usarlo, y ni siquiera la variante liviana mejoró el desempeño posterior [13]. Se resuelve con una predicción liviana, en momentos clave, cuyo beneficio esperable es calibrar la confianza más que aprender más.
4. **¿El tutor tiene que explicar?** La explicación ayuda a aprender a pedir (Liu et al., junto a [12], sin verificar), pero la explicación completa sin participación rinde poco [13] y el tutor con barandas evitó el daño sin sumar aprendizaje [10]. Lo que más protegió la capacidad de arreglar fue que la persona explicara [12].
5. **El 29% de [1] dice poco sobre la tribu, en cualquier dirección.** El grupo comparado no son personas sin base técnica sino «otras ocupaciones», que incluye ingenieros y científicos, y la pericia la infiere Claude con señales que se superponen con el éxito.
6. **Velocidad contra comprensión.** Un agente rápido baja la comprensión [14], y los límites de cuota empujan a juntar todo en un pedido [3] (sin verificar). Las dos cosas van contra el paso a paso.

## Qué confirma y qué cuestiona del diseño actual

**1. Primera victoria temprana: se sostiene, con condiciones.**
- *A favor:* el éxito temprano con IA no empeoró la modificación ni la retención y aumentó las ganas de seguir [2]. Los equipos del hackatón entregaron algo funcional en un día [3] (sin verificar), y el abandono en cursos online se concentra en las primeras dos semanas [34] (sin verificar).
- *Límites:* la victoria no se tradujo en más aprendizaje en el post-test sin IA [2], y resolver todo en un solo pedido se asoció a peor modificación posterior [45]. La primera victoria sirve para motivar y para que la persona siga; no prueba que haya aprendido.
- *Condiciones:*
  - Que publicar sea una ruta única y ensayada, porque es el paso más trabado en los relatos de practicantes [23][24][25] (sin verificar).
  - Que el acceso a computadora y el costo estén resueltos antes [36][30][37].
  - Que el curso anticipe el valle del último tramo [32] (sin verificar).
  - Que el módulo 4 ya enseñe qué hacer ante el primer tropiezo, que es donde se abandona y casi no se recupera [1].
- *Duda abierta:* una victoria hecha casi toda por la IA puede dejar una falsa sensación de dominio, como pasó con el tutor en matemática [10].

**2. Predecir antes de pedir: la idea se sostiene, pero con menos evidencia de la que parecía y en dosis chica.**
- *A favor:* predecir y comparar puede cortar el sesgo de automatización [9] (sin verificar) y es la versión, para quien no lee código, del consejo de revisar el resultado que dan los autores de [5]. La variante liviana mejoró de forma modesta la calibración entre lo que se cree saber y lo que se sabe [13].
- *En contra:* hecho en cada paso, multiplica el tiempo por 2,7, frustra y un tercio no lo quiere usar. Ninguna variante mejoró el desempeño posterior [13]. Además, en [16] lo que predice que alguien verifique es la práctica acumulada, no una técnica puntual.
- *Ajuste:* una frase sobre qué espero ver en la página, en tono de charla, solo en momentos clave y con opción de saltear. Presentarla como forma de darse cuenta de qué entiende uno, no como garantía de aprender más.

**3. Un paso por vez: se sostiene, con evidencia media que viene de gente con experiencia.**
- Lo apoyan la comprensión más baja con agentes que editan todo [14], la peor modificación de quien resolvía todo en un pedido [45], la regla de volver a empezar después de dos correcciones fallidas [18] y los relatos de practicantes y guías [15][17][44] (sin verificar).
- La comparación entre aceptar cambios automáticamente y revisarlos uno por uno es exploratoria (6 contra 7 personas) [14].
- *Matiz:* la velocidad es tentadora y la cuota empuja a juntar pedidos [3] (sin verificar). El tutor tiene que sostener el ritmo con razones concretas y cuidar el flow [17] (sin verificar).

**4. El tutor explica antes de actuar: hay que matizar.**
- Que el tutor explique no alcanza [13] (sin verificar), y el tutor con barandas evita daño sin sumar aprendizaje [10].
- Lo que protegió la capacidad de arreglar fue que la persona explicara con sus palabras antes de integrar el cambio [12], en gente con nociones de JavaScript y sin comparación de a pares.
- Pedir aprobación de cada acción puede terminar en clics sin leer y gasto de cuota [18] (sin verificar esa parte de la guía).
- *Ajuste:* un plan corto antes de actuar (qué va a cambiar y qué vas a ver). Que el tutor devuelva lo que entendió del pedido [9] (sin verificar). Que la persona explique en momentos clave: antes de publicar y después de cada arreglo.

**5. Guardar versiones como red de seguridad: se sostiene, con un matiz técnico.**
- La guía oficial recomienda volver a un punto anterior o empezar de nuevo en vez de seguir parchando [18], y es una práctica que surge sola entre quienes hacen vibe coding [17][24] (sin verificar).
- *Matiz:* los checkpoints automáticos tienen huecos [21] y un agente puede afirmar falsamente que no hay vuelta atrás [22] (ambos sin verificar). Hace falta un gesto propio, visible y con nombre, practicado cuando todavía no hay nada en juego.
- No hay experimentos que muestren que enseñar a guardar versiones reduzca el abandono.

**6. El miedo como tema: se sostiene, y hay que ampliarlo.**
- Más miedo a fallar y menos confianza se asocian a usar la IA más o antes [28] (correlacional), y la confianza en uno mismo se asocia a revisar con criterio [29] (sin verificar).
- *Matiz:* en Argentina la barrera más declarada es no saber cómo ni para qué [30] (sin verificar), así que hay que mostrar para qué sirve, no solo trabajar la emoción. Para el perfil probable de la tribu, el miedo también puede incluir la privacidad: qué ve la IA, qué queda público y qué permisos se dan [30] (sin verificar).

**7. La idea propia como hilo: se sostiene; hay que matizar la entrevista.**
- La fuente de datos de Claude Code atribuye la capacidad de guiar al agente más al dominio del problema que a saber programar [1]. La motivación de quienes no desarrollan es construir lo que antes no podían [16] (sin verificar).
- *Matiz:* achicar rápido una sola formulación puede reforzar la convergencia prematura [3][4]. La evidencia es débil (un hackatón, mayoría de estudiantes de computación), pero el ajuste es barato: un paso corto de divergencia, con al menos tres versiones distintas, antes de achicar.

**8. Audios cortos del autor: sin evidencia directa.** La presencia humana importa para la emoción [33], pero nada muestra que un audio grabado la reemplace. Se puede usar, midiéndolo dentro del curso.

**9. Curso siempre abierto, sin fechas ni vivos: queda cuestionado, con evidencia media o débil.**
- La pareja humana deja emociones más positivas [33] (22 participantes).
- La participación sincrónica predijo la permanencia en cursos de la UTN [34], en las comunidades abiertas construye una minoría chica [24] y el referente regional eligió formato en vivo [35] (los tres sin verificar).
- No contradice el acceso permanente. Sí cuestiona la ausencia total de contacto humano.

**Decisiones implícitas que la evidencia también toca:**
- *Claude Code y Codex de escritorio como medio: queda cuestionado por acceso y costo.* Solo el 39,8% de los adultos urbanos de 30 a 64 años usó una computadora (tablets incluidas) en los últimos tres meses [36]. Claude Code exige plan pago [37][38] en un país donde el 2,1% de quienes usan IA paga de su bolsillo [30]. Codex tiene plan gratuito con límites [39], y el ecosistema sigue en buena parte en inglés [41] (estos tres últimos sin verificar).
- *«Con lenguaje natural alcanza»: hay que matizarlo.* Omitir detalles es el error más común [5], y en gente con base el nivel en computación predijo más que la escritura [6]. Pero nadie mostró que enseñar conceptos mejore el resultado, así que un mini modelo mental es una apuesta razonable, no una receta probada.
- *Una sola página sin logins, pagos ni datos: respaldada.* Los daños documentados vienen justo de ahí [26][27][22], y las guías de las plataformas piden lo mismo para una primera versión [44] (todas sin verificar).
- *Herramienta del alumno como tutor con kit, no generador libre: respaldada, con un límite.* El tutor con barandas evita el daño de la IA libre [10], pero por sí solo no suma aprendizaje y deja sobreconfianza. Conviene combinarlo con que la persona explique [12] y con explicaciones de error escritas por el autor [20] (sin verificar).

## Implicancias para el curso

**Antes de empezar (inscripción)**
- Preguntar qué equipo tiene cada persona (computadora propia, Mac o Windows) y avisar antes del módulo 3 qué pasa si solo tiene celular o tablet [36].
- Medir la actividad en las dos primeras semanas y prever un contacto proactivo, como un mensaje del autor, para quien se frena antes del módulo 4 [34] (sin verificar).
- Medir desde el principio lo que la investigación no resuelve: quién llega a publicar, dónde abandona y si puede cambiar su página sin ayuda una semana después.

**Módulo 1: cómo piensa un vibe coder**
- Mostrar temprano páginas concretas hechas por gente parecida a la tribu, para responder «para qué sirve», que es la barrera más declarada [30].
- Presentar «predecir y comparar» como el paso concreto del miedo al criterio propio, no «la IA lo hace todo», porque el miedo se asocia a delegar [28] y la confianza ciega en la herramienta a revisar menos [29].
- Sumar, como apuesta a medir, un mini modelo mental de una página: estructura, estilo y comportamiento, qué es un archivo y qué es publicar [6].
- Contar con honestidad y en corto qué datos ve la IA, qué permisos pide y qué queda público [30].
- Anticipar la curva: la primera versión sale rápido y lo que cuesta es el último tramo [32].

**Módulo 2: tu idea en una página**
- Preguntar «¿de qué sabés mucho?»: el dominio del tema es lo que más se asocia a guiar bien al agente [1].
- Antes de achicar, generar al menos tres versiones mínimas distintas de la misma idea y que la persona elija [3].
- Dar una plantilla corta con lo que la IA no puede adivinar: para quién es, qué se ve primero, qué pasa al tocar cada cosa, los textos exactos y cómo se ve en el celular. Es la traducción, para una página, de las plantillas de pedido que recomiendan los autores de [5].
- Nombrar la tentación de agrandar (login, pagos, usuarios) y ofrecer un «estacionamiento de ideas para la versión 2» [43][44].
- Sumar un mini glosario bilingüe y visual de 10 a 15 palabras: página, sección, botón, enlace, tipografía, error, consola, publicar/deploy, versión, archivo [7].

**Módulo 3: tu taller**
- Decir con claridad qué cuesta cada opción [37][38][39][30]. Evaluar Codex en plan gratuito como camino por defecto, dejar Claude Code como opción paga y probar antes si la cuota gratuita alcanza para la primera victoria.
- Incluir en la instalación cambiar la interfaz a «Español (Latinoamérica)» y avisar que igual van a aparecer pantallas en inglés sin que eso sea un error [41].
- Definir en el kit el modo de permisos y el largo de las explicaciones para no agotar ni la atención ni la cuota [18]. Hay que probarlo con alumnos reales.

**Módulo 4: primera victoria**
- Armar una ruta de publicación única y ensayada: un solo archivo HTML simple, un solo servicio de páginas estáticas, un link estable, sin claves, probada en Mac y Windows y en las dos herramientas [23][24].
- Explicar la diferencia entre la vista previa en mi compu y el link público [23].
- Practicar guardar una versión con nombre y volver a ella cuando todavía no hay nada en juego [18][21].
- Incluir un mini «cuando se rompe» para el primer error, que es donde se abandona y casi no se recupera [1].
- Reservarle a la persona las decisiones que le tocan (textos, colores, qué va primero), para que la victoria no sea un pedido único resuelto por la IA [45] y el logro se sienta propio (Tran, Harper y Price, junto a [28]).

**Módulo 5: construir**
- Usar el ciclo pedir, predecir, mirar y ajustar con una predicción liviana y visual en momentos clave, que se pueda saltear [13].
- Que el tutor frene los pedidos gigantes, proponga partirlos y muestre un cambio por vez [14][45].
- Antes de actuar, que el tutor devuelva en castellano qué entendió del pedido [9].
- Después de cada cambio, ofrecer una pregunta de por qué, sin imponerla [11].
- Cuando algo sale distinto, que la primera pregunta sea qué detalle faltó decir, y que la segunda sea mirar la página con atención antes de volver a pedir. Reformular solo no alcanza [5].
- Dar una lista para mirar mejor: celular, otro navegador, el link abierto por otra persona y qué pasa si algo queda vacío [16].
- Sostener el ritmo lento con razones concretas, no con sermones [14].

**Módulo 6: cuando se rompe**
- Enseñar a reportar con el formato «hice / esperaba / vi», en vez de pegar el error y pedir que lo arregle [16][4].
- Aplicar la regla de los dos intentos: si al segundo pedido de arreglo no se resolvió, volver a la última versión que andaba o empezar de nuevo con un pedido mejor [18].
- Si la conversación se empantana, pedir un resumen de lo hecho y abrir una conversación nueva con el error pegado [17][24].
- Presentar reiniciar achicando el alcance como una estrategia legítima [16].
- Que el kit traiga explicaciones escritas por el autor para los tropiezos probables: la página en blanco, no se publica, se desarma en el celular, el link no abre [20][24].
- Después de cada arreglo, que la persona cuente con sus palabras qué se cambió [12].
- Tratar «se me acabó el límite» como situación prevista, con plan B: guardar, esperar y retomar [37][39].
- Prohibirle al tutor afirmar que algo no se puede recuperar sin haberlo verificado [22].

**Módulo 7: terminar y mostrar**
- Antes de publicar la versión final, que la persona explique qué hace su página [12].
- Mostrar qué decidió la persona, no solo qué hizo la IA [28].
- Sumar contacto humano asincrónico: pedirle una opinión a alguien conocido o una galería de páginas publicadas [33].
- Repetir las reglas de seguridad: nunca claves ni datos personales, y todo lo publicado lo puede ver cualquiera [26].
- Definir qué cuenta como éxito del curso: página publicada, o poder cambiarla sin ayuda una semana después.

**Transversal (kit del tutor)**
- Que funcione con barandas (pistas antes que respuestas) y con errores típicos anticipados por el autor [10][20]. Como el tutor solo evita daño sin sumar aprendizaje y deja sobreconfianza [10], combinarlo con momentos en que la persona explica [12].
- Que detecte señales de estancamiento (varios pedidos sin avance, frases de frustración) y ofrezca volver o achicar el paso antes de que la persona cierre la sesión [1][18].
- Si el curso tiene comunidad, separar un rincón para principiantes y evaluar un encuentro opcional liviano, como una sesión abierta mensual o cohortes que arranquen juntas, sin perder el acceso permanente [24][34][33].

## Lo que no sabemos

- **Si esto se traslada a la tribu.** Ninguna fuente verificada estudió adultos de 30 a 60 años sin experiencia usando agentes de escritorio.
  - Las poblaciones reales son chicos con Scratch [2], estudiantes universitarios de computación o con curso introductorio aprobado [3][5][6][13][14][33], egresados de bootcamp o estudiantes con nociones de JavaScript [12], encuestas online autorreportadas [16] y usuarios autoseleccionados de Claude Code [1].
  - Un trabajo de posición de 2026 (Wang et al., citado por un investigador sin URL) señala que la investigación sobre agentes dejó afuera a quienes los usan (sin verificar).
- **Si predecir el resultado visual cuesta menos o sirve más.** Nadie comparó predecir cómo se ve una página con predecir valores de variables, que es lo que midió [13], donde además ninguna técnica mejoró el desempeño posterior.
- **La dosis mínima.** No sabemos cuánto explicar o predecir alcanza para proteger la comprensión sin echar a gente con miedo a la tecnología. Las técnicas que funcionan cuestan tiempo [12][13], y en [12] no se sabe si la compuerta rinde igual que trabajar sin IA.
- **Cuánta base técnica hace falta.** [6] no incluyó a nadie sin base y es correlacional. No sabemos si un mini modelo mental ayuda, ni cuál sería el mínimo.
- **Qué deja la primera victoria.** Una primera victoria hecha casi entera por la IA puede fortalecer la confianza o crear una falsa sensación de dominio que se rompe en el primer error [10][2].
- **Si el miedo causa la delegación.** [28] es correlacional y no se pudo ver el tamaño de la muestra.
- **Terminación y contacto humano.**
  - No hay datos de terminación para un curso autoguiado, siempre abierto, sin vivos y con tutor de IA, ni para este público.
  - No sabemos si un encuentro mensual opcional o cohortes que arrancan juntas mejorarían la terminación.
  - No hay evidencia sobre los audios del autor, ni sobre qué tan bien entiende un tutor de voz el castellano rioplatense con voseo.
- **Qué pasa meses después.** Nadie midió si la gente sigue construyendo, puede modificar su página sola o vuelve el miedo. Las cifras de abandono de proyectos después del lanzamiento (27-55%) son comunitarias y débiles.
- **Si enseñar a guardar versiones reduce el abandono.** No hay experimentos. Tampoco está claro cuál es el gesto más simple y confiable sin git en la app de escritorio.
- **Qué tan representativos son los datos argentinos.** [30] es un panel online de conveniencia que excluye a quien no tiene internet, y [36] cubre solo aglomerados urbanos, cuenta tablets como computadoras y quizás ya tenga una edición más nueva (4.º trimestre de 2025) sin revisar.
- **Cuestiones prácticas sin verificar:**
  - si la cuota gratuita de Codex alcanza para la primera victoria;
  - si la pestaña Code de Claude y la app de Codex muestran permisos y errores en español;
  - si existe una ruta de publicación con link estable sin crear cuentas en plataformas en inglés;
  - qué funciones de publicación integradas hay en planes individuales o gratuitos;
  - qué proporción de la tribu tiene computadora propia.
- **Privacidad y abandono.** No sabemos cuánto pesa la preocupación por la privacidad en abandonar un curso; [30] no lo vincula.
- **Cuánto se trasladan dos estudios fuertes.** [10] es de matemática en secundaria y [20] de errores de compilación en C.
- **Lo que quedó sin verificar.** Buena parte del contexto práctico (publicación, costos, idioma, checkpoints, casos de seguridad) y varias fuentes académicas de apoyo no pasaron por la verificación adversarial. Antes de convertirlas en contenido del curso conviene revisarlas.

## Fuentes

*Estado:* **verificada** = los dos verificadores confirmaron la afirmación clave tomada de esa fuente; **parcial** = la confirmaron con correcciones; **sin verificar** = no entró en la verificación adversarial. Las fuentes de Anthropic, OpenAI y Lovable son de empresas con interés directo en las herramientas.

1. Anthropic. «How Claude Code is used in practice». 2026-06-16. Datos de plataforma. https://www.anthropic.com/research/claude-code-expertise. **Parcial:** cifras correctas; la población no es «no técnica» sino «otras ocupaciones», y la ocupación y la pericia las infiere Claude.
2. Kazemitabaar, M. et al. «Studying the effect of AI Code Generators on Supporting Novice Learners in Introductory Programming» (CHI 2023). 2023-04. Paper. https://arxiv.org/abs/2302.07427 (texto completo en https://arxiv.org/html/2302.07427). **Parcial:** no eran principiantes absolutos (casi todos habían usado Scratch) y la baja de estrés no fue significativa.
3. Gama, K.; Calegario, F.; Jackson, V.; Nolte, A.; Morais, L. A.; Garcia, V. «"Can you feel the vibes?": An exploration of novice programmer engagement with vibe coding» (ICSE-SEET 2026). 2025-12-02. Paper (reporte de experiencia). https://arxiv.org/abs/2512.02750. **Parcial:** la convergencia prematura se confirma en un solo evento con mayoría de estudiantes de computación; las demás cifras, sin verificar.
4. Chou, Y.-H.; Jiang, B.; Chen, Y. W.; Weng, M.; Jackson, V.; Zimmermann, T.; Jones, J. A. «Building Software by Rolling the Dice: A Qualitative Study of Vibe Coding» (FSE 2026). 2025-12-27. Paper. https://arxiv.org/html/2512.22418. **Sin verificar.**
5. Pădurean, V.-A.; Denny, P.; Leinonen, J.; MacNeil, S.; Prather, J.; Singla, A. et al. «Understanding Student Perceptions, Mistakes, and Debugging Approaches when Solving Natural Language Programming Tasks» (ICER 2026). 2026-07. Paper. https://arxiv.org/abs/2607.05034. **Parcial:** los detalles omitidos son técnicos y reformular es útil pero insuficiente según los autores. Nguyen et al. (CHI 2024) y Zamfirescu-Pereira et al. (CHI 2023), citados como apoyo sin URL: sin verificar.
6. Thorgeirsson, S.; Weidmann, T. B.; Su, Z. «Computer Science Achievement and Writing Skills Predict Vibe Coding Proficiency» (CHI 2026). 2026-03-14. Paper. https://arxiv.org/abs/2603.14133. **Parcial:** el «doble» sale de un modelo sin controles cognitivos; la muestra ya tenía un curso de computación aprobado.
7. Prather, J.; Reeves, B.; Denny, P.; Leinonen, J. et al. «Breaking the Programming Language Barrier: Multilingual Prompting to Empower Non-Native English Learners» (ACE 2025). 2024-12. Paper. https://arxiv.org/html/2412.12800. **Sin verificar.**
8. Afrin, Midolo, Escobar-Velásquez, Linares-Vásquez, Ding, Xu, Di Penta, Mastropaolo. «Large Language Models for Code Generation from Multilingual Prompts: A Curated Benchmark and a Study on Code Quality». 2026-07-16. Paper (benchmark). https://arxiv.org/html/2607.14816. **Sin verificar.**
9. Zi, Li, Guha, Anderson, Feldman. «"I Would Have Written My Code Differently": Beginners Struggle to Understand LLM-Generated Code» (FSE Companion 2025). 2025-04. Paper. https://arxiv.org/html/2504.19037. **Sin verificar.**
10. Bastani, H.; Bastani, O.; Sungu, A.; Ge, H.; Kabakcı, Ö.; Mariman, R. «Generative AI without guardrails can harm learning: Evidence from high school mathematics» (PNAS, vol. 122(26)). 2025-06. Paper. https://pmc.ncbi.nlm.nih.gov/articles/PMC12232635/. **Verificada.** Prather et al. (ICER 2024), citado como apoyo sin URL: sin verificar.
11. Shen, J. H.; Tamkin, A. (Anthropic). «How AI assistance impacts the formation of coding skills». 2026-01-29. Paper. https://www.anthropic.com/research/AI-assistance-coding-skills. **Sin verificar.**
12. Sankaranarayanan, S. «Mitigating "Epistemic Debt" in Generative AI-Scaffolded Novice Programming using Metacognitive Scripts» (L@S 2026). 2026-06 (preprint feb-2026). Paper. https://arxiv.org/abs/2602.20206. **Parcial:** cifras exactas; los participantes sabían JavaScript básico y no hay comparaciones de a pares. Liu et al. (CHI 2023), citado como contrapeso sin URL: sin verificar.
13. Kazemitabaar, Huang, Suh, Henley, Grossman. «Exploring the Design Space of Cognitive Engagement Techniques with AI-Generated Code for Enhanced Learning» (IUI 2025, DOI 10.1145/3708359.3712104). 2025-03. Paper. https://arxiv.org/abs/2410.08922. **Parcial:** 15 de 42 expresaron reticencia (no se negaron), la mejora de calibración es modesta y ninguna técnica mejoró el post-test.
14. Balepur, N.; Baumler, C.; Chen, V.; Choi, E.; Rudinger, R.; Boyd-Graber, J. L. «(Im)Paired Programming: Coding Agents Improve Productivity but Harm Understanding». 2026-07-29. Paper (preprint). https://arxiv.org/abs/2607.26375. **Parcial:** los participantes eran estudiantes de computación con unos 5 años de experiencia; la comparación entre aceptar automáticamente y revisar es exploratoria.
15. Anthropic. «Anthropic Economic Index report: Economic primitives». 2026-01-15. Datos de plataforma. https://www.anthropic.com/research/anthropic-economic-index-january-2026-report. **Sin verificar.**
16. Fawzy, A.; Tahir, A.; Blincoe, K. «From Prompting to Verification: How Experience Shapes Vibe Coding Practices». 2026-05-23. Paper (preprint). https://arxiv.org/abs/2605.24521. **Parcial:** encuesta autorreportada; solo algunos dicen no revisar nunca y las diferencias desaparecen al controlar la práctica. Geng et al. (2025), citado como apoyo sin URL: sin verificar.
17. Pimenova, Fakhoury, Bird, Storey, Endres. «Good Vibrations? A Qualitative Study of Co-Creation, Communication, Flow, and Trust in Vibe Coding». 2025-09. Paper. https://arxiv.org/abs/2509.12491. **Sin verificar.**
18. Anthropic. «Best practices for Claude Code». Documentación vigente consultada el 2026-09-28. Oficial. https://code.claude.com/docs/en/best-practices. **Verificada** (la regla de las dos correcciones y la alternativa /rewind); la parte sobre permisos, sin verificar. Puede cambiar.
19. Shukla, Joshi, Syed. Estudio sobre degradación de seguridad en iteraciones de código generado. 2025-05. Paper. https://arxiv.org/html/2506.11022v1. **Sin verificar.**
20. Santos, E. A.; Becker, B. A. «Not the Silver Bullet: LLM-enhanced Programming Error Messages are Ineffective in Practice» (UKICER 2024). 2024-09. Paper. https://arxiv.org/abs/2409.18661. **Sin verificar.**
21. Anthropic. «Checkpointing - Claude Code Docs». Documentación vigente consultada el 2026-09-28. Oficial. https://code.claude.com/docs/en/checkpointing. **Sin verificar.**
22. The Register (22/07/2025) y AI Incident Database #1152. Borrado de la base de producción por el agente de Replit (caso Jason Lemkin, SaaStr). 2025-07. Prensa e incidente documentado. Sin URL registrada. **Sin verificar.**
23. Karpathy, A. «Vibe coding MenuGen». 2025-04-27. Practicante (blog). https://karpathy.bearblog.dev/vibe-coding-menugen/. **Sin verificar.** El relato de Sajor (Stack Overflow, enero 2026), citado como apoyo sin URL: sin verificar.
24. Comunidad Vibe Coding Educativo (VCE). Boletín semanal, preguntas frecuentes y datos de la comunidad. 2025-07 a 2026-09. Practicante. https://vibe-coding-educativo.github.io/boletin/. **Sin verificar;** el conteo por palabras clave es aproximado.
25. Fischer, M. A. (OIA, Universidad del Aconcagua). «El cuestionario que se convirtió en aplicación: vibe coding aplicado a la práctica docente». 2026-03-27. Practicante. https://oia.uda.edu.ar/el-cuestionario-que-se-convirtio-en-aplicacion-vibe-coding-aplicado-a-la-practica-docente/. **Sin verificar.**
26. Superblocks (sobre la investigación de Matt Palmer). «Lovable Vulnerability Explained: How 170+ Apps Were Exposed». 2026-03-09. Prensa. https://www.superblocks.com/blog/lovable-vulnerabilities. **Sin verificar.**
27. Lovable. «Our response to the April 2026 incident». 2026-04. Oficial (empresa). https://lovable.dev/blog/our-response-to-the-april-2026-incident. **Sin verificar.**
28. Margulieux, L. E.; Prather, J.; Reeves, B. N.; Becker, B. A.; Cetin Uzun, G.; Loksa, D.; Leinonen, J.; Denny, P. «Self-Regulation, Self-Efficacy, and Fear of Failure Interactions with How Novices Use LLMs to Solve Programming Problems» (ITiCSE 2024, DOI 10.1145/3649217.3653621). 2024-07. Paper. https://research.aalto.fi/en/publications/self-regulation-self-efficacy-and-fear-of-failure-interactions-wi/ (resumen en https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3649217.3653621). **Verificada** sobre el resumen; no se pudo abrir el texto completo ni ver el tamaño de la muestra. Tran, Harper y Price (2026), citado como apoyo sin URL: sin verificar.
29. Lee, H.-P.; Sarkar, A.; Tankelevitch, L.; Drosos, I.; Rintel, S.; Banks, R.; Wilson, N. (Microsoft Research, CHI 2025). «The Impact of Generative AI on Critical Thinking: Self-Reported Reductions in Cognitive Effort and Confidence Effects From a Survey of Knowledge Workers». 2025-04. Paper. https://www.microsoft.com/en-us/research/publication/the-impact-of-generative-ai-on-critical-thinking-self-reported-reductions-in-cognitive-effort-and-confidence-effects-from-a-survey-of-knowledge-workers/. **Sin verificar.**
30. Avenburg, Bendersky, Judzik, Levy Yeyati y otros (CEPE-Di Tella y Fundar). «Encuesta Nacional sobre Adopción de IA en Argentina. Relevamiento Individuos Agosto-Septiembre 2025» (Documento de Políticas Públicas N.º 37). 2025-11. Encuesta (panel online de conveniencia, Netquest, 1.589 casos). https://repositorio.utdt.edu/items/3505760f-5658-4eb7-a504-08e4a53e19c3 (PDF: https://repositorio.utdt.edu/bitstreams/f39a5ac4-7525-4f1c-9cb5-6808e6f5132f/download). **Parcial:** el 2,1% es pago personal y el 89,1% es capacitación por cuenta propia, en adultos conectados; las cifras de barreras y uso, sin verificar. ChatGPT Go en Argentina (La Nación, 11/12/2025), citado junto a esta fuente: sin verificar.
31. AARP. «Navigating the world of AI». 2026-01. Encuesta. https://datastories.aarp.org/2026/navigating-the-world-of-ai/. **Sin verificar.**
32. Fawzy, A.; Tahir, A.; Blincoe, K. «Vibe Coding in Practice: Motivations, Challenges, and a Future Outlook – a Grey Literature Review» (ICSE-SEIP 2026). 2025-09-30. Paper. https://arxiv.org/abs/2510.00328v1. **Sin verificar.** Osmani (dic 2024), citado como apoyo sin URL: sin verificar.
33. Gardella, Prather, Leinonen, Denny, Pettit, Riggs. «Fast and Forgettable: A Controlled Study of Novices' Performance, Learning, Workload, and Emotion in AI-Assisted and Human Pair Programming Paradigms» (ICER 2026). 2026-08 (preprint abr-2026). Paper. https://arxiv.org/abs/2604.18538. **Verificada;** 22 participantes de nivel intermedio.
34. Urteaga, Siri, Garófalo (UTN). «Predicción temprana de deserción mediante aprendizaje automático en cursos profesionales en línea» (RIED). 2020. Paper. https://redalyc.org/jatsRepo/3314/331463171008/html/index.html. **Sin verificar.**
35. DPL News. «Laboratoria reinventa su formación ante la IA: el futuro del empleo exige nuevas habilidades». 2026-08-05. Prensa. https://dplnews.com/laboratoria-formacion-ia-empleo-nuevas-habilidades/. **Sin verificar;** resultados autodeclarados.
36. INDEC. «Acceso y uso de tecnologías de la información y la comunicación. EPH. Cuarto trimestre de 2024». 2025-05. Oficial. https://www.indec.gob.ar/uploads/informesdeprensa/mautic_05_25FD0D0C4A71.pdf (cuadros: https://www.indec.gob.ar/ftp/cuadros/sociedad/cuadros_tic_05_25.xls). **Verificada** (Cuadros 3 y 4); «computadora» incluye tablets y solo cubre 31 aglomerados urbanos. El dato de hogares y el de CEPAL (ONU Noticias, 29/08/2026), sin verificar.
37. Anthropic. «Get started with the desktop app - Claude Code Docs». Documentación vigente consultada el 2026-09-28. Oficial. https://code.claude.com/docs/en/desktop-quickstart. **Sin verificar.**
38. Anthropic. Página de precios de Claude. Consultada el 2026-09-28. Oficial. https://claude.com/pricing. **Sin verificar;** puede cambiar.
39. OpenAI. Precios y planes de Codex. Consultada el 2026-09. Oficial. https://learn.chatgpt.com/docs/pricing. **Sin verificar;** puede cambiar.
40. The Register. Nota sobre los precios de Replit Agent 3. 2025-09-18. Prensa. https://www.theregister.com/2025/09/18/replit_agent3_pricing/. **Sin verificar.**
41. Anthropic. «How to use Claude in your preferred language» (Claude Help Center). 2026-08-06. Oficial. https://support.claude.com/en/articles/10769299-how-to-use-claude-in-your-preferred-language. **Sin verificar.**
42. Wajid, A.; Camacho Zúñiga, C. (Tecnológico de Monterrey, TecScience). «La facilidad de interacción con ChatGPT puede aumentar su uso entre estudiantes de programación». 2026-08-28. Prensa institucional. https://tecscience.tec.mx/es/educacion-y-humanismo/chatgpt-estudantes-de-programacion/. **Sin verificar;** el paper original (DOI 10.1155/hbe2/8254212) no se pudo abrir.
43. Lovable. «A first look at the build economy». 2026-06. Datos de plataforma. https://lovable.dev/blog/a-first-look-at-the-build-economy. **Sin verificar;** datos propios con fines de marketing.
44. Lovable. Guía de buenas prácticas. Documentación vigente. Oficial (empresa). https://docs.lovable.dev/tips-tricks/best-practice. **Sin verificar.**
45. Kazemitabaar, M.; Hou, X.; Henley, A.; Ericson, B. J.; Weintrop, D.; Grossman, T. «How Novices Use LLM-Based Code Generators to Solve CS1 Coding Tasks in a Self-Paced Learning Environment» (Koli Calling 2023). 2023-09 (preprint). Paper. https://arxiv.org/abs/2309.14049. **Parcial:** la aportó un verificador para matizar [2] (el enfoque de un solo pedido tuvo la mayor corrección al escribir y la menor al modificar); el 66% que citaba el borrador no se verificó.
