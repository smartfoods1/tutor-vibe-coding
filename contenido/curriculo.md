# Mapa del curso

> **Estado:** borrador pendiente de aprobación del autor (T023), con las correcciones de dos revisiones. **Fecha:** 2026-09-28.
> **Base:** la investigación verificada de `contenido/investigacion/` (informes 01 a 05; cuando chocan, manda el 05), más el spec 001, la constitución 1.0.2, los contratos del kit, la API y los mails, el guion de 10 turnos, el machete vigente y las decisiones del autor del 28/9.
> **Cómo leerlo en dos líneas:** cada módulo dice qué hace la persona, qué hace el tutor, cuándo está terminado y qué se mide, y cada decisión lleva su referencia ("03 [5]" es la fuente 5 del informe 03) o la marca *apuesta*.
> Lo marcado V1, V2 o V3 espera las pruebas de viabilidad, que al 28/9 no se corrieron (`viabilidad.md` tiene las tablas, sin resultados).
> **Advertencia general:** ningún estudio verificado trabajó con adultos de 30 a 60 años que nunca programaron. Todo lo que sigue es hipótesis de diseño que el piloto y los primeros alumnos tienen que medir.

## Principios pedagógicos

Diez principios. Cada uno dice qué hace el curso, en qué evidencia se apoya y con qué fuerza. La fuerza (fuerte, media o débil) y el estado (verificada o confirmada, corregida, sin verificar) son los que dejó cada informe; si el 05 recalifica una fuente, vale el 05.

**1. La idea propia es el hilo, y la primera versión entra en un molde probado antes en las dos herramientas.**
- *En el curso:* todo se hace sobre la idea del alumno (Constitución I). El tutor la achica sin reemplazarla, pregunta antes de sugerir y recién después ofrece una forma de página que ya se probó (un molde cuenta como probado cuando anduvo en las dos herramientas, V2).
- *Evidencia:* conectar lo que se aprende con la propia vida rindió más en quienes esperaban que les fuera mal, 05 [63] (media, confirmada; secundaria, alumnos con bajas expectativas). Contrapeso: en cursos en línea a escala, el efecto fue chico e inconsistente, y en algunos cursos negativo, 03 [31]; 05 [80] (fuerte); es el formato más parecido a este. Completar algo que ya funciona redujo el abandono, 05 [64] (media, confirmada; secundaria). Según datos de uso de Anthropic, guiar al agente depende más de dominar el tema que de saber programar; es la interpretación de la propia fuente, con ocupación y pericia inferidas por Claude y un grupo de comparación que incluye ingenieros, 01 [1] (media, corregida; dice poco sobre la tribu, 01, tensión 5). Las ideas que propone la IA mejoran cada caso pero los vuelven parecidos, 05 [68] (media, confirmada).
- *Fuerza:* media para cada pieza. Juntar idea propia y molde es *apuesta*: nadie comparó las dos cosas en adultos (05, hueco 4). Que el "por qué te importa" sostenga en los bajones también es *apuesta*: se mide en el piloto (quién lo retoma y quién abandona después de un tropiezo).

**2. Primero una victoria propia, terminada en la primera sesión y en dos momentos: verla andar y después publicarla.**
- *En el curso:* una versión mínima, diseñada para que falle lo menos posible (un título, una frase y un solo elemento que responde), vista en la compu antes de publicarla. El logro se atribuye a lo que la persona eligió, predijo y comprobó, con devolución concreta.
- *Evidencia:* los logros propios son la fuente más asociada con la autoeficacia, 03 [5] (fuerte para la asociación, verificada; no prueba que diseñarlos la suba). Contrapunto: en intervenciones con adultos de otro dominio (actividad física), el feedback y ver a otros pesaron más que la maestría graduada, 03 [52] (media); por eso la victoria va acompañada de devolución clara y del audio de alguien que tropezó. Lo que uno arma vale más solo si lo termina, 05 [62] (media, corregida). Con un generador de código mejoraron los primeros resultados y las ganas de seguir, sin daño en la retención, 01 [2] (fuerte, corregida; chicos de 10 a 17 años, y no mejoró el post-test sin IA). Límite: el tutor con barandas evitó el daño pero dejó confianza de más, 03 [22] (fuerte, verificada), y la confianza en uno mismo, no en la IA, se asocia con más pensamiento crítico, 02 [38] (media, verificada). Los dos momentos salen de 05, hueco 1.
- *Fuerza:* fuerte para la asociación; media para el diseño, y más baja por el contrapunto de 03 [52] y porque 01 [2] es con chicos.

**3. Mucha guía y un paso por vez. Las decisiones son de la persona, antes y después del único pedido completo de la versión mínima.**
- *En el curso:* el tutor explica antes de actuar, da ejemplos antes de pedir y frena los pedidos gigantes. Para la versión mínima acepta un pedido completo, con las decisiones tomadas antes (molde, textos, elemento que responde) y un primer cambio propio justo después.
- *Evidencia:* con poco conocimiento previo se aprende más con mucha asistencia (d ≈ 0,51), y ante la duda conviene dar ayuda, 03 [12] (fuerte, corregida). La tutoría que acompaña cada paso rinde más que la que corrige al final, 03 [20] (fuerte, sin verificar). Un agente que edita todo baja la comprensión, 01 [14] (media, corregida). Resolver todo en un pedido se asoció con peor capacidad de modificar después, 01 [45] (media; chicos que escribían código). La conciliación entre pedido único y decisiones propias es 05, contradicción 2.
- *Fuerza:* fuerte para la guía; media para el paso a paso. Aflojar la guía cuando la persona ya puede es *apuesta*: 03 [12] lo deja como investigación pendiente.

**4. El miedo va repartido y pegado a la acción, nunca como charla suelta.**
- *En el curso:* cada miedo se nombra en una frase cuando aparece y se responde con un hecho del curso y un gesto concreto (tabla en Transversales). El módulo 1 es liviano.
- *Evidencia:* reinterpretar el estrés tiene un efecto chico (d = 0,23; cerca de 0,14 al corregir por sesgo), algo mayor combinado con otro contenido, 03 [9] (media, corregida). Los ejercicios reflexivos al inicio no movieron la finalización a escala, 03 [31] (fuerte, corregida). Lo que acompaña a la ansiedad es la falta de experiencia y de autoeficacia, y eso cambia, 03 [1][2] (media, corregidas). Ver los propios resultados cambia las creencias sobre el error más que una explicación, 05 [48] (media, corregida). La queja más citada por adultos mayores que aprenden a programar es la mala didáctica, 05 [71] (media, corregida).
- *Fuerza:* media.

**5. El error se encuadra neutro, no se celebra, y la red de seguridad existe desde la primera publicación.**
- *En el curso:* "si no pasó lo que esperabas, encontraste algo". Volver a una versión se ensaya en el módulo 4, cuando no hay nada en juego, y se enseña a fondo en el 6.
- *Evidencia:* el entrenamiento con manejo de errores, que combina explorar con el aviso explícito de que los errores son esperables y útiles, superó al que los evita: d = 0,44 en general, 0,56 en transferencia y 0,80 en tareas distintas de las practicadas; en 55 estudiantes que aprendían un programa, d = 0,75 en transferencia, en parte por el control emocional, 05 [47] (fuerte, confirmada; entrenamientos cortos). El curso no usa ese encuadre sino uno neutro, que no celebra el error y casi no tiene exploración (salvo la práctica opcional del módulo 6). Ese giro sale de que alentar el error bajó la autoeficacia de personas muy responsables, 03 [51] (media, sin verificación independiente), y de que centrarse en el error no le conviene a todos, 03 [11] (media, corregida). La ansiedad se asocia con más reacción ante los errores propios, 05 [46] (media, corregida).
- *Fuerza:* fuerte, en promedio, para el entrenamiento con manejo de errores de 05 [47]; media para el encuadre neutro que usa el curso, que es una adaptación a partir de 03 [11][51]. Que la red esté desde el módulo 4 es decisión de diseño (05, afirmación 3), y que todo esto valga para errores que genera la IA no está probado (05, afirmación 8).

**6. Predecir en dosis chica: de trazo grueso, en momentos clave y salteable sin culpa.**
- *En el curso:* una línea sobre lo que se va a ver en la página, antes de verlo. En las lecciones 5 y 6 la invitación está en cada pedido, como pide FR-017, pero ocupa media línea; en los momentos clave se sostiene y en los cambios obvios ya viene con la oferta de saltearla. Sin puntaje.
- *Evidencia:* trazar el código línea por línea llevó 2,7 veces el tiempo y frustró; anticipar en palabras llevó entre 1,5 y 1,8 veces, sin más carga, y ninguna técnica mejoró el desempeño posterior, 05 [50] (media, corregida; universitarios de computación). Mirar sin predecir casi no mejora la explicación (24% contra 22%) y predecir sí, poco (30%), 05 [37] (media, corregida). Lo que sostiene el "no en cada cambio" es otra cosa: el beneficio se concentra en lo que sorprende, 05 [39] (media, confirmada), y las pruebas previas bajaron la persistencia en un curso abierto, 05 [45] (media, corregida). Tampoco conviene dejarlo solo como opción, porque la gente subestima estas estrategias, 05 [48]; que lo salteen justo quienes más lo necesitan es plausible, no probado.
- *Fuerza:* media en otros dominios; débil para la tribu. Nadie lo probó con adultos que no programan ni con una página (05, hueco 3).

**7. La persona cuenta con sus palabras qué cambió, en dos momentos y sin compuerta: después de un arreglo y antes de la publicación final.**
- *En el curso:* "contame qué cambió en tu página". "No sé" vale: el tutor explica y sigue.
- *Evidencia:* con una compuerta que obligaba a explicar, falló al arreglar sin IA el 39%, contra el 77% del grupo con IA libre, y la compuerta costó una mediana de 14,2 minutos, 05 [28] = 01 [12] (débil, confirmada: preprint de un autor, con gente que sabía JavaScript). El tutor con barandas solo evita el daño, sin sumar aprendizaje, 01 [10] (fuerte, verificada). Un tutor con andamiaje se percibió menos útil, 05 [29] (débil, confirmada: preprint con 17 personas y un tutor de estrategia, no una compuerta de explicación).
- *Fuerza:* débil. Que contar qué cambió en la página sirva igual a quien no lee código es *apuesta* (05, afirmación 7). Por eso son solo dos momentos.

**8. Lo que no puede fallar vive en la estructura: no depende de que la persona lea aprobaciones ni de que el agente se acuerde.**
- *En el curso:* carpeta propia, permisos endurecidos desde el kit (en Claude, `acceptEdits` fijo), `versiones/` visible y protegida, contador de intentos en un archivo visible y, en Claude, hooks desde el kit inicial que vuelven a poner las reglas críticas en cada turno y después de compactar (05, hueco 2). La pausa pedagógica la hace el tutor: es conducta, no estructura, y por eso es lo que más depende de V2.
- *Evidencia:* la gente aprueba entre el 93% y el 97% de los permisos y frenó un comando peligroso solo el 13,6% de las veces, 02 [28][55] (media, verificadas; datos del fabricante). Las instrucciones se diluyen con los turnos, 05 [24], y con instrucciones de unas 1.700 palabras en promedio el mejor cumplimiento completo fue del 27,2%, 05 [27] (media, confirmadas). Un kit corto ayuda pero no garantiza la conducta: lo que no puede fallar va a hooks, permisos y archivos visibles (05, afirmación 6 y hueco 2). Los checkpoints no registran lo que hacen los comandos, 05 [31], y "Accept edits" aprueba borrar dentro de la carpeta, 05 [32]. Un agente dio por imposible una recuperación que era posible, 05 [36] (débil).
- *Fuerza:* media. En Codex, `AGENTS.md` y los archivos visibles son la capa base, y los hooks quedan como refuerzo hasta ver en la app cómo se aprueban (05 [23]): ahí la conducta depende más del agente, y eso es *apuesta*. Cuánto se diluye la conducta en una sesión larga con un novato no está medido (05, hueco 2): V2 suma una sesión larga para verlo.

**9. Lenguaje llano, pocas palabras nuevas y justo cuando hacen falta, en sesiones cortas.**
- *En el curso:* una palabra técnica por vez, con su equivalente en inglés cuando aparece en pantalla; sesiones de 30 a 40 minutos que cierran en algo guardado (la primera victoria es la excepción: 75 minutos, con techo de 90); una conversación nueva entre etapas. La duración de las sesiones es *apuesta*: ninguna fuente da minutos, solo que la conversación larga se degrada y que dirigir cansa. Se mide en el piloto.
- *Evidencia:* la mala didáctica (jerga, saltos de dificultad) es la queja más citada, 05 [71] (media, corregida). Los detalles interesantes pero no esenciales restan, 03 [33] (fuerte, sin verificar). Faltan palabras técnicas en la propia lengua, 01 [7] (media, sin verificar). En Argentina la barrera más declarada es no saber cómo ni para qué, 01 [30] (media, sin verificar). Las conversaciones largas se degradan, 05 [24][25][26] (media), y dirigir a la IA cansa, 02 [8] (débil).
- *Fuerza:* media.

**10. El autor acompaña, no enseña: un audio corto por módulo, de una traba real, al principio y fuera del momento de hacer.**
- *En el curso:* audios de 2 a 3 minutos, grabados una sola vez, con transcripción, salteables, que cierran con una pregunta que retoma el tutor. El tutor nunca imita la voz del autor.
- *Evidencia:* las historias de lucha conectan más que las de logro (d entre 0,35 y 0,53) y casi no mueven el aprendizaje, 03 [6] (media para la conexión, débil para el aprendizaje); los estudios posteriores dan resultados mixtos, 03 [53][54][55]. Las piezas cortas y personales enganchan más, 03 [47] (media, sin verificar). Ver a alguien que tropieza y sigue sube más la autoeficacia que ver a alguien perfecto (Schunk, citado en 03 [6], sin verificar; con chicos). Un modelo funciona si la tribu lo percibe parecido a ella, no exitoso y distinto, 03 [6][54]: el efecto del audio depende de que el autor se perciba como par.
- *Fuerza:* débil. No hay evidencia sobre audios del autor y finalización (01, 03 y 04, "Lo que no sabemos"): se mide, y en el piloto se pregunta además si el autor se siente como alguien parecido o como alguien distinto.

## El recorrido de un vistazo

Antes del módulo 1 va la portada, que no es un módulo: qué se logra (tu idea publicada como una página con link), cuánto lleva, dicho como estimación ("calculamos unas 5 horas, repartidas en varios días; lo estamos midiendo"), que desde el módulo 3 hace falta una computadora Mac o Windows y cuánto cuesta cada camino, con fecha. Así el costo no aparece por sorpresa en el módulo 3. Es una recomendación del 05, hueco 5, sin datos de este público. Lo que la portada dice sobre costos depende de V1 y V3: "gratis" para Codex y para Netlify aparece recién con `probado: true` en el machete.

| Módulo | Dónde pasa | Duración: presupuesto (techo) | Qué se lleva el alumno | Estado |
|---|---|---|---|---|
| Portada (no es un módulo) | Web | 3 min | Qué se logra, cuánto lleva (como estimación), qué computadora hace falta y el costo de cada camino, con fecha | **Depende de V1 y V3:** "gratis" solo con `probado: true` |
| 1. Cómo piensa un vibe coder | Web, desde el celular, por texto o voz | 12 min (15) | Qué parte del vibe coding toma el curso, sus miedos con nombre y con un lugar en el recorrido, y la semilla de su idea con por qué le importa | Listo. No menciona planes ni "gratis": eso va al módulo 3 |
| 2. Tu idea en una página | Web, desde el celular | 22 min (25) | `mi-idea.md`: para quién, por qué le importa, la versión mínima, el molde y "qué sigue" | Listo. Los moldes se prueban en V2 y en el piloto |
| 3. Tu taller | Web, desde la computadora | 45 min (60), con descargas | Su herramienta instalada, la cuenta para publicar lista y el kit en una carpeta fija, con la app contestando a "hola, probando" | **Borrador:** V1, V2 y V3 |
| 4. Primera victoria | Su herramienta, con el kit | 75 min (90) | Su idea andando, publicada con un link, la versión "primera" guardada, un cambio propio y una vuelta atrás ensayada | **Borrador:** V1, V2 y V3 |
| 5. Construir | Su herramienta, en una o dos sesiones de hasta 40 minutos | 70 min (80) | La página mejorada paso a paso, versiones con nombre y un cuaderno con lo que esperaba y lo que vio | Listo en lo pedagógico, con la invitación a predecir en cada pedido (FR-017); la conducta del tutor depende de V2 y el cupo, de V1 |
| 6. Cuando se rompe | Su herramienta | 35 min (45) | Volver por su cuenta a una versión, contar un error con "hice, esperaba, vi", la regla de los dos intentos y una copia de su carpeta | Listo en lo pedagógico; la conducta del tutor depende de V2 |
| 7. Terminar y mostrar | Su herramienta y la web | 45 min (55) | La versión final publicada en el mismo link, revisada, un cambio hecho sin ayuda y el link registrado | **Borrador:** V3 (y V1, V2) |

- **Tiempos (*apuesta*: no hay datos de este público; 05, hueco 5).** Los módulos 1 y 2 suman 34 minutos, con techo de 40 (SC-003). Con la portada, los presupuestos suman 5 h 07 y los techos, 6 h 13: la mediana entra en SC-004 solo si la mayoría queda cerca del presupuesto, y lo que más puede romperlo es el módulo 3 y el cupo de Codex gratis. La primera publicación está pensada para el minuto 55 de la primera sesión en la herramienta, con techo de 90 (SC-002). El reloj de SC-002 arranca con el "empecemos" de la lección 4, no con la prueba del módulo 3. Los audios están incluidos. Cómo se mide cada tiempo: ver Medición.
- **Los dos momentos de más riesgo:**
  - *Instalar (módulo 3):* el primer paso con una barrera concreta (cuenta, a veces pago, pantallas en inglés, pasar del celular a la compu). Es el candidato más fuerte a punto de fuga, sin datos de abandono (05, hueco 5).
  - *El primer error (módulo 4):* las sesiones novatas se abandonan unas tres veces más (19% contra 5 a 7%) y, cuando se traban, casi no se recuperan (4% contra 15% de éxito), 01 [1] (media, corregida).
- **La curva que busca el diseño (*apuesta*):** duda al entrar; alivio en el 1 (todavía no hay que saber nada); entusiasmo con algo propio en el 2; esfuerzo acompañado en el 3; "existe" en el 4; avance con cansancio en el 5; susto que se vuelve criterio en el 6; orgullo y exposición en el 7.

## Módulo 1: Cómo piensa un vibe coder

- **Objetivo:** que la persona sepa de dónde viene el vibe coding y qué propone el curso (construir con IA pensando en el resultado, sin pensar en cómo se construye la solución); que se ubique en el reparto de roles (vos pensás y decidís, la máquina escribe, vos mirás); que nombre lo que la frena y reciba una respuesta concreta; y que cierre contando con sus palabras qué le gustaría que exista y por qué le importa (FR-007, FR-012).
- **Audio del autor:**
  - *Cuándo:* apenas entra, antes de la primera palabra del tutor, con la transcripción al lado. Se puede saltear sin que el módulo se bloquee.
  - *Qué tipo de historia cuenta:* una traba real, no un logro. Alguien que no venía de la tecnología y empezó creyendo que esto no era para él: de dónde venía y qué sintió la primera vez que vio en pantalla algo que solo estaba en su cabeza. Arranca por una escena concreta con fecha (03 [6]).
  - *Idea eje (punto de partida, no una línea para decir):* yo también empecé creyendo que esto no era para mí.
  - *Cierra con una pregunta que retoma el tutor:* ¿qué te gustaría que exista?
  - *No dice:* la historia de Karpathy (la cuenta el tutor); precios, planes, nombres de apps ni botones, porque se vencen y el audio se graba una vez (FR-028); nombres de empresas ni métricas propias; promesas de que es fácil.
- **Conceptos** (pocos; el resto se reparte donde se usa, 05, contradicción 9):
  1. *El origen.* Karpathy nombró el vibe coding el 2/2/2025 para una forma de trabajar en la que aceptaba todos los cambios sin leerlos, pegaba los errores sin comentario y se olvidaba de que el código existía. Le pareció aceptable para proyectos descartables de fin de semana, como valoración al pasar, 02 [2][1] (media, corregidas).
  2. *Qué propone el curso.* Desarrollar habilidades para construir con IA pensando en el resultado, sin pensar en cómo se construye la solución (redacción de Andrés, 29/9): la persona define qué quiere que exista y cómo se da cuenta de que funciona; del cómo se ocupa la máquina. Describir, predecir, mirar y guardar versiones es la versión chiquita de la disciplina que el propio Karpathy separa del vibe coding, 02 [5] (corregida). En una línea: el vibe coding "sube el piso", deja que casi cualquiera cree algo describiéndolo, 02 [5].
  3. *El reparto de roles:* vos pensás y decidís, la máquina escribe, vos mirás. Al alumno se le da como pista, no como hallazgo: "lo que sabés del tema de tu idea te va a servir para guiarla". Viene de datos de uso de Anthropic que la propia fuente interpreta así, 01 [1] (media, corregida).
  4. *Expectativas realistas, en dos líneas:* calculamos unas 5 horas en varios días y lo estamos midiendo; algo se va a romper y está previsto; qué ve la IA y que lo publicado lo ve cualquiera. 03 [43] (recomendación de los autores, sin verificar); 01 [30] y 03 [3] (sin verificar).
  - Van a otros módulos: el error como información se dice en una frase y se practica en el 4 (05 [48]); el recorte de Willison va al 2; "dirigir cansa", al 5; "carpeta, versión, publicar", al 3.
- **Actividad paso a paso** (celular; unas 6 a 8 respuestas del tutor, para que cada respuesta escrita desde el celular tenga más de un minuto; se prueba en el quickstart §3 con alguien de la tribu):
  1. Escucha el audio o lee la transcripción.
  2. El tutor se presenta como el tutor del curso y pregunta "¿qué te trajo hasta acá?", para contestar en una o dos líneas, por texto o por voz.
  3. El tutor cuenta el origen y qué propone el curso en tres o cuatro frases y pregunta: "con tus palabras, ¿qué parte hacés vos y qué parte la máquina?". Una línea alcanza; si no cierra, la completa sin corregir como en un examen.
  4. El miedo, con cuatro opciones de un toque más respuesta libre: romper algo en la compu; no entender nada; gastar plata; "ya estoy grande para esto". Cuatro opciones es una decisión de diseño (*apuesta*); de 03 [32] y 05 [67] solo sale que elegir motiva poco a los adultos. Otros miedos (que quede feo, tener que mostrarlo) entran por la respuesta libre y se atienden en los módulos 4 y 7. El tutor no discute el miedo: contesta con un hecho del curso y le dice en qué módulo se atiende (ver la tabla de Transversales). Por ejemplo: la herramienta trabaja solo dentro de una carpeta; cada paso se explica antes; desde la primera publicación hay copias guardadas; "antes de instalar nada vas a ver el costo de cada camino, con fecha" (sin mencionar planes gratis ni precios: eso va al módulo 3). Ante "ya estoy grande", no lo niega: con más edad suele haber algo más de ansiedad, pero lo que pesa es la falta de experiencia y de confianza, y eso es justo lo que el curso construye, 03 [1][2].
  5. **Cierre:** "contame qué te gustaría que exista y por qué te importa", en dos o tres líneas. Si no se le ocurre nada, el tutor pregunta de qué sabe mucho y a quién le gustaría mostrarle algo. Si sigue en blanco, ofrece tres familias bien distintas (algo para expresar, una herramienta útil, un ritual), nunca un ejemplo único, 04 [26] (media); 05, hueco 4. El tutor deja en el resumen del módulo, que lee el módulo 2, la semilla en una línea neutra y las categorías genéricas de miedo (por ejemplo, "costo" o "romper la compu"), sin frases textuales, sin edad y sin datos de salud (spec, Retención; research §16). El "por qué me importa" se vuelve a preguntar en el módulo 2 y vive en la idea, que el alumno puede borrar. Marca el avance (`marcar_avance`).
  - *Sin tutor (tope alcanzado, FR-026):* la guía escrita trae el audio, los conceptos en media página y las dos preguntas (qué te frena y qué te gustaría que exista) como formulario; "ya lo hice" marca el módulo.
- **Qué hace el tutor y qué no hace:**
  - *Hace:* mensajes cortos, una pregunta por vez; opciones de un toque más respuesta libre; explica cada palabra técnica la primera vez; contesta el miedo con hechos, no con aliento.
  - *No hace:* presentarse como el autor ni imitar su voz (FR-006); dar una charla de mentalidad (en el mercado, la charla inicial se saltea, 04 [1], débil: es relativo al mapa de YouTube y a un público emprendedor); proponer ideas antes de que la persona cuente la suya (05, hueco 4); prometer que es fácil, que es rápido o que la idea va a dar plata (Constitución I); hablar de planes, precios o "gratis", ni repetir lo que informa OpenAI sobre su plan gratis, porque para este público suena a "es gratis" (Constitución IV; SC-008); diagnosticar: ante un malestar serio sigue el protocolo (FR-032, research §15).
- **Terminado cuando:** la persona dijo con sus palabras el reparto de roles, en una línea, y dejó dos o tres líneas sobre qué le gustaría que exista y por qué le importa, y quedó registrado `modulo_completo` con `modulo=1`.
- **Dónde se traba y cómo se previene:**
  - *Que se sienta una clase:* el módulo es para hacer y se corta en 12 minutos (03 [31]; 04 [1]).
  - *Jerga o saltos de dificultad:* una palabra técnica por vez (05 [71]).
  - *"No se me ocurre nada":* familias, no ejemplos, y siempre después de preguntar.
  - *El dictado no entiende el voseo:* no hay evidencia sobre cómo transcribe el rioplatense (01, "Lo que no sabemos"); el texto está siempre disponible.
  - *La charla se vuelve un desahogo:* presupuesto de respuestas y, si es un malestar serio, el protocolo.
- **Qué se mide:** `inscripcion` (con `fuente`) y `modulo_completo` con `modulo=1` y `via` (tutor o guía escrita). La duración activa sale de las marcas de las sesiones, como se explica en Medición. El miedo elegido no se guarda como dato aparte: solo su categoría genérica, dentro del resumen.
- **Evidencia:** 01 [1][30]; 02 [1][2][5]; 03 [1][2][3][6][9][31][32][43]; 04 [1][26]; 05 [48][67][71], contradicción 9 y hueco 4.
- **Estado:** listo para escribir la guía del tutor y la guía escrita (T048). No depende de las pruebas: ante el miedo a gastar plata, el tutor solo dice que antes de instalar va a ver el costo de cada camino, con fecha. La frase sobre Codex vive en el módulo 3, que está en borrador, y no usa la palabra "gratis" hasta que se cumplan V1 y SC-008.

## Módulo 2: Tu idea en una página

- **Objetivo:** convertir la semilla en "mi idea en una página", que se lee en dos minutos (FR-008, FR-009): qué es y para quién, qué siente la persona al imaginarla funcionando y por qué le importa, la versión mínima (la más chica que ya valdría la pena, FR-008), el molde, cómo se va a dar cuenta de que funciona y "qué sigue". La idea sigue siendo suya: el tutor la achica, no la reemplaza.
- **Audio del autor:**
  - *Cuándo:* al abrir el módulo, antes de la entrevista.
  - *Qué tipo de historia cuenta:* una traba real, no un logro: una idea suya que tuvo que achicar o recortar para que existiera, y qué sintió al dejar lo grande para después. Se cuenta sin nombres de apps.
  - *Idea eje:* para que exista, la tuve que achicar, y lo que quedó afuera no se perdió.
  - *Cierra con:* ¿cuál es la versión más chica de tu idea que ya te daría ganas de mostrar?
  - *No dice:* consejos de negocio ni cifras; nombres de apps y servicios; nada que se venza.
- **Conceptos:**
  1. *Qué es una página que funciona.* Lo que no entra tiene dos salidas (decisión del 28/9): guardar en el propio dispositivo, donde cada visitante ve solo lo suyo, 05 [57][58] (media, confirmadas), y links que salen de la página (agenda, WhatsApp con el mensaje armado), 05 [59]. Si un link de pago cuenta como link externo permitido lo decide el autor (Decisiones); hasta entonces no se ofrece.
  2. *Las exclusiones como cuidado:* tu página no guarda datos de nadie, así que nadie te los puede robar, 05 [61] (media, corregida); 02 [47]. Acá entra el recorte de Willison: está bien construir así cuando un error no lastima a nadie, no cuando hay datos ajenos, 02 [1][3] (débil: postura de un practicante).
  3. *La versión mínima,* la más chica que ya valdría la pena (FR-008): un título, una frase y un solo elemento que responde (un botón, una pregunta, un temporizador) (05, hueco 4). Como criterio interno, se diseña para que falle lo menos posible; al alumno no se le promete que no va a fallar.
  4. *El molde* es la forma de la página: tarjeta, guía paso a paso, test o ritual con temporizador (05, hueco 4).
  5. *Lo que la máquina no puede adivinar:* para quién es, qué se ve primero, qué pasa al tocar cada cosa, los textos exactos y cómo se ve en el celular, 01 [5] (fuerte en su contexto, corregida). Y "sé que funciona si...", en una frase, 02 [20] (media, corregida).
- **Actividad paso a paso** (celular; unas 12 a 15 respuestas del tutor; lo marcado con \* es el núcleo obligatorio, que protege SC-003):
  1. Escucha el audio.
  2. \* El tutor lee la semilla del módulo 1 y pregunta de a una: para quién es (para vos, para regalar o para vender), quién más la usa, qué tendría que quedar guardado (05, hueco 4) y de qué sabe mucho (01 [1]).
  3. \* "¿Qué sentís cuando la imaginás funcionando?" La persona escribe en dos o tres líneas por qué le importa. Eso va arriba de la página de la idea y el tutor lo trae de vuelta en los bajones, 05 [63] (media; en secundaria). Que eso sostenga a este público es *apuesta*: en cursos en línea a escala el efecto fue chico e inconsistente, 03 [31]; 05 [80]. Se mide en el piloto.
  4. \* Divergir antes de achicar: "si tu página solo pudiera hacer una cosa, ¿cuál sería? ¿Y otra bien distinta?". Las dos o tres versiones salen de la persona. El tutor ayuda con preguntas, propone solo si se traba y siempre variantes de su idea, nunca ideas nuevas, 01 [3] (débil, corregida); 05 [68].
  5. \* Elige una. Si pide login, pagos, datos compartidos o IA adentro, el tutor separa el corazón de la idea de la infraestructura, ofrece la salida que corresponde y anota el resto en "qué sigue" (FR-009). Si el corazón es un intercambio vivo entre personas, lo dice claro y ofrece la versión vidriera como primer paso.
  6. \* Recién ahora aparecen los moldes, 3 o 4, cada uno con un ejemplo corto y bien distinto de los otros (con un solo ejemplo, una participante lo copió, 04 [26]). Elige uno. Elegir motiva poco a los adultos, 05 [67]: el molde está para que la primera versión ande, no para entusiasmar.
  7. Si hay tiempo: los textos exactos, qué pasa al tocar el elemento que responde y "sé que funciona si...". Si no, se decide al empezar la lección 4.
  8. \* El tutor arma la página de la idea (`guardar_idea`). La persona la lee, la corrige y la puede editar y descargar (US2-4).
  - *Estructura de `mi-idea.md`* (una hoja que se lee en dos minutos): qué es; para quién; qué siento cuando la imagino funcionando y por qué me importa; la versión más chica que ya valdría la pena; el molde; lo que la máquina no puede adivinar; sé que funciona si; qué sigue.
  - *Sin tutor:* la guía escrita con la plantilla de la idea (`contenido/ejemplos/plantilla-idea.md`, T032), la lista de salidas y los moldes con sus ejemplos.
- **Qué hace el tutor y qué no hace:**
  - *Hace:* pregunta antes de sugerir y devuelve lo entendido con las palabras de la persona. Si la idea toca salud, datos de otras personas o algo íntimo, avisa que el link lo puede ver cualquiera y propone una versión sin datos personales (spec, casos borde); no repite ni guarda datos de salud (research §16).
  - *No hace:* mostrar moldes antes de que la persona cuente su idea; reemplazarla por una "mejor"; empujar hacia un test o un temporizador porque es fácil de hacer (se mide); prometer que va a vender; escribir la página todavía.
- **Terminado cuando:** hay una versión de `mi-idea.md` guardada con para quién es, por qué le importa, la versión mínima, el molde y "qué sigue" (aunque esté vacío); la persona la vio y la pudo descargar; y quedó `modulo_completo` con `modulo=2` (la API ya exige una idea guardada).
- **Dónde se traba y cómo se previene:**
  - *Achicar le saca lo valioso,* que muchas veces es el vínculo, 05 [55][56] (débil). Se dice, no se disimula: el "por qué te importa" queda visible y lo grande va a "qué sigue", no a la basura.
  - *La idea es una automatización personal* (ordenar fotos, contestar mails): se rescata la parte que se muestra o se dice con honestidad que queda afuera (05, hueco 4).
  - *Pide turnos, cobros o clientes,* probable en quien tiene un emprendimiento, 05 [54] (débil): salidas por link.
  - *Quedarse con la primera ocurrencia:* paso 4. *La tentación de agrandar,* que el mercado empuja, 01 [43] (débil): "qué sigue".
  - *El tiempo:* si pasa de 25 minutos, con el núcleo alcanza; lo demás se decide al empezar la lección 4.
  - *Termina en el celular y no vuelve:* el módulo 3 exige la compu. El único puente es el recordatorio de los 3 días (FR-025), en tono de pregunta (ver Medición).
- **Qué se mide:** `modulo_completo` con `modulo=2` y `via`; las versiones de la idea y si la editó la persona (`ideas.autor`); el tiempo activo de los módulos 1 y 2 juntos (SC-003, ver Medición). Propuesta sin datos personales: sumar `molde=<x>` al detalle del evento, para ver si el tutor empuja todo a lo mismo (05, hueco 4).
- **Evidencia:** 01 [1][3][5][43]; 02 [1][3][20][47]; 03 [31]; 04 [26]; 05 [54][55][56][57][58][59][61][63][67][68][80], hueco 4.
- **Estado:** listo para escribir (T048). Queda abierto qué ideas trae de verdad la tribu (05, hueco 4). Los moldes se prueban en las dos herramientas (V2) y en el piloto: un molde cuenta como probado recién cuando anduvo en las dos.

## Módulo 3: Tu taller

- **Objetivo:** que la persona elija una herramienta sabiendo el costo real, la instale sin terminal, deje lista la cuenta donde va a publicar y abra el kit con su idea adentro, sin que se sienta un examen técnico (FR-010, FR-011, FR-013). Todo lo que pide cuentas o configuraciones se resuelve acá, donde el tutor de la web puede leer capturas, y no en la primera victoria (05, hueco 1).
- **Audio del autor:**
  - *Cuándo:* al abrir el módulo, antes de elegir. Nunca en medio de una instalación.
  - *Qué tipo de historia cuenta:* una traba real, no un logro: algo que le costó al instalar o configurar (una pantalla en inglés, un permiso que no entendía, un paso que en un video duraba segundos) y cómo siguió: pidió ayuda, volvió al otro día. Si el autor no tiene un caso, el miedo a romper la computadora y qué lo calmó. Ver a alguien que tropieza y sigue ayuda más que ver a alguien que lo hace perfecto (Schunk, citado en 03 [6], sin verificar y con chicos; el modelado con aciertos y errores transfiere más, 03 [7], fuerte, sin verificar). Funciona si el autor se percibe como par (03 [6][54]).
  - *Idea eje:* trabarse al instalar no dice nada de vos.
  - *Cierra con:* ¿qué computadora vas a usar? Y si te trabás, mandá una captura.
  - *No dice:* nombres de apps, planes, precios ni pasos. Cambian cada pocas semanas: la app de Codex pasó a ser un modo de la app de ChatGPT el 9/7/2026, 05 [23].
- **Conceptos** (dados justo cuando hacen falta; una capa mínima de conceptos es *apuesta* con respaldo correlacional, 02 [41]):
  1. *El mapa mínimo:* tu página es una carpeta; una versión es una copia de esa carpeta; publicar es subir una copia; el link es esa copia publicada, y después de cambiar algo hay que volver a publicar, 04 [16] (media).
  2. *Tu carpeta vive en un lugar fijo y no se mueve:* ni Descargas ni el escritorio, 04 [35] (débil). Es una carpeta propia, lejos de tus fotos y documentos, y la herramienta trabaja ahí y en ningún otro lado, 02 [45] (débil); Constitución V.
  3. *La vista previa en tu compu no es el link público,* 01 [23] (débil).
  4. *Costo real, con la fecha del machete:* la app de ChatGPT en modo Codex, con el plan gratis "sujeto a despliegue"; Claude, con Pro, a US$20 por mes más impuestos en Argentina, 05 [5][8] (media, confirmadas). "Gratis" se dice solo si se probó (machete `codex-planes`, hoy `probado: false`).
  5. *Un glosario de 10 a 15 palabras con su versión en inglés:* carpeta (folder), archivo (file), proyecto (project), publicar (deploy, publish), versión, vista previa (preview), link, cuenta (account), visibilidad (visibility), configuración (settings), error. 01 [7] (media, sin verificar). Las pantallas en inglés no son un error, 01 [41] (sin verificar).
- **Actividad paso a paso** (en la compu; unas 12 a 15 respuestas del tutor y hasta 2 capturas):
  1. Entra desde la compu con su mail (FR-004) y escucha el audio.
  2. Cuenta qué tiene y qué computadora usa. El tutor recomienda una sola herramienta con el costo y la fecha del machete (`consultar_machete`, nunca de memoria):
     - *Ya usa ChatGPT, gratis o pago:* la app de ChatGPT en modo Codex. Se dice así, no "la app de Codex" (05 [9]).
     - *Tiene Claude Pro:* la app de Claude, pestaña Code.
     - *Tiene Claude gratis:* necesita Pro (US$20 más impuestos); se le ofrece Codex (spec, casos borde).
     - *No tiene nada y no quiere pagar:* Codex con el plan sin pago de ChatGPT, contado como lo que informa OpenAI, con la fecha del machete y sin la palabra "gratis" hasta que V1 y una persona del piloto lo confirmen (SC-008).
     - *Solo tiene celular, tablet o Linux:* qué necesita para seguir; su avance queda guardado (US3-5).
     - En todos los casos: una herramienta y quedarse con ella. Es una implicancia del 04, que encontró cursos organizados por herramienta, 04 [18]; no hay un estudio que lo muestre (*apuesta*).
  3. Instala siguiendo el machete, un paso por mensaje (`codex-instalar-mac`, `codex-instalar-windows`, `claude-instalar`). En Windows, la app nueva de ChatGPT desde la Microsoft Store, no la que se llama "ChatGPT Classic". Si la app permite la interfaz en español, se pone.
  4. Si se traba, sube una captura; si no sabe sacar una, sirve una foto de la pantalla hecha con el celular (*apuesta*). El tutor da el próximo paso concreto y la captura no se guarda (FR-011). Si ve una clave, avisa y no la repite (US3-3).
  5. Justo antes del primer permiso que pide la app, una línea pegada a esa acción: lo que se siente en el cuerpo es energía para dar el paso, no un aviso de que esto no es para vos. Es *apuesta*: en 03 [9] la versión suelta ("el estrés potencia") no fue significativa (d = 0,18); el efecto chico es del conjunto y del formato combinado con otro contenido, medido en estudiantes de unos 22 años y en tareas en vivo. Por eso va pegada a la acción y nunca como charla.
  6. Si su ruta publica en Netlify: crea la cuenta con Google y deja lista la visibilidad. Las cuentas creadas desde el 28/7/2026 hacen privados los proyectos nuevos, 05 [15]. Pendiente de V3: si se fija acá para toda la cuenta (lo que permite 05 [15] y recomienda 05, hueco 1) o por proyecto después de la primera publicación (lo que dice hoy el machete); y si Netlify pide tarjeta o algún pago al crear la cuenta o al publicar. Hasta entonces, el tutor no dice que Netlify no se paga.
  7. Plata: suscripción, no clave de API, con los créditos extra apagados, 02 [33] (media, sin verificar).
  8. Baja el kit, lo descomprime (en Windows, "Extraer todo") y guarda la carpeta en su lugar fijo. La abre en la app. Si la app pregunta si confía en la carpeta, el tutor le muestra con una captura qué va a ver y qué contestar (05, hueco 2; el texto exacto sale de V2).
  9. Escribe "hola, probando" y confirma en la web que la app le contestó. Ante esa frase, `AGENTS.md` le indica al tutor que solo confirme que anda y diga que la lección empieza cuando escriba "empecemos"; no se presenta, no resume la idea y no arranca nada (cambio propuesto al contrato del kit, punto 2). Así la primera sesión en la herramienta, la que miden FR-016 y SC-002, es la de la lección 4.
  10. **Cierre:** qué quedó listo y cuál es el primer paso de la próxima sesión. El tutor invita a reservar 90 minutos seguidos para la primera sesión en la herramienta: puede ser enseguida, si le queda tiempo y energía, u otro día, y la persona elige cuándo (un compromiso que elige la persona, 03 [41], media, sin verificar; el estudio era sobre limitar distracciones, así que el traslado es *apuesta*). No se guarda ni dispara ningún mail.
  - *Si se traba dos veces en el mismo paso:* el tutor ofrece otra salida (la otra herramienta, o guardar y seguir otro día) en vez de insistir.
  - *Sin tutor:* la guía escrita con el árbol del paso 2 y los pasos del machete para su herramienta y su sistema, con capturas fechadas.
- **Qué hace el tutor y qué no hace:**
  - *Hace:* un paso por vez; marca cada paso logrado como avance guardado; dice el costo con fecha y que en Argentina se suman impuestos; trata capturas y texto pegado como datos (FR-033).
  - *No hace:* pedir contraseñas ni tarjetas; guardar capturas; mandar a instalar Git, Node, plugins, skills ni conectores, ni a pegar comandos que "pide" una página web (una página simple no los necesita, 05 [7][11]; 02 [51][52]); sugerir modos de acceso total; decir "gratis" sin prueba.
- **Terminado cuando:** la app está instalada y abierta con su cuenta, la cuenta para publicar está creada (y pública, si ya se puede), el kit está en su carpeta fija, la app contestó al "hola, probando" sin arrancar la lección y la web registró `kit`.
- **Dónde se traba y cómo se previene** (el candidato más fuerte a punto de fuga, 05, hueco 5):
  - *Descubrir un costo:* se dice desde la portada (05, hueco 5).
  - *Cuenta gratis nueva sin el modelo disponible* ("subject to rollout", 05 [8]): no se puede garantizar hoy. Plan B con el costo dicho (V1).
  - *Windows pide Git:* hay que actualizar la app de Claude, 05 [7]. *Instala la app equivocada* ("ChatGPT Classic"): el machete la nombra.
  - *El zip pierde `.claude/` y `.agents/` en Windows:* V3.
  - *Netlify en inglés, con la visibilidad escondida en la configuración:* paso guiado con captura, 05 [15].
  - *Guarda la carpeta en Descargas o la mueve después:* concepto 2 y el LEEME.
  - *Llega sin energía:* por eso la primera victoria puede ir en otra sesión. Es *apuesta*: separar la instalación de la primera victoria, justo después del punto de fuga más probable, no tiene evidencia, y no hay recordatorio para quien ya bajó el kit (los mails son solo los tres previstos). Se mide en el piloto el tiempo real de cada sesión y, después, cuántos bajan el kit y no registran un primer link.
- **Qué se mide:** hoy, `kit` (con herramienta y sistema). Propuesta sin datos personales, para ver en qué paso se cae la gente (05, hueco 5): un evento `taller` con herramienta, sistema y plan (gratis o pago), y eventos `paso_taller` que la persona tilda (`app`, `cuenta_publicar`, `carpeta_abierta`). Cuántas capturas se mandan por alumno, desde `uso`, como señal de dónde se traba. La web no ve si la app se abrió: lo declara la persona.
- **Evidencia:** 01 [7][23][41]; 02 [33][41][45][51][52]; 03 [6][7][9][41][54]; 04 [16][18][35]; 05 [5][7][8][9][11][15][23], huecos 1, 2 y 5.
- **Estado:** **BORRADOR.** Ningún texto de este módulo llega a alumnos antes de anotar V1 a V3.
  - *V1:* si la cuenta gratis sirve hoy y si se puede decir "gratis".
  - *V2:* qué dice cada app al abrir la carpeta (la captura del paso 8), si Claude respeta el modo `acceptEdits` fijado por el kit, si carga el kit y si ante "hola, probando" el tutor solo confirma sin arrancar la lección.
  - *V3:* instalar en una Mac y una PC con Windows limpias; cuándo y cómo se hace pública la visibilidad de Netlify; si Netlify pide tarjeta o algún pago; si el zip conserva `.claude/` y `.agents/`; dónde conviene guardar la carpeta para que la persona la encuentre sin ayuda al otro día.

## Módulo 4: Primera victoria

- **Objetivo:** en la primera sesión con el kit, en 90 minutos o menos desde el "empecemos" de la lección 4 (la prueba "hola, probando" del módulo 3 no cuenta), ver su idea andando en la compu y después publicarla con un link que abre cualquiera sin cuenta (FR-016, SC-002). Termina con la versión "primera" guardada, un primer cambio que eligió y predijo la persona y una vuelta atrás ensayada. Publicar en la primera hora es una meta propia del curso: en el mercado lo hace el profesor con su ejemplo, y cuánto tarda un alumno no está medido (05, afirmación 1).
- **Audio del autor:**
  - *Cuándo:* después del saludo del tutor, que le indica dónde escucharlo (FR-005; US1-8; contrato del kit, punto 10). Ocupa 3 de los 75 minutos.
  - *Qué tipo de historia cuenta:* una traba real, no un logro: la primera vez que vio andar algo que había imaginado, contada desde lo que le faltaba (qué tan fea o incompleta era esa primera versión) y qué sintió igual al verla andar. Lo técnico, como mucho, en una frase.
  - *Idea eje:* fea, pero existe.
  - *Cierra con:* ¿qué es lo primero que querés ver andando de tu idea?
  - *No dice:* métricas, nombres de herramientas ni pasos (FR-028).
- **Conceptos:**
  - *Ver andar no es publicar:* primero en la compu, después el link (05, hueco 1; 01 [23]).
  - *Publicar es sacar una foto:* cada cambio hay que volver a publicarlo, 04 [16]. Se publica poco: en Netlify cada publicación y las visitas gastan créditos del plan, 05 [13]. Cuántas publicaciones entran sin pagar ("unas 20 por mes") se dice recién cuando V3 confirme que el plan no pide tarjeta ni pago y el machete lo tenga con `probado: true`.
  - *Una versión guardada es una copia en `versiones/`* que ves en el Finder o el Explorador. Es tu red desde hoy (05, hueco 2 y afirmación 3).
  - *Predecir es decir en una línea qué vas a ver, antes de verlo.* No es un examen.
- **Actividad paso a paso** (presupuesto de 75 minutos y 15 de margen hasta el techo de 90; unos 10 a 12 pedidos, estimación que confirma V1; los minutos cuentan desde el "empecemos"):
  1. *Minutos 0 a 3.* Abre la carpeta y escribe "empecemos". Acá arranca el reloj de SC-002. El tutor se presenta, resume la idea en dos frases, indica dónde está el audio y propone un paso (US1-1).
  2. *Minutos 3 a 6.* Escucha el audio (opcional).
  3. *Minutos 6 a 12.* Decisiones antes del pedido, todas de la persona: confirma el molde, el título, la frase y el único elemento que responde, tomados de `mi-idea.md`. Si faltan los textos exactos, los decide ahora (05, contradicción 2).
  4. *Minutos 12 a 25.* El tutor dice en una o dos líneas qué va a hacer y arma la versión mínima en un solo pedido, llenando el molde con sus palabras en `sitio/index.html`: un solo archivo HTML, sin herramientas de compilación ni imágenes de afuera (05, hueco 1). El pedido completo vale acá porque las decisiones ya son de la persona (05, contradicción 2).
  5. *Minutos 25 a 30. Momento A:* la ve andar en la vista previa de la app o con doble clic en `sitio/index.html` (machete `ver-claude` y `ver-codex`; 05 [12]). Cuenta qué ve antes de hablar del porqué: cerca de 1 de cada 5 registra mal lo que pasó, 05 [38].
  6. *Minutos 30 a 33.* Guarda por su cuenta la versión con el nombre "primera" (`/guardar-version` en Claude, `$guardar-version` en Codex; el nombre es un cambio propuesto al contrato del kit) y abre `versiones/` en el Finder o el Explorador para ver la copia.
  7. *Minutos 33 a 55. Momento B:* publica con la skill `publicar` y el machete. En Netlify arrastra **solo la carpeta `sitio`**, nunca la carpeta entera del kit, que dejaría públicos `mi-idea.md`, `bitacora.md` y `cuaderno.md`; la skill y el LEEME lo muestran con una captura. Hace pública la visibilidad si todavía no lo estaba. Abre el link en el celular o en una ventana privada, sin sesión: su idea existe y tiene dirección. El link queda en la bitácora.
  8. *Minutos 55 a 65. Momento C, hacerla suya:* un primer cambio chico que decide la persona. Antes, la frase de encuadre ("si no pasa lo que esperabas, encontraste algo") y una línea en el cuaderno sobre qué espera ver ("no sé" vale). Lo pide, lo mira, cuenta qué vio y el tutor devuelve "anotaste X, pasó Y". No se vuelve a publicar si el cambio no lo vale.
  9. *Minutos 65 a 70.* Ensaya volver: `volver-version` a "primera" (la skill guarda antes la versión actual), ve que volvió y regresa al cambio. Ensayar la red cuando no hay nada en juego es una decisión de diseño (05, afirmación 3): no hay estudios sobre cuándo enseñarlo.
  10. *Minutos 70 a 75. Cierre:* el tutor le devuelve qué eligió, qué predijo y qué comprobó (02 [38]), propone para la próxima sesión una meta un poco más difícil, 03 [8] (sin verificar), y deja la bitácora al día. Propuesta: que registre ya el link en la web (ver Medición y Decisiones), con las dos opciones de mostrar desmarcadas.
  - *Minutos 75 a 90:* margen. No se planifica nada ahí.
  - **Cortes:** si llega al minuto 55 sin publicar, publicar pasa primero, y el cambio y el ensayo de volver quedan para el comienzo de la próxima sesión. Si publicar falla dos veces, no se insiste: se anota en la bitácora dónde se trabó y se sigue en la próxima sesión, con la página ya vista andando (05, hueco 1). Si algo se rompe, el tutor vuelve a la última versión guardada antes de cerrar: nadie se va con su idea rota (05, hueco 4).
  - **Bitácora al día en cada paso:** el tutor actualiza `bitacora.md` después de cada paso logrado (vista, "primera" guardada, link, cambio, ensayo), no solo al cerrar, para que un corte del cupo no borre dónde quedó (cambio propuesto al contrato del kit, punto 8).
- **Qué hace el tutor y qué no hace:**
  - *Hace:* explica en una o dos líneas antes de actuar; muestra la página en vez de decir "listo", 02 [19]; ante "hacelo vos todo", hace un paso, explica y devuelve la próxima decisión (turno 3); usa el molde probado.
  - *No hace:* agregar lo que nadie pidió ni embellecer antes de publicar, 02 [15]; usar frameworks o instalar nada (la página en blanco porque la IA generó React es una traba conocida, 01 [24], débil); pedir o aceptar contraseñas ni claves, porque la persona entra con Google en su navegador (turno 9, FR-019); crear cuentas por la persona; publicar sin que la haya visto andar; elogiar en genérico ("¡perfecto!"), porque la confianza que no se apoya en lo comprobado se infla sola, 03 [22]; prometer que el link dura para siempre.
- **Terminado cuando:** hay un link que abre sin sesión en otro dispositivo o en una ventana privada; `versiones/` tiene "primera"; el cuaderno tiene una predicción con lo que se vio; la persona hizo un cambio propio y volvió atrás una vez; y la bitácora tiene el link. En el piloto, el link tiene que llegar dentro de los 90 minutos contados desde el "empecemos" (SC-002); el cambio y el ensayo pueden cerrarse al empezar la sesión siguiente.
- **Dónde se traba y cómo se previene:**
  - *El primer error* (01 [1]): la versión mínima es chica y va en un molde probado, volver se ensaya en el paso 9 y la lección trae un "cuando se rompe" corto, escrito por el curso, para los tropiezos probables (página en blanco, no se publica, se desarma en el celular, el link no abre), 01 [20] (fuerte, sin verificar; errores de compilación en C) y 01 [24].
  - *Publicar se traba* (05 [1][15]): como ya vio su idea andando, la victoria no depende del link (05, hueco 1).
  - *Arrastra la carpeta equivocada:* riesgo de privacidad (paso 7). Si arrastra algo que no es `sitio`, además crea otro sitio con otro link.
  - *El link pide iniciar sesión:* la visibilidad de Netlify quedó privada, 05 [15], o el link de Claude pide cuenta, 05 [1][2]. Se nota al abrirlo en la ventana privada.
  - *Se corta el cupo gratis:* cuando se agota el límite, la app deja de contestar y el tutor ya no puede anotar ni explicar nada. Por eso la bitácora se actualiza en cada paso logrado (no solo al cerrar), y `LEEME.txt`, `curso/machete.md` y el principio de cada lección traen un texto fijo, "Si la app deja de contestar por el límite", que la persona lee sin la herramienta: dónde ver cuándo se renueva y las opciones con su costo según el machete (esperar o pasar a un plan pago, con fecha) (spec, casos borde; 05 [70]; V1).
  - *No hay vista previa en el plan gratis:* doble clic (05 [12]).
  - *La victoria la hizo toda la IA* (03 [22]): los pasos 3, 8 y 10 la vuelven propia.
  - *"Está fea":* es la versión 1, y lo terminado vale más que lo dejado a medias (05 [62]).
- **Qué se mide:** la herramienta no le manda nada a la web (Constitución III). Propuesta: registrar el link al cierre de esta lección (evento `link` con `etapa=primera`), porque la métrica para decidir es "terminó su idea y publicó" (05, hueco 5); ver la tensión con `api.md` en Decisiones. En el piloto: minutos desde el "empecemos" hasta el link, con cronómetro (SC-002, ver Medición), en qué paso se traba cada persona, si el link abre sin cuenta y si hizo por su cuenta el cambio y la vuelta atrás.
- **Evidencia:** 01 [1][20][23][24]; 02 [15][19][38]; 03 [8][22]; 04 [16]; 05 [1][2][12][13][15][38][62][70], huecos 1 a 5, contradicción 2 y afirmaciones 1 y 3.
- **Estado:** **BORRADOR.**
  - *V1:* si Codex gratis termina la lección sin tocar el límite, cuántos pedidos entran, qué ve la persona cuando se corta y si el plan gratis tiene skills y vista previa. Si no hay skills, guardar, volver y publicar van como pasos escritos iguales para las dos herramientas, en la misma lección o en el machete filtrado por herramienta, para mantener una sola fuente (FR-015); si no hay vista previa, doble clic.
  - *V2:* turnos 1, 3, 6, 9 y 10, más los chequeos (a), (c), (i), (k) y (l) de la tabla de pendientes.
  - *V3:* la ruta de cada herramienta; que la persona arrastre solo `sitio`; si el link de Netlify abre sin cuenta una vez público y si el de Claude la pide; si Netlify pide tarjeta o algún pago.
  - *Cambio propuesto al contrato del kit:* sumar los cuatro moldes como archivos HTML probados en las dos herramientas (`curso/moldes/`), para que la versión mínima salga igual en las dos y con menos pedidos (*apuesta* apoyada en 05 [64]).

## Módulo 5: Construir

- **Objetivo:** llevar la página hacia lo que su idea pedía con el ciclo pedir, predecir, mirar y ajustar, un cambio visible por vez, con versiones con nombre y el cuaderno como registro (FR-017). En el camino aprende a pedir con los detalles que la máquina no adivina y a mirar más allá del caso en que todo anda.
- **Audio del autor:**
  - *Cuándo:* al empezar la lección 5.
  - *Qué tipo de historia cuenta:* una traba real, no un logro: una vez que una herramienta le dijo que algo estaba hecho y, al mirar, no lo estaba; o el cansancio de dirigir a la IA durante una jornada larga.
  - *Idea eje:* la herramienta dice "listo"; vos mirás.
  - *Cierra con:* antes del próximo cambio, anotá qué esperás ver.
  - *No dice:* nombres de clientes ni incidentes de terceros; métricas.
- **Conceptos:**
  1. *Un pedido en cuatro partes llanas:* qué quiero, dónde, qué no tocar y cómo me doy cuenta de que salió, 02 [20] (media, corregida).
  2. *Un cambio visible por pedido,* 01 [14][45]; 02 [13] (débil).
  3. *Si sale distinto,* la primera pregunta es qué detalle faltó decir; reformular sin mirar no alcanza, 01 [5].
  4. *Predecir el comportamiento, no solo el aspecto:* qué pasa si toco, si recargo o si lo abro en el celular, 02 [43] (media, sin verificar).
  5. *Mirar mejor:* en el celular, con un texto largo, con algo vacío, recargando, abierto por otra persona, 02 [39]; 01 [16].
  6. *"Casi bien" es lo normal,* también para los profesionales, 02 [11] (fuerte como dato de encuesta a desarrolladores, sin verificar).
  7. *Dirigir cansa:* sesiones cortas que cierran en algo guardado, 02 [8] (débil).
- **Actividad paso a paso** (una o dos sesiones de hasta 40 minutos, cada una en una conversación nueva; de 2 a 4 cambios):
  1. Dice "sigamos". El tutor lee la bitácora, retoma donde quedó y trae la sorpresa de la sesión anterior, si hubo: "¿sigue siendo así?". Sin repaso, la idea vieja vuelve, 05 [44].
  2. Solo en la primera sesión, una vez: un ejemplo resuelto sobre su propia página (Constitución I). El tutor propone un cambio chico y muestra el ciclo entero en voz alta: el pedido en cuatro partes, la predicción, lo que salió y, si hizo falta, el ajuste, 03 [13][14] (fuerte y media, sin verificar). Después, la persona hace el siguiente.
  3. Elige el próximo cambio, de su versión o de "qué sigue" si entra en una página, y arma el pedido. El tutor ayuda con la forma; las palabras son de la persona.
  4. La invitación a predecir, en cada pedido (FR-017), en media línea. En los momentos clave (la primera vez que hace ese tipo de cambio, o si algo se mueve o responde a un clic) el tutor la sostiene: "¿qué esperás ver? Anotalo en una línea en `cuaderno.md`". En los cambios obvios (un color, un texto) la invitación ya viene con la salida: "¿lo anotás o lo salteamos? Es un cambio chico". El tutor no dice que no hace falta ni insiste.
  5. El tutor devuelve en castellano qué entendió del pedido, 01 [9] (sin verificar), guarda una versión si el cambio es grande y lo hace.
  6. La persona abre la página y cuenta qué cambió de verdad. El tutor chequea la observación (recargar, comparar con la versión anterior, 05 [38]) y devuelve la evidencia sin puntaje: "anotaste X, pasó Y, ahora sabés Z". Si hubo sorpresa, queda marcada en el cuaderno.
  7. Si funcionó, guarda una versión con un nombre que elige la persona. Publica solo cuando hay un cambio que lo vale.
  8. Una vez por sesión, una prueba de "qué pasa si" con la lista del concepto 5.
  9. Al cerrar: una línea sobre qué esperaba y qué le sorprendió, y la bitácora al día (que además se actualiza después de cada cambio logrado).
- **Qué hace el tutor y qué no hace:**
  - *Hace:* frena los pedidos gigantes y propone partirlos, 01 [14][45]; guarda una versión antes de cada cambio grande; acepta "no sé qué esperar"; ofrece "¿por qué creés que pasó?" solo después de una sorpresa, sin imponerlo, 01 [11]; si hay fotos propias, pide que la persona las copie dentro de `sitio/`, las incluye sin instalar nada (y si no puede achicarlas así, explica el límite) y antes avisa que lo que está en la página lo ve cualquiera, sobre todo si aparecen caras de otras personas (05, hueco 1; V2); si reaparecen el login o los pagos, los lleva a "qué sigue". *Apuesta:* si la persona predice bien y pide claro, acorta sus explicaciones y acepta pasos un poco más grandes (03 [12] deja pendiente cómo retirar la guía).
  - *No hace:* insistir con la predicción en los cambios obvios ni volverla obligatoria (05 [39][45]); decir "acertaste" o "fallaste"; cambiar varias cosas a la vez; mostrar código salvo que se lo pidan; decir "listo" sin mostrar; seguir en la misma conversación después de dos intentos fallidos (la regla del módulo 6 vale desde acá).
- **Terminado cuando:** hizo al menos dos cambios con el ciclo, al menos uno con la predicción anotada y comparada en el cuaderno; hay una versión con nombre por cada paso que funcionó; pasó una prueba de "qué pasa si"; y la página hace lo que `mi-idea.md` dice para la versión elegida. El módulo 6 se puede hacer en cualquier momento, cuando algo se rompe: en ese caso el tutor primero resuelve (abrir `versiones`, volver) y ofrece el audio del 6 al cierre de esa sesión, no en pleno susto (principio 10).
- **Dónde se traba y cómo se previene:**
  - *Espiral de pedidos que no avanzan,* 01 [4][17]: la regla de los dos intentos se adelanta.
  - *Juntar todo en un pedido para ahorrar cupo,* 01 [3]; 05 [70]: el tutor da razones concretas, no sermones, 01 [14].
  - *La conversación larga se degrada,* 05 [24][25]: una conversación por sesión.
  - *Fallas silenciosas* (un botón que se ve pero no hace nada), 02 [43]; 04 [34]: la prueba de "qué pasa si".
  - *El último tramo es el que más cuesta,* 01 [32] (sin verificar): se anticipa ("es la parte que más cuesta; no sos vos").
  - *El cuaderno se siente como examen o traba por perfeccionismo,* 05 [45][46]; 03 [51]: lenguaje de curiosidad, sin puntaje y con salteo explícito.
  - *Cansancio:* se corta después de algo guardado (*apuesta*).
- **Qué se mide:** nada en la web (datos mínimos). En el piloto: cuántas predicciones se anotan, cuántas sorpresas aparecen, si alguien saltea todas y dónde se abandona (05, hueco 3). El cuaderno queda en la compu del alumno, y en el piloto se mira solo con su permiso.
- **Evidencia:** 01 [3][4][5][9][11][14][16][17][32][45]; 02 [8][11][13][20][39][43]; 03 [12][13][14][51]; 04 [34]; 05 [24][25][38][39][44][45][46][48][50][70], huecos 1 y 3.
- **Estado:** listo en lo pedagógico, con la lectura compatible con FR-017 (invitación de media línea en cada pedido, con salteo ofrecido en los obvios).
  - *V2:* que el tutor invite en cada pedido, sostenga la invitación en los momentos clave y ofrezca saltearla en los obvios sin decir que no hace falta (turno 7 y chequeo (a)); que sostenga un cambio por vez; que maneje las fotos sin instalar nada (chequeo (o)).
  - *V1:* cuánto rinde el plan gratis en una sesión de construcción y qué pasa si el límite corta a mitad de un cambio.
  - *Si el autor enmienda FR-017* a "momentos clave" (Decisiones, tensión 1), la invitación en los obvios desaparece; el resto del módulo no cambia.

## Módulo 6: Cuando se rompe

- **Objetivo:** que la persona pueda salir por su cuenta de un problema (FR-018): contarlo con "hice, esperaba, vi", leer el error como información, cortar a los dos intentos, volver a una versión que andaba y seguir en una conversación nueva con lo aprendido. Y que no le crea a la herramienta si dice que se perdió todo.
- **Audio del autor:**
  - *Cuándo:* al empezar la lección 6, fuera del momento de hacer. Si el módulo arranca por una rotura en medio del 5, el tutor primero resuelve (abrir `versiones`, volver) y ofrece el audio al cierre de esa sesión, no en pleno susto (principio 10). Si la persona se frustra en otro momento, el tutor puede recordarle dónde está (*apuesta*).
  - *Qué tipo de historia cuenta:* una traba real, no un logro: algo que se le rompió de verdad, qué perdió y qué lo salvó (o qué lo hubiera salvado), y qué cambió después en su forma de trabajar.
  - *Idea eje:* guardá copias de lo que te importa, antes de necesitarlas.
  - *Cierra con:* abrí tu carpeta `versiones` y mirá lo que ya tenés guardado.
  - *No dice:* nombres de apps y servicios, porque se vencen (FR-028); nada en tono de exhibición: se cuenta como confesión que le sirve al otro.
- **Conceptos:**
  1. *Un error es información* sobre lo que faltó decir o lo que cambió, en tono neutro y sin celebrarlo. Es la adaptación del curso a partir de 03 [11][51] (media); el encuadre que probó 05 [47] (fuerte) es otro: exploración más el aviso de que los errores son esperables y útiles.
  2. *"Hice, esperaba, vi",* en vez de pegar el error y pedir que lo arreglen, 01 [4][16]. Delegar la depuración se asoció con los peores puntajes, 02 [35] (media, corregida; no causal).
  3. *La regla de los dos intentos:* si el segundo intento de arreglo no funcionó, se frena, se vuelve a la última versión que andaba y se abre una conversación nueva. En Claude sale de la guía oficial, 05 [30]; 01 [18]. En Codex es una decisión del curso, 05 [23]; 05, contradicción 10.
  4. *Tus versiones son archivos que ves en tu carpeta:* si la herramienta te dice que se perdió todo, abrí `versiones` (05, hueco 2; 05 [36]).
  5. *Tu sitio es una carpeta que podés copiar y mudar* (spec, casos borde). Empezar de nuevo achicando es una estrategia legítima, 01 [16].
- **Actividad paso a paso** (una sesión de unos 35 minutos):
  1. Escucha el audio (o, si llegó por una rotura, al cierre).
  2. Si todavía no se rompió nada, puede practicar sin nada en juego. Es opcional y lo decide y lo hace la persona, porque alentar el error bajó la autoeficacia de personas muy responsables, 03 [51]. Propuesta del mapa (*apuesta*, a decidir por el autor, Decisiones): la práctica de romper se hace sobre una copia de su página (`practica/`, que el tutor arma copiando `sitio/` y que nunca se publica), porque PRIMM arranca con material que no es el propio para que el error pese menos, 03 [19] (sin verificar). Ahí pide un cambio que desarme algo a propósito, mira la página rota y la cuenta. La vuelta atrás se practica aparte sobre `sitio/`, sin romper nada: `volver-version` a una versión anterior, verla y regresar a la última.
  3. Ante un error real, o el de la práctica: el tutor lo traduce en una frase; la persona lo cuenta con "hice, esperaba, vi" y, si quiere, dice qué cree que pasó ("no sé" vale). Es una aplicación del curso, no algo que muestre una fuente. Antes de probar un arreglo, la invitación a anotar qué espera ver (FR-017; acá es siempre momento clave).
  4. Primer intento; si no anduvo, un segundo con un pedido mejor. Cada intento fallido suma una marca en la columna "Intentos" del cuaderno, no en la memoria del agente (05, hueco 2; 05 [27]).
  5. Con dos marcas: vuelve por su cuenta con `volver-version` a la última que andaba, anota qué aprendió y abre una conversación nueva con un pedido que el tutor le redacta para que lo pegue.
  6. Después del arreglo, cuenta con sus palabras qué se cambió en la página (principio 7).
  7. Abre `versiones/` desde el Finder o el Explorador, y una versión vieja en el navegador, sin la herramienta.
  8. Copia por su cuenta la carpeta entera del proyecto a otro lugar: un pendrive o su nube. Si un día pierde la carpeta, volver a bajar el kit le devuelve la idea, pero no la página que construyó.
  9. El tutor trae de vuelta el "para quién y por qué" del módulo 2, 05 [63] (media, confirmada).
- **Qué hace el tutor y qué no hace:**
  - *Hace:* traduce el error antes de arreglarlo; explica cada comando antes de correrlo; lleva la cuenta en el cuaderno y frena a los dos intentos; antes de decir que algo no se puede recuperar, lista las versiones y abre la última, 01 [22]; 05 [36]; usa las explicaciones escritas por el curso para los tropiezos probables, 01 [20]; actualiza la bitácora después de cada paso logrado, así un corte del cupo no borra dónde quedó (el texto fijo "Si la app deja de contestar por el límite" está en `LEEME.txt` y al principio de la lección).
  - *No hace:* parchar en loop ni pegar el error una y otra vez, 02 [9][39]; intentar una tercera vez en la misma conversación; culpar a la persona; borrar nada de `versiones/`; salir de la carpeta (turno 5); usar git (research §13); hacer por la persona la copia del paso 8; romper algo sin avisar.
- **Terminado cuando:** volvió por su cuenta al menos una vez a una versión guardada y la vio andar (en un error real o en la práctica de volver); contó un error con "hice, esperaba, vi" en el cuaderno; contó con sus palabras qué cambió después de un arreglo; y tiene una copia de su carpeta fuera de la compu.
- **Dónde se traba y cómo se previene:**
  - *Pánico con "se rompió todo":* el primer gesto es abrir `versiones`.
  - *El bucle de volver a pedir lo mismo,* 04 [29]: la columna Intentos.
  - *La herramienta afirma que no hay vuelta atrás,* 05 [36] (débil): la regla del kit.
  - *El agente borra `versiones/`,* algo que "Accept edits" aprueba sin preguntar, 05 [32]: regla deny en Claude que niega borrar o sobrescribir versiones existentes, no crear nuevas (V2); en Codex, la regla en `AGENTS.md` más la copia del paso 8.
  - *La práctica se vive como una trampa:* es opcional, sobre una copia y la hace la persona, nunca el tutor a escondidas.
  - *La frustración cierra la sesión:* el tutor propone volver o achicar antes de que pase, 01 [1][18].
- **Qué se mide:** nada en la web. En el piloto: si la persona se recupera por su cuenta de un problema, 04 [32], cuánto tardó y cuántas veces se activó la regla de los dos intentos (según la bitácora).
- **Evidencia:** 01 [1][4][16][18][20][22]; 02 [9][35][39]; 03 [11][19][51]; 04 [29][32]; 05 [23][27][30][32][36][47][63], hueco 2 y contradicción 10.
- **Estado:** listo en lo pedagógico. La práctica sobre una copia espera la decisión del autor.
  - *V2:* que `volver-version` ande igual en las dos apps; que la regla deny proteja `versiones/` sin bloquear `guardar-version` (chequeos (c) y (d) en la misma corrida); que el tutor frene a los dos intentos, redacte el pedido nuevo y no dé nada por perdido; si `/rewind` anda en la app de Claude (como complemento, no como red).
  - *V1:* si hay skills en Codex gratis. Si no hay, guardar y volver van como pasos escritos iguales para las dos herramientas (ver módulo 4).

## Módulo 7: Terminar y mostrar

- **Objetivo:** la versión final publicada en el mismo link, revisada con una lista corta, explicada por la persona, con un último cambio hecho sin ayuda y registrada en la web con sus permisos (FR-022, FR-023). Se lleva "qué sigue" al día y una copia de su carpeta.
- **Audio del autor:**
  - *Cuándo:* al empezar la lección 7, antes de la publicación final.
  - *Qué tipo de historia cuenta:* una traba real, no un logro: la vergüenza de mostrar algo imperfecto, o algo que hizo y casi nadie vio, contado sin cifras y sin tono de negocio.
  - *Idea eje:* mostrar también es parte de hacer.
  - *Cierra con:* ¿a quién le vas a mandar el link primero?
  - *No dice:* éxito económico ni consejos de venta. El antecedente del mercado trata el miedo recién al final y en esa clave, 04 [3]; acá no.
- **Conceptos:**
  - *Lo que está en la página lo ve cualquiera:* ni claves, ni contraseñas, ni datos de otras personas, ni servicios pagos, 02 [1][47]; 05 [61]; 04 [36].
  - *Qué es público y qué no:* el link sí; el cuaderno, la bitácora y la idea no, mientras publiques solo `sitio`, 03 [3].
  - *Actualizar es publicar en el mismo sitio,* para que el link no cambie (machete). Si circula mucho, la página gratis se puede pausar, 05 [13].
  - *Si alguien dice "eso es vibe coding" con desprecio,* vos sabés qué parte tomaste, 02 [12] (débil).
  - *"Qué sigue"* y por qué el curso no incluye login ni pagos, 04 [36][38].
- **Actividad paso a paso** (unos 45 minutos, con techo de 55):
  1. Escucha el audio.
  2. El tutor trae dos o tres sorpresas del cuaderno: "¿siguen valiendo?", 05 [44].
  3. **Un cambio sin ayuda:** la persona elige el cambio, arma el pedido en cuatro partes, predice, lo pide y lo comprueba; si se rompe, vuelve atrás por su cuenta. El tutor pasa al modo "solo ejecuto y explico comandos": no sugiere ni corrige, salvo riesgo o pedido. Volver atrás por su cuenta también cuenta como éxito (*apuesta*: lo aprendido se mide con una tarea sin tutor, 03 [22][23]).
  4. Recorre con el tutor la lista antes de compartir: claves, datos de otras personas, servicios pagos, imágenes incluidas en el archivo, cómo se ve en el celular y si andan los links externos.
  5. Cuenta con sus palabras qué hace su página y qué decidió, 01 [12]. Si quiere, esa frase es el texto con el que la comparte.
  6. Guarda la versión final, publica en el mismo sitio (en Netlify, arrastrando otra vez solo `sitio`, en la sección de deploys de ese sitio) y la abre en otro dispositivo sin sesión.
  7. Antes de mandarla, una línea pegada a ese gesto: lo que siente es energía para el paso, no un aviso. Es *apuesta*, como en el módulo 3: en 03 [9] la versión suelta no fue significativa y el efecto chico es del formato combinado, medido en estudiantes jóvenes y en tareas en vivo; en tareas públicas tendió a ser algo mayor, sin diferencia significativa.
  8. El tutor menciona una sola vez la línea "Hecho en [curso]" y la agrega solo si la persona la pide (FR-022; US4-3).
  9. Copia otra vez la carpeta del proyecto a su pendrive o su nube.
  10. Registra el link en la web, o completa el registro si lo hizo en el módulo 4, y elige, con las dos casillas desmarcadas, si va a la galería y si el autor lo puede usar como contenido (FR-023). Actualiza "qué sigue" en `mi-idea.md` (FR-009).
  11. **Cierre sobrio:** el tutor le muestra con hechos lo que decidió la persona en todo el curso (el molde, los textos, qué quedó afuera, qué arregló, a qué versión volvió), a partir del cuaderno y la bitácora: "decidiste X, anotaste Y, volviste atrás Z" (implicancia de 01 sobre 01 [28]; 02 [38]). Nada de "ya sos programador" en ninguna forma: la confianza que no se apoya en lo comprobado se infla, 03 [22].
- **Qué hace el tutor y qué no hace:**
  - *Hace:* la lista de seguridad; explica qué es público; guarda una versión antes de la final; anota el link final en la bitácora e indica cómo registrarlo; en el paso 3 se corre del medio.
  - *No hace:* agregar "Hecho en [curso]" sin pedido; tocar las casillas de consentimiento; prometer que alguien va a mirar la página o contestar; empujar a publicar en redes; prometer que el link dura para siempre (no está documentado qué pasa con el link de Claude si la persona deja de pagar, 05 [2][6], y el de Netlify depende de los créditos).
- **Terminado cuando:** el link final abre sin cuenta en otro dispositivo; la persona pasó la lista, explicó qué hace su página e intentó el cambio sin ayuda (cuenta si salió o si volvió atrás por su cuenta); tiene una copia de su carpeta; y registró el link (evento `link`).
- **Dónde se traba y cómo se previene:**
  - *Vergüenza de mostrar algo "de juguete",* 02 [18] (débil): el audio, el paso 7 y mostrar cuando quiera.
  - *Privacidad,* 03 [3]: la lista y el "qué es público".
  - *Arrastra la carpeta fuera del sitio* y crea otro link: el machete dice dónde arrastrar.
  - *El link no abre para otros o se agotaron los créditos,* 05 [1][13][15]: se comprueba en otro dispositivo antes de mandarlo.
  - *La sesión de la web venció* (dura 30 días): entra con el código de su mail.
  - *No vuelve a la web a registrar:* el kit se lo recuerda; si ya registró en el módulo 4, el dato principal ya está.
- **Qué se mide:** `link` (con `etapa=final`, si se adopta la propuesta del módulo 4), los dos consentimientos, las inscripciones que llegan con `fuente=hecho-en` y el mail `contame`. Solo en el piloto: "del 1 al 10, ¿qué tan capaz te sentís de cambiar tu página sin ayuda?", al empezar el módulo 1 y al terminar el 7, adaptado de 03 [4] (sin verificar), y si el cambio sin ayuda salió.
- **Evidencia:** 01 [12][28]; 02 [1][12][18][38][47]; 03 [3][4][9][22][23]; 04 [3][36][38]; 05 [1][2][6][13][15][44][61].
- **Estado:** **BORRADOR.**
  - *V3:* publicar la versión final en el mismo link, con Netlify y con Claude, y si el link de Claude abre sin cuenta; si Netlify pidió tarjeta o algún pago. Si no abre, los alumnos de Claude también publican en Netlify y la página de Claude queda como vista previa privada (05, afirmación 12).
  - *V2:* que el tutor respete el modo "solo ejecuto" (chequeo (g)) y no agregue la línea sin pedido.
  - *V1:* si el cupo gratis alcanza para esta sesión y qué ve la persona si se corta (el texto fijo de `LEEME.txt`).
  - *Sin prueba prevista:* qué pasa con el link de Claude si la persona deja de pagar, 05 [2][6].

## Transversales

### Miedo: repartido y pegado a la acción

| Momento | Miedo probable | Gesto al que se pega | Referencia |
|---|---|---|---|
| Portada y módulo 1 | Gastar plata sin querer | El costo de cada camino, con fecha, desde antes de inscribirse; en el módulo 1, sin hablar de planes gratis | 05, hueco 5 (recomendación, sin datos de este público) |
| Módulo 1 | "Ya estoy grande para esto" | Nombrarlo sin negarlo: lo que pesa es la falta de experiencia, y eso lo da el curso | 03 [1][2] |
| Módulo 1 | "No sé para qué me sirve" | Contar qué le gustaría que exista antes de ver ejemplos | 01 [30] |
| Módulo 1 | Qué ve la IA y qué queda público | Una respuesta corta y honesta | 01 [30], 03 [3] |
| Módulo 2 | "Mi idea es tonta" o "es demasiado grande" | Escribir por qué le importa; lo grande va a "qué sigue" | 05 [63] (secundaria; a escala, chico e inconsistente, 03 [31]: *apuesta*), hueco 4 |
| Módulo 3 | Romper la compu; todo en inglés | Carpeta propia en un lugar fijo, captura cuando se traba, glosario, "en inglés no es un error" | 02 [45], 01 [7][41] |
| Módulo 4 | "Me va a salir mal" | Una versión mínima chica, en un molde probado; verla andar antes de publicar; ensayar volver; "algo se va a romper y está previsto" | 01 [1], 05 huecos 1 y 4 |
| Módulo 5 | "No entiendo lo que hace" o "me están tomando examen" | Media línea de invitación a anotar lo que espera ver, con salteo ofrecido en lo obvio; el tutor devuelve lo que entendió, sin puntaje | 05 hueco 3, 01 [9] |
| Módulo 6 | "Se rompió todo, perdí todo" | Abrir `versiones`; la columna Intentos; la copia fuera de la compu | 05 hueco 2 |
| Módulo 7 | Vergüenza de mostrar; qué queda público | La lista antes de compartir; una línea antes de mandar el link; mostrar cuando quiera | 02 [18], 03 [3][9] |

- Se nombra en una frase cuando aparece y enseguida se pasa a la acción. Nada de charlas de mentalidad, 03 [9][31]; 04 [1].
- El tutor contesta con hechos del curso, no con aliento. Nada de "te felicito por animarte" en genérico.
- El miedo a fallar se asocia con delegar antes y más, 01 [28] (media, verificada; correlacional): que las decisiones vayan antes de cada pedido también es una respuesta al miedo.
- De los miedos que nombra en el módulo 1, el resumen del módulo guarda solo la categoría genérica ("costo", "romper la compu"), sin frases textuales, sin edad y sin datos de salud (spec, Retención), y el tutor de la web la retoma en el 2 y el 3. Si además viajan al kit dentro de `mi-idea.md`, también como categoría, lo decide el autor (*apuesta*).
- Encuadre del error: "si no pasó lo que esperabas, encontraste algo". Nunca "equivocarse es genial". Es una adaptación neutra a partir de 03 [11][51] (media); el encuadre que probó 05 [47] (fuerte) combina exploración con el aviso de que los errores son esperables y útiles.
- Un entorno calmo y predecible probablemente le sirva a quien es más sensible, pero no conviene presentar el curso como "diseñado para personas sensibles", 03 [50] (débil).

### Predicción: la dosis

- **Cuándo se sostiene** (de 6 a 10 veces en todo el curso, *apuesta*): el primer cambio propio del módulo 4; la primera vez que hace un tipo de cambio nuevo; cuando algo se mueve o responde a un clic; antes de probar un arreglo en el módulo 6; el cambio sin ayuda del módulo 7.
- **En los cambios obvios** (un color, un texto): en las lecciones 5 y 6 la invitación igual aparece, porque FR-017 la pide antes de cada pedido, pero en media línea y con la salida ofrecida ("¿lo anotás o lo salteamos?"). El tutor no dice que no hace falta ni insiste. En las lecciones 4 y 7, fuera de los momentos listados, no se invita.
- **Cómo:**
  - una línea sobre lo que se ve o lo que hace la página, nunca sobre el código, porque ahí sería adivinar, 05 [41];
  - siempre antes de ver, nunca reconstruida después, 05 [39];
  - con la frase de encuadre antes y con "no sé qué esperar" como respuesta válida;
  - el tutor chequea lo observado antes del porqué, 05 [38], y devuelve "anotaste X, pasó Y, ahora sabés Z", sin puntaje;
  - las sorpresas grandes vuelven al empezar la sesión siguiente y en el módulo 7, 05 [44].
- **Qué no se hace:** preguntar "¿qué tan seguro estás?" queda afuera por ahora, como opción a probar, porque no hay evidencia sobre su costo en personas perfeccionistas (05, hueco 3).
- **El cuaderno** (`cuaderno.md`) tiene estas columnas: `Fecha | Qué pedí | Qué espero ver | Qué vi | ¿Me sorprendió? | Intentos`. No lleva una columna "¿Coincidió?", que suena a examen. La columna Intentos sostiene la regla de los dos intentos en un archivo visible, 05 [27].
- **Se presenta como** una práctica fundamentada y a prueba, no como un método probado (05, hueco 3). Referencias: 05 [37][38][39][41][44][45][48][50] y contradicción 1.
- **Propuesta de enmienda de FR-017** a "momentos clave": ver Decisiones, tensión 1.

### Explicar con palabras propias

- **Dos momentos fijos:** después de un arreglo (módulo 6) y antes de la publicación final (módulo 7).
- **Forma:** "contame qué cambió en tu página", siempre sobre la página y nunca sobre el código. Si lo que cuenta no coincide con lo que pasó, el tutor muestra la diferencia en la página, sin corregir como en un examen. "No sé" vale: el tutor explica y le pide que lo diga a su manera.
- **Por qué no más seguido:** la compuerta costó una mediana de 14,2 minutos de fricción, 05 [28], y en otro estudio el tutor con andamiaje se percibió menos útil, 05 [29] (débil: 17 personas, tutor de estrategia). Nunca funciona como compuerta que bloquea. Es *apuesta* con respaldo indirecto (principio 7; 05, afirmación 7).
- No cuentan como "explicar" dos gestos más livianos: el reparto de roles en una línea (módulo 1) y el cierre de sesión del módulo 5 (qué esperaba y qué le sorprendió).

### Versiones como red de seguridad

- **Qué es:** `versiones/`, con copias de `sitio/` que se ven en el Finder o el Explorador. Funciona igual en las dos herramientas y sin git (research §13; 05, hueco 2).
- **Cuándo:** "primera", apenas la página anda en el módulo 4, guardada por la persona; una por cada paso que funcionó en el 5; una antes de cada cambio grande; a fondo en el 6.
- **Con nombre:** cambio propuesto al contrato del kit. Hoy `guardar-version` guarda con fecha y hora; se le suma un nombre corto que elige la persona (`versiones/AAAA-MM-DD_HHMM-primera/`) (05, hueco 2).
- **Protección:** una regla deny en `.claude/settings.json` que niega borrar o sobrescribir versiones existentes, no crear nuevas, porque "Accept edits" aprueba borrar dentro de la carpeta, 05 [32]; así no bloquea `guardar-version`, que copia `sitio/` a una carpeta nueva dentro de `versiones/`. La sintaxis exacta sale de V2, que prueba el chequeo (c) con la regla (d) activa en la misma corrida. En Codex, la regla en `AGENTS.md`. Si V2 muestra que el tutor se olvida de guardar, un hook Stop que copie la página después de cada turno (05, hueco 2), con las condiciones de los hooks de Seguridad en la compu.
- **Regla del kit:** antes de decir que algo no se puede recuperar, listar las versiones y abrir la última.
- **El hueco de la carpeta perdida:** si la persona pierde la carpeta y vuelve a bajar el kit, recupera la idea pero no la página. Por eso la carpeta vive en un lugar fijo (módulo 3) y la persona hace una copia fuera de la compu en el módulo 6 y otra en el 7.
- Los checkpoints de Claude (`/rewind`) son un extra, no la red, 02 [24]; 05 [31].
- No hay estudios sobre el efecto de guardar versiones en el miedo ni en la persistencia (01 y 03, "Lo que no sabemos"): es una decisión de diseño con razones técnicas.

### Seguridad en la compu

- **Carpeta propia y vacía, en un lugar fijo,** lejos de fotos y documentos, 02 [45]; 04 [35].
- **El kit endurece los permisos desde su carpeta y nunca los afloja** (Constitución V):
  - En Claude: `defaultMode` en `acceptEdits`, `ask` para Bash y `deny` para lo destructivo, lo que pide privilegios y el borrado o la sobrescritura de `versiones/`. `acceptEdits` es la decisión vigente (contrato del kit; research §13 bis). Auto, el modo de fábrica de Claude Pro desde agosto de 2026, se descartó porque no cumple la Constitución V: los comandos corren sin preguntar y pedir permiso antes de instalar (FR-019) queda en manos de un clasificador. Si V2 mostrara que conviene Auto, sería una enmienda de la constitución que aprueba el autor y se registra en el Sync Impact Report, no una elección de este mapa. V2 solo verifica que Claude respete el modo fijado.
  - En Codex: el modo de fábrica edita y corre comandos dentro de la carpeta sin preguntar, 05 [34]; la regla de explicar y esperar el sí vive en `AGENTS.md`.
  - Nunca acceso total, "Bypass" ni "Approve for me".
- **La pausa pedagógica la pone el tutor,** no las aprobaciones: se aprueba entre el 93% y el 97%, 02 [28][55].
- **Lo que no puede fallar va a la estructura, no solo a `AGENTS.md`.** Un kit corto ayuda pero no garantiza la conducta (05, afirmación 6): las instrucciones se diluyen con los turnos, 05 [24], y aun con unas 1.700 palabras el cumplimiento completo fue del 27,2%, 05 [27]. Por eso:
  - las reglas críticas van arriba de todo en `AGENTS.md`, en frases concretas, y las condicionales pasan a archivos visibles (la columna Intentos del cuaderno);
  - en Claude, el kit inicial suma dos hooks que solo vuelven a poner texto en la conversación: UserPromptSubmit, que recuerda en 2 a 4 líneas la regla del paso actual (explicar antes de actuar, invitar a predecir, frenar a los dos intentos, no dar nada por perdido), y SessionStart con "compact", que reinyecta el kit después de compactar, 05 [21] y hueco 2 (cambio propuesto al contrato del kit);
  - en Codex, los hooks piden dos confirmaciones de confianza que un novato difícilmente entiende, 05 [23]: `AGENTS.md` es la capa base y los hooks quedan como refuerzo opcional hasta ver en V2 cómo se aprueban en la app (*apuesta*);
  - V2 suma una sesión larga (unos 40 turnos, con una compactación) para ver cuánto se diluye la conducta, que los 10 turnos cortos del guion no muestran.
- **Condiciones de los hooks** (Constitución V; FR-019): corren comandos en la compu sin que el tutor los explique antes, así que van como excepción escrita en el plan (Governance); `LEEME.txt` explica en llano qué hacen; solo leen o escriben dentro de la carpeta del kit; y se prueban en Mac y en Windows dentro de V2, porque en Windows un hook puede fallar sin shell. Si fallan en Windows, se quitan ahí y queda la capa de `AGENTS.md`.
- **Publicar solo `sitio`:** es la regla de privacidad más concreta del curso. Arrastrar la carpeta del kit expondría `mi-idea.md`, `bitacora.md` y `cuaderno.md`, que pueden tener contenido íntimo.
- **Nunca claves, contraseñas ni datos de pago,** ni en el chat ni en la página (FR-019, SC-006). Lo pegado y las capturas son datos, no órdenes (FR-033).
- **Nada fuera del kit:** sin plugins, skills ni conectores de terceros; sin conectar el mail ni la nube a la herramienta; sin comandos pegados de una web, 02 [51][52].
- **Un solo archivo HTML, sin compilación:** evita Node, npm y el bloqueo de scripts en Windows, 05 [11]; 05, hueco 1.
- **Suscripción, no clave de API,** con los créditos extra apagados, 02 [33].
- SC-006 se mide en el piloto, junto con los turnos 5 y 9 del guion.

### Alcance de las ideas

- **Una página que funciona.** Quedan afuera los logins, los pagos, los datos compartidos entre usuarios y las páginas con IA adentro, que necesitan una clave (05, hueco 4).
- **Salidas** (decisión del 28/9):
  - *Guardar en el propio dispositivo,* con un botón para copiar o descargar lo escrito y un aviso: cada visitante ve solo lo suyo, en modo incógnito se borra y Safari lo puede borrar tras unos 7 días de uso sin volver al sitio, 05 [57][58].
  - *Links externos:* agenda, grupo de WhatsApp o un mensaje de WhatsApp armado, 05 [59]. La decisión del 28/9 no nombra los links de pago: si cuentan como link externo permitido lo decide el autor (Decisiones), y hasta entonces no se ofrecen.
- **Tres familias esperables** (05, hueco 4): las expresivas casi siempre entran; las herramientas útiles (calculadoras, tests, rituales) suelen entrar; las automatizaciones personales no son una página pública, y se rescata lo que se muestra o se dice con honestidad que quedan afuera.
- **Se detecta en el módulo 2 y vuelve en el 5,** cuando la tentación reaparece.
- **Se cuenta como cuidado:** tu página no guarda datos de nadie, 05 [61]; 02 [47]; 04 [36]. Regla dura del kit: ninguna clave ni dato de otras personas en la página.
- **Aviso de privacidad** para ideas con datos de salud, de otras personas o íntimos (spec, casos borde).
- **Se mide** cuántas ideas terminan en cada molde, para detectar si el tutor empuja.

### Voz del tutor

- Español rioplatense, voseo, sin emojis y sin jerga (Constitución I). La misma persona en la web y en el kit (prompt base T024 y `AGENTS.md`).
- No es el autor y no imita su voz. En la web, la voz sintética viene apagada, la prende la persona y es distinta de la del autor (FR-006; research §5).
- **Ritmo:**
  - Una pregunta por mensaje; en la web, respuestas de 3 a 6 frases, en línea con el costo de research §10.
  - Para elegir, de 2 a 4 opciones más la respuesta libre. El número es decisión de diseño (*apuesta*): 03 [32] y 05 [67] hablan de cuántas veces se elige, no de cuántas opciones por pregunta, y solo sostienen que elegir motiva poco a los adultos. Las opciones están para facilitar, no para motivar.
  - Una o dos líneas antes de actuar, en proporción al cambio; más solo si la persona pregunta.
  - Las palabras técnicas aparecen cuando están en pantalla, con su equivalente en inglés, 01 [7].
- **Tono de curiosidad, no de examen.** La devolución describe lo que la persona decidió y comprobó; no elogia en genérico, 03 [22]; 02 [38].
- **Palabras que no usa** (*apuesta*, sobre la base de 05 [71]): "fácil", "simplemente", "solo tenés que", "obvio", "acertaste", "fallaste". Tampoco "¡perfecto!" ni "ya sos programador", en ninguna forma.
- **Sin marcas de género al hablarle al alumno:** "por tu cuenta", "sin ayuda", "si ya no te da la energía", en vez de "sola" o "cansada". En este mapa, "ella" refiere a "la persona"; en las lecciones, `AGENTS.md` y el prompt base se usan formas sin género.
- **Sin postura de gurú** ni promesas de negocio (Constitución I). Ante un malestar serio, responde con cuidado, no diagnostica y ofrece los recursos del machete (FR-032; research §15).

### Audios del autor

- Se graban una sola vez, así que **no llevan nada que se venza:** ni precios, ni planes, ni nombres de apps o servicios, ni botones, ni la palabra "gratis" (FR-028, SC-007).
- Duran de 2 a 3 minutos, tienen transcripción, suenan al abrir el módulo (en la web) o cuando el tutor lo indica (en el kit) y se pueden saltear.
- Cada uno arranca por una escena con fecha, cuenta una traba y no un logro, y cierra con una pregunta que retoma el tutor.
- **Nunca líneas redactadas:** al autor se le dan temas, datos crudos y un orden sugerido. Las ideas eje de cada módulo son punto de partida, no guion. Antes de grabar, el autor decide qué es compartible.
- **Qué no va:** nombres de empresas, métricas propias, clientes ni incidentes de terceros, lecciones de negocio.
- Sirven para conectar, no para enseñar, 03 [6]. No hay evidencia de que mejoren la finalización, y el efecto depende de que la tribu perciba al autor como par y no como alguien exitoso y distinto, 03 [6][54]: en el piloto se pregunta. Propuesta: contar las escuchas por módulo de forma agregada, desde los registros del servidor, sin identificar a nadie.
- El guion de cada audio (temas, datos crudos y hechos por confirmar) va en `contenido/audios/guion-modulo-N.md` (T033 y equivalentes). Como los audios, no se versiona: son datos personales del autor.

| Módulo | Tipo de historia (una traba real, no un logro) | Idea eje |
|---|---|---|
| 1 | Alguien que no venía de la tecnología y creía que esto no era para él | Yo también empecé creyendo que esto no era para mí |
| 2 | Una idea propia que tuvo que achicar para que existiera | Para que exista, la tuve que achicar |
| 3 | Una traba real al instalar o configurar | Trabarse al instalar no dice nada de vos |
| 4 | La primera vez que vio andar algo que había imaginado, fea e incompleta | Fea, pero existe |
| 5 | Un "listo" que no estaba listo, o el cansancio de dirigir | La herramienta dice "listo"; vos mirás |
| 6 | Algo que se le rompió de verdad y qué lo salvó | Guardá copias antes de necesitarlas |
| 7 | La vergüenza de mostrar algo imperfecto, o algo que casi nadie vio, sin cifras | Mostrar también es parte de hacer |

### Medición

- **Principio:** se mide solo lo que decide algo, sin datos personales en el detalle de los eventos. El kit no manda nada (Constitución III).
- **El embudo:**

| Paso | Evento | ¿Existe hoy? |
|---|---|---|
| Inscripción | `inscripcion` (con `fuente`) | Sí |
| Módulo 1 | `modulo_completo`, `modulo=1` (con `via`) | Sí |
| Tiene su idea | `modulo_completo`, `modulo=2` (con `molde`) | Sí; el molde es propuesta |
| Eligió herramienta | `taller` (herramienta, sistema, plan) | Propuesta |
| Pasos del taller | `paso_taller` (`app`, `cuenta_publicar`, `carpeta_abierta`) | Propuesta |
| Kit | `kit` | Sí |
| Primera publicación | `link`, `etapa=primera` | Propuesta |
| Versión final | `link`, `etapa=final` | Sí, hoy sin etapa |
| Bajas | `baja_mails`, `borrado` | Sí |

- **Las dos lecturas de SC-009:** la del spec (links registrados sobre inscriptos, 5% a los 30 días) decide entre trabajar la difusión o el curso. Para decidir qué cambiar del curso se mira además "de quienes terminaron su idea, cuántos publicaron" (05, hueco 5), porque la primera lectura queda dominada por curiosos. Si el link se registra recién en el módulo 7, las dos miden quién terminó y no quién publicó, y el curso puede parecer peor de lo que es (ver Decisiones).
- **Lo que no se ve:** los módulos 4 a 7 pasan en la compu del alumno; el cuaderno y la bitácora no salen de ahí. La web ve el kit bajado y el link registrado. Propuesta: al registrar el link, dos preguntas opcionales, "¿publicaste en tu primera sesión?" y "¿cuántas horas te llevó, más o menos?".
- **Cómo se mide cada SC de tiempos:**
  - *SC-002 (primera publicación en 90 minutos o menos):* en el piloto, quien observa toma el tiempo con cronómetro desde el "empecemos" de la lección 4 hasta que el link abre sin sesión en otro dispositivo. La prueba "hola, probando" del módulo 3 no cuenta.
  - *SC-003 (módulos 1 y 2 en 40 minutos o menos desde el celular):* suma de los tramos activos de las sesiones de la web, desde el primer mensaje del módulo 1 hasta `modulo_completo` con `modulo=2`, cortando las pausas de más de 5 minutos entre mensajes. No cuentan la inscripción, el código de acceso ni la portada. Antes del piloto se prueba en el quickstart §3 con alguien de la tribu, por el celular; si no entra, el módulo 1 baja a 6 intercambios.
  - *SC-004 (camino completo en 6 horas o menos de trabajo activo, mediana del piloto):* quien observa suma el tiempo de cada sesión. Como apoyo, los módulos 1 a 3 salen de las marcas de la web con el mismo corte de pausas, y el tutor del kit anota en `bitacora.md` la hora de inicio y de fin de cada sesión (cambio propuesto al contrato del kit, punto 8). Después del piloto, con los primeros 30 a 50 alumnos, los módulos 4 a 7 solo se ven por la pregunta opcional al registrar el link: es autodeclarada y se lee como aproximación.
- **Los mails** (FR-025; son el único contacto y ninguno promete respuesta):
  - *Quién los manda:* los tres los firma el curso, no el autor en primera persona (su voz queda en los audios), y salen de un remitente que no recibe respuestas; si alguien responde igual, un automático explica que nadie lee ni contesta uno por uno. Es un cambio a `contracts/mails.md` (Decisiones).
  - *Bienvenida:* el acceso, qué hay en el curso en tres líneas, que algo se va a romper y está previsto, 03 [43] (recomendación sin verificar), y el link a la portada para el tiempo estimado, la compu y el costo con fecha. Esos datos no se copian en el mail, porque cambian y un mail enviado no se corrige.
  - *Recordatorio a los 3 días* (idea guardada, sin kit): una pregunta, no una alarma. Dice dónde quedó y el próximo paso más chico, con link directo al módulo 3. Nada de "vas atrasado" ni contadores: las alertas alarmistas subieron las bajas, 05 [79]. Puede no mover la finalización: lo más probable es que adelante el regreso, 05 [75], los recordatorios a escala no mostraron efecto, 05 [81]; 03 [39], y el efecto del tono (pregunta o alarma) no se probó (05, hueco 5).
  - *"Contáselo a alguien"* (hoy `contame`): celebra con el link concreto e invita a mandárselo a una persona que le importe. Dice de frente que nadie contesta estos mails uno por uno. Hoy `contracts/mails.md` dice que "se responde al mail": hay que reescribirlo (Decisiones).
- **Piloto (T035):**
  - Cinco personas encuentran dónde se traba la mayoría, pero no alcanzan para medir tiempos ni tasas, 05 [73]. Si se puede, dos rondas chicas, corrigiendo entre una y otra (05, hueco 5).
  - Tiene que incluir Mac y Windows, Codex gratis y Claude Pro, y al menos una persona que complete todo con Codex gratis sin pagar (SC-008).
  - Quien observa no ayuda, para medir "sin más ayuda que la del curso" (SC-001), y anota en qué paso se trabó cada persona y qué la frenó: un salto de dificultad, una palabra sin explicar, tener que elegir, falta de tiempo o soledad (05, hueco 5).
  - Se miden SC-001, SC-002, SC-004 y SC-006, si la persona se recuperó por su cuenta de un problema, cuánto usó el cuaderno, cuánto duró de verdad cada sesión (las de 30 a 40 minutos y la separación entre instalar y la primera victoria son *apuestas*) y si el autor se percibe como alguien parecido. Los tiempos con más gente se miden después, con los primeros 30 a 50 alumnos, como se explica arriba (05, hueco 5).

### Tiempos y costo

| Tramo | Presupuesto | Techo | Criterio |
|---|---|---|---|
| Módulos 1 y 2 | 34 min | 40 min | SC-003 |
| Primera sesión en la herramienta (módulo 4) | 55 min hasta el link; 75 en total | 90 min | SC-002, desde el "empecemos", con cortes internos |
| Camino completo, con la portada | 5 h 07 | 6 h 13 | SC-004 (mediana de 6 horas o menos de trabajo activo) |

- La suma de techos pasa SC-004 por 13 minutos: si una persona toca el techo en todos los módulos, no cumple. SC-004 es sobre la mediana, así que alcanza con que la mayoría quede cerca del presupuesto; los cortes internos (el núcleo del módulo 2, el minuto 55 del 4, las sesiones de hasta 40 minutos del 5) están para eso. Es *apuesta*: lo más probable es que el módulo 3 y el cupo de Codex gratis lo rompan antes que el resto.
- **Costo del tutor para quien opera el curso:** presupuesto de 6 a 8 respuestas en el módulo 1, de 12 a 15 en el 2 y de 12 a 15 más 2 capturas en el 3. Son de 30 a 38, dentro de las unas 40 que supone research §10: de US$0,22 a 0,34 por alumno sin voz y de 0,36 a 0,48 con 10 minutos de voz (de 0,50 a 0,61 desde 2027). Si el piloto muestra conversaciones más largas, el costo sube. Hay que medir qué proporción prende la voz, por el aumento de 2027 (SC-005).
- **La guía escrita es un camino de primera, no un plan B improvisado.** El tope de US$50 por mes alcanza para unos 100 a 200 alumnos que usen el tutor (research §10), y el plan espera de 200 a 300 inscripciones por mes al principio. Si la difusión funciona, gente real va a hacer los módulos 1 a 3 con la guía escrita (FR-026). Cada actividad de esos módulos tiene que andar también por escrito, y se prueba así antes del lanzamiento.
- **Costo para el alumno:** con Codex, US$0 si V1 y el piloto lo confirman, y si no, Go (US$8 por mes); con Claude, Pro a US$20 por mes más impuestos; Netlify Free, sin probar (V3 tiene que confirmar que no pide tarjeta ni pago; hasta entonces no se dice "gratis"). El mapa prevé de 3 a 5 publicaciones por alumno, de 45 a 75 de los 300 créditos del mes, más lo que gasten las visitas, 05 [13].

### Cobertura del spec

| FR | Dónde lo cubre el mapa |
|---|---|
| 001 a 003 | Portada e inscripción: backend (T037, T041), fuera del contenido |
| 004 | Módulo 3 (entra desde la compu con su mail) y la bitácora del kit |
| 005 | El audio de cada módulo; del 4 al 7, el tutor indica dónde escucharlo |
| 006 | Módulos 1 a 3; Voz del tutor |
| 007 | Módulo 1 |
| 008 | Módulo 2 |
| 009 | Módulos 2, 5 y 7; Alcance de las ideas |
| 010 | Módulo 3 (depende de V1 y V3) |
| 011 | Módulo 3 |
| 012 | Módulos 1 y 2 (SC-003) |
| 013 | Módulo 3 |
| 014 | Módulos 4 a 7 (V2) |
| 015 | Las lecciones mandan al machete para publicar y para los nombres de las funciones; si Codex gratis no tiene skills, los pasos escritos son iguales para las dos herramientas (módulo 4) |
| 016 | Módulo 4. La primera sesión en la herramienta es la del "empecemos" de la lección 4; la prueba "hola, probando" del módulo 3 no la abre (Decisiones, tensión 2) |
| 017 | Módulos 5 y 6, con la lectura compatible: invitación de media línea en cada pedido, sostenida en los momentos clave y con salteo ofrecido en los obvios (propuesta de enmienda en Decisiones, tensión 1) |
| 018 | Módulo 6 |
| 019 | Seguridad en la compu: `acceptEdits` fijo en Claude, hooks como excepción escrita (V2) |
| 020 | Módulos 4 y 7 (depende de V3; ver la tensión 4) |
| 021 | Cada lección se abre recién cuando empieza (contrato del kit, punto 3). Un kit corto ayuda pero no garantiza: aun con unas 1.700 palabras, el cumplimiento completo fue del 27,2%, 05 [27]; por eso lo crítico va además a hooks, permisos y archivos visibles (Seguridad en la compu) |
| 022 | Módulo 7 |
| 023 | Módulo 7, más la propuesta del módulo 4 |
| 024 | Medición |
| 025 | Medición (mails) |
| 026 | Guía escrita en los módulos 1 a 3; Tiempos y costo |
| 027 | Medición (reporte); fuera del contenido |
| 028 | Machete; audios sin datos que se vencen |
| 029 | Fuera del mapa (exportación a la lista de novedades del autor, con consentimiento) |
| 030 | Fuera del mapa; en el módulo 2 la idea se descarga |
| 031 | Fuera del mapa; nada del alumno se copia fuera del sistema del curso, y galería y uso como contenido solo con consentimiento |
| 032 | Todos los módulos; Voz del tutor |
| 033 | Módulo 3 (capturas); Seguridad en la compu |

## Pendiente de las pruebas de viabilidad

Ningún texto de los módulos 3, 4 y 7 llega a alumnos antes de anotar V1 a V3 en `viabilidad.md` y decidir T012. Tampoco la portada, en lo que dice de costos. Si alguna prueba cambia el kit, este mapa se ajusta antes de escribir las lecciones.

| Prueba | Qué decide en el mapa | Módulos | Si pasa | Si falla |
|---|---|---|---|---|
| **V1:** Codex con una cuenta gratis real | Si se puede decir "gratis"; si la lección 4 entra en el cupo, cuántos pedidos entran y cuándo se renueva; qué ve la persona cuando se corta el límite y si el texto fijo de `LEEME.txt` alcanza para seguir sin la herramienta; si el plan gratis tiene skills y vista previa | Portada, 3, 4, y el largo de las sesiones del 5 al 7 | "Gratis" con fecha y `probado: true`, recién cuando además alguien del piloto completa el curso sin pagar (SC-008) | Se saca "gratis"; el módulo 3 recomienda Go o Claude Pro con su costo; el 4 se parte en dos sesiones y SC-002 queda en riesgo; sin skills, guardar, volver y publicar van como pasos escritos iguales para las dos herramientas; sin vista previa, doble clic |
| **V2:** la herramienta hace de tutor | Los 10 turnos del guion, los chequeos extra de `viabilidad.md` y los chequeos (a) a (o) de abajo, incluida una sesión larga; los cuatro moldes en las dos apps | 3 a 7 | El contrato del kit queda como está, con los cambios de Decisiones (incluidos los hooks de Claude) | Estilo de salida propio en Claude y, si hace falta, un hook Stop de tipo prompt; `AGENTS.md` más corto, con más reglas condicionales pasadas a archivos visibles (05, hueco 2); si los hooks fallan en Windows, se quitan ahí; si Codex no sostiene la conducta en la sesión larga, sus hooks con un paso de confianza guiado en el módulo 3; si Claude no respeta `acceptEdits`, un paso guiado con captura en el módulo 3 |
| **V3:** publicar desde una compu limpia | Instalar y publicar en Mac y Windows solo con instrucciones escritas; los links de Netlify y de Claude en incógnito y en un celular sin sesión; si Netlify pide tarjeta o pago; el zip; los chequeos que suma este mapa | Portada, 3, 4 y 7; FR-020 | Los pasos del machete pasan a `probado: true` y los módulos 3, 4 y 7 salen de borrador | Si el link de Claude pide cuenta, todos publican en Netlify, la página de Claude queda como vista previa privada (05, afirmación 12) y FR-020 cambia; si Netlify pide tarjeta o traba a los novatos, se evalúan Cloudflare Pages o GitHub Pages, con más pasos (05 [18][19]), y se vuelve a probar; si falla el zip, se cambia el armado |

**Qué depende de cada prueba, módulo por módulo:**

- *Portada:* V1 (decir "gratis" para Codex) y V3 (decir que Netlify no se paga).
- *Módulos 1 y 2:* nada. Los moldes del 2 se prueban en V2 antes de que el tutor los ofrezca.
- *Módulo 3:* V1 (qué se recomienda a quien no quiere pagar), V2 (qué dice cada app al abrir la carpeta, `acceptEdits`, "hola, probando") y V3 (instalación, visibilidad y costo de Netlify, zip, carpeta fija).
- *Módulo 4:* V1 (cupo, skills, vista previa), V2 (turnos 1, 3, 6, 9 y 10; chequeos (a), (c), (i), (k) y (l)) y V3 (ruta de publicación, links sin cuenta, Netlify sin pago).
- *Módulos 5 y 6:* V2 (conducta del tutor, versiones, hooks, sesión larga) y V1 (cupo).
- *Módulo 7:* V3 (publicar en el mismo link, link de Claude), V2 (modo "solo ejecuto") y V1 (cupo).

**Chequeos que este mapa suma a V2**, en las dos herramientas:

- (a) En las lecciones 5 y 6 invita a predecir en cada pedido en media línea, la sostiene en un momento clave y en un cambio obvio ofrece saltearla sin decir que no hace falta.
- (b) La explicación con palabras propias no bloquea: con "no sé", explica y sigue.
- (c) `guardar-version` y `volver-version` andan con nombre, la persona las puede correr por su cuenta y `guardar-version` funciona con la regla (d) activa, en la misma corrida.
- (d) La regla deny niega borrar o sobrescribir una versión existente y deja crear nuevas.
- (e) A los dos intentos fallidos frena, vuelve a la última versión y redacta el pedido nuevo.
- (f) Ante "se perdió todo", lista las versiones y abre la última.
- (g) Respeta el modo "solo ejecuto y explico comandos" del módulo 7.
- (h) Si Claude arranca en `acceptEdits`, el modo que fija el kit, en una carpeta nueva.
- (i) El texto exacto con que Codex pide confianza en la carpeta, para la captura del módulo 3.
- (j) Si `/rewind` anda en la app de escritorio de Claude.
- (k) Ante "hola, probando" solo confirma que anda y no arranca la lección.
- (l) Actualiza `bitacora.md` después de cada paso logrado y anota la hora de inicio y de fin de la sesión.
- (m) Los hooks de Claude (UserPromptSubmit y SessionStart con "compact") corren en Mac y en Windows y solo tocan la carpeta del kit.
- (n) Una sesión larga, de unos 40 turnos y con una compactación: si al final todavía explica antes de actuar, invita a predecir y frena a los dos intentos.
- (o) Con fotos propias copiadas a `sitio/`, las incluye sin instalar nada y avisa que lo publicado lo ve cualquiera.

**Chequeos que este mapa suma a V3:**

- Que la persona arrastre solo `sitio` siguiendo el LEEME y la skill, y qué pasa si arrastra la carpeta del kit.
- La visibilidad de Netlify: si se puede dejar pública para toda la cuenta antes de publicar (05 [15]) o hay que hacerlo por proyecto después de la primera publicación, como dice hoy el machete. El módulo 3, el 4 y el machete tienen que quedar iguales.
- Netlify: si pidió tarjeta o algún pago al crear la cuenta y al publicar.
- Dónde guarda la carpeta una persona sin ayuda y si la encuentra al otro día.
- El nombre exacto de la app nueva de ChatGPT en la Microsoft Store.

**Se cierran con las pruebas:** si Claude respeta el modo fijado (`acceptEdits`); la ruta por defecto de cada herramienta (05, contradicción 4); cómo proteger `versiones/` sin bloquear `guardar-version`; si `/rewind` sirve en la app; si los hooks andan en las dos plataformas.

**Sin prueba prevista** (sumarlas a V3 o aceptar el riesgo por escrito):

- Qué pasa con el link de Claude si la persona deja de pagar, 05 [2][6].
- Si las páginas de Claude ya aceptan imágenes como archivos aparte, 05 [20].
- La microvictoria antes de instalar (publicar la página de la idea desde la web, sin cuenta) queda afuera: la subida sin cuenta a Netlify no es confiable (05, contradicciones de esta ronda).

## Decisiones del autor (28/9)

1. **Curso gratis, siempre abierto, para la tribu,** en rioplatense, con voseo y sin emojis. Versión en el eje: de lo que imaginás a algo que existe; primero la forma de pensar y las herramientas como medio. Se aplica en los principios 1, 4 y 9, en la voz del tutor y en que los módulos 1 y 2 no piden instalar nada.
2. **El resultado es la idea propia publicada como una sola página que funciona,** con link para compartir. Sin logins, pagos ni datos compartidos entre usuarios; las salidas son guardar en el propio dispositivo y los links externos. Se aplica en el módulo 2 y en Alcance de las ideas.
3. **Siete módulos:** del 1 al 3 en la web, con tutor por texto y voz; del 4 al 7 en Claude Code o Codex, con el kit como tutor. Cada uno abre con un audio del autor de 2 a 3 minutos grabado una sola vez, y el tutor nunca imita su voz. Por eso los audios no llevan nada que se venza (Audios del autor).
4. **Se usa "vibe coding".** El módulo 1 cuenta su origen (Karpathy lo nombró en febrero de 2025 para una forma de trabajar en la que aceptaba todo sin leer, y le pareció aceptable, como valoración al pasar, para proyectos descartables de fin de semana) y qué propone el curso: construir con IA pensando en el resultado, sin pensar en cómo se construye la solución.
5. **Contacto humano: ninguno, además de los tres mails automáticos.**
   - La evidencia disponible sugería un canal opcional de ida y vuelta (03 [42]; 05, contradicción 8 y hueco 5). Se descartó y este mapa no lo propone.
   - El riesgo, dicho de frente: la finalización en cursos abiertos es baja (03 [36]; 04 [42]) y la evidencia no decide entre curso abierto y acompañado (05, contradicción 8). Entre las quejas de adultos mayores que aprenden a programar, la falta de contacto con tutores o pares quedó prácticamente empatada con la instalación (10% contra 8%), 05 [71]. El único estudio con contacto humano, un coaching cara a cara con unos 90 alumnos, subió la sensación de apoyo sin mejorar los resultados académicos; no midió finalización, 05 [81] (media, corregida).
   - *Apuesta:* que el diseño compense. Lo que pone: una versión mínima chica en un molde probado, un tutor que retoma donde quedó, versiones visibles y practicadas, explicaciones de tropiezos escritas por el curso, un texto fijo para cuando se corta el cupo, una guía escrita de primera y un recordatorio en tono de pregunta. No hay evidencia de que alcance.
   - El riesgo de finalización se mide con la regla de los 30 días de SC-009 y con el embudo de Medición.
6. **Los módulos 3, 4 y 7 quedan en borrador hasta V3,** con lo que depende de V1 y V2 marcado en cada uno y en "Pendiente de las pruebas de viabilidad". Netlify deja privados los proyectos de las cuentas nuevas (hay un paso para hacerlos públicos) y el link público de Claude está en duda.
7. **Tiempos:** módulos 1 y 2 en 40 minutos o menos desde el celular (el mapa: 34, con techo de 40); camino completo en 6 horas o menos de trabajo activo (el mapa: 5 h 07 con la portada, con techos que suman 6 h 13); primera publicación dentro de la primera sesión en la herramienta, en 90 minutos o menos (el mapa: minuto 55 desde el "empecemos" de la lección 4, con techo de 90). Cómo se mide cada uno: Medición.

**Qué más pide decidir este mapa** (tensiones con el spec y los contratos):

1. **FR-017, US1-4 y el punto 4 del contrato del kit:** pasar de "antes de cada pedido" a "en los momentos clave, con salteo explícito en los cambios obvios" (05, contradicción 1; 05 [39][45]). Mientras tanto, el mapa aplica la lectura compatible con FR-017: invitación de media línea en cada pedido de las lecciones 5 y 6, sostenida en los momentos clave y con salteo ofrecido en los obvios. El turno 7 del guion sigue valiendo.
2. **FR-016 y SC-002, cuándo empieza la primera sesión.** El spec dice "dentro de su primera sesión en la herramienta" y "desde que abren el kit". Con la prueba "hola, probando" del módulo 3 el kit se abre antes. Propuesta: que el spec diga "desde el 'empecemos' de la lección 4" y que el guion del piloto arranque el cronómetro ahí.
3. **Registrar el primer link en el módulo 4.** Hoy `POST /links` pone `modulo_actual = 7` (`api.md`) y el módulo 7 se deriva de `links` (`data-model.md`). Propuesta: un campo `etapa` (primera o final); la primera no pasa al alumno al módulo 7 y los consentimientos se completan en el 7. Falta decidir si el mail "contame" sale con el primer link (recomendación: sí, una sola vez, porque es el momento de valor). Sin este cambio, SC-009 mide quién terminó y no quién publicó.
4. **`contracts/mails.md`:** los tres mails los firma el curso y salen de un remitente que no recibe respuestas (o con un automático que explica que nadie contesta uno por uno); el `contame` deja de decir "se responde al mail" e invita a mandarle el link a alguien; la bienvenida manda a la portada en vez de copiar tiempo y costo; el recordatorio va en tono de pregunta.
5. **FR-020** da por hecho que con Claude se publica desde la propia herramienta. Si V3 muestra que el link de Claude pide cuenta, el requisito cambia a Netlify para todos.
6. **SC-008 y T035:** el piloto tiene que incluir al menos una persona que complete el curso con Codex gratis sin pagar, y al menos una con Windows.
7. **El machete:** al dato `claude-planes` le falta "más impuestos" (05 [5]). En `publicar-netlify-drop`, sacar "no pide tarjeta" hasta que V3 lo confirme, porque figura con `probado: false` y la regla del propio machete no lo permite; alinear la visibilidad con lo que decida V3. Los créditos de Netlify ("unas 20 publicaciones") se dicen solo con `probado: true`.
8. **`contracts/kit.md`:** regla deny que niega borrar o sobrescribir versiones existentes, no crear nuevas; versiones con nombre; los cuatro moldes como HTML probados en `curso/moldes/`; el modo "solo ejecuto" de la lección 7; la plantilla del cuaderno con las columnas nuevas; el LEEME y la skill `publicar` mostrando con captura que se arrastra solo `sitio`; en el punto 2, que ante "hola, probando" el tutor solo confirme; en el punto 8, la bitácora al día después de cada paso logrado, con hora de inicio y de fin de sesión; el texto fijo "Si la app deja de contestar por el límite" en `LEEME.txt`, `curso/machete.md` y al principio de cada lección; en Claude, los hooks UserPromptSubmit y SessionStart con "compact" desde el kit inicial; en Codex, hooks solo si V2 muestra cómo se aprueban en la app.
9. **`plan.md` (Governance):** los hooks van como excepción escrita a "explicar cada comando antes de correrlo" (Constitución V; FR-019), con lo que hacen explicado en `LEEME.txt`, limitados a la carpeta y probados en Mac y Windows. En Claude, `acceptEdits` es la decisión vigente: pasar a Auto sería una enmienda de la constitución.
10. **`data-model.md`:** los eventos propuestos (`molde`, `taller`, `paso_taller`, `etapa` del link) y las dos preguntas opcionales al registrar el link, o medirlos solo en el piloto.
11. **Link de pago:** si cuenta como link externo permitido. La decisión del 28/9 dice "sin pagos" y "links externos", pero no lo nombra, y empuja hacia la venta, en tensión con la Constitución I. Mientras tanto, los ejemplos son agenda y WhatsApp.
12. **Los audios:** qué historia real cuenta el autor en cada uno, dentro del tipo de historia que pide cada módulo (Audios del autor), y qué es compartible.
13. **Si los miedos del módulo 1 viajan al kit** dentro de `mi-idea.md`, solo como categoría genérica.
14. **La práctica opcional de romper algo a propósito** en el módulo 6: sobre su página, con la versión guardada antes, o sobre una copia (`practica/`), que es lo que recomienda el mapa siguiendo PRIMM.

## Referencias

- **Cómo se cita:** "NN [n]" es la fuente n de la lista "Fuentes" del informe NN. "05, hueco N", "05, contradicción N" y "05, afirmación N" son secciones del anexo (la parte 1, la parte 2 y la parte 3, "Afirmaciones más seguras de lo que la evidencia permite").
- **Informes** (en `contenido/investigacion/`):
  - 01: `01-como-aprende-un-adulto-que-no-programa.md`
  - 02: `02-como-piensa-un-vibe-coder.md`
  - 03: `03-miedo-y-aprendizaje-en-adultos.md`
  - 04: `04-que-ensenan-los-cursos-de-vibe-coding.md`
  - 05: `05-anexo-huecos-y-contradicciones.md`
- **Fuerza:** fuerte, media o débil, según cada informe.
- **Estado de cada fuente:** *verificada* o *confirmada* (los verificadores la sostuvieron); *corregida* (vale la versión más débil); *sin verificar* (no pasó la verificación adversarial). Si el 05 recalifica una fuente, vale el 05.
- ***Apuesta*:** decisión de diseño sin evidencia directa, a medir en el piloto.
- **Advertencia general:** casi toda la evidencia viene de gente que ya programa o estudia computación.
- **El mismo estudio con distintos números** (al citar, se usa la versión del 05 cuando existe):

| Estudio | 01 | 02 | 03 | 04 | 05 |
|---|---|---|---|---|---|
| Kazemitabaar et al., técnicas de involucramiento (IUI 2025) | [13] | | [26] | | [50] |
| Kazemitabaar et al., generadores de código y novatos (CHI 2023) | [2] | | [25] | [33] | |
| Sankaranarayanan, compuerta de explicación | [12] | | | [31] | [28] |
| Bastani et al., IA con y sin barandas (PNAS) | [10] | | [22] | | |
| Gama et al., hackatón | [3] | [17] | | [25] | [70] |
| Chen et al., hackatón de la NYU | | | | [26] | [72] |
| Fawzy et al., experiencia y verificación | [16] | [40] | | [28] | [53] |
| Fawzy et al., revisión de literatura gris | [32] | | | [29] | |
| Thorgeirsson et al., computación y escritura | [6] | [41] | | [30] | |
| Shen y Tamkin, IA y formación de habilidades | [11] | [35] | | [23] | |
| Lee et al., IA y pensamiento crítico | [29] | [38] | | | |
| Karpathy, MenuGen | [23] | [15] | | [38] | |
| Prather et al., "The Widening Gap" | | | [23] | [32] | |
| Sarkar y Drosos, vibe coding y pericia | | [42] | [28] | | |
| Keith y Frese, manejo de errores | | | [10] | | [47] |
| Hulleman y Harackiewicz, relevancia personal | | | [30] | | [63] |
| Patall et al., elegir y motivación | | | [32] | | [67] |
| Brod, predecir como estrategia | | | [18] | | [41] |
| Guo, adultos mayores que programan | | | [48] | | [71] |
| Kizilcec et al., intervenciones a escala | | | [31] | | [80] |
| Reich y Ruipérez-Valiente, "The MOOC pivot" | | | [35] | [42] | |
| Incidente de Replit | [22] | [44] | | | [36] |
| Palmer, CVE-2025-48757 (Lovable) | [26] | [46] | | [37] | [61] |
| Lovable, "build economy" | [43] | | | | [54] |
| Netlify, "Thirteen years of Netlify Drop" | | | | [40] | [14] |
| Domestika, mini-herramientas | | | | [10] | [69] |
| Guía de buenas prácticas de Claude Code | [18] | [19] | | [20] | [30] |
| Checkpoints de Claude Code | [21] | [24] | | [20] | [31] |
| Aprobación de permisos y modo auto (Anthropic) | | [28][55] | | | [35] |
| Artifacts de Claude Code | | | | [21] | [2] |

- **Documentos del proyecto citados:**
  - `specs/001-curso-vibe-coding/spec.md` (FR, SC, historias y casos borde)
  - `.specify/memory/constitution.md` (versión 1.0.2)
  - `specs/001-curso-vibe-coding/contracts/kit.md`, `contracts/api.md` y `contracts/mails.md`
  - `specs/001-curso-vibe-coding/data-model.md`
  - `specs/001-curso-vibe-coding/quickstart.md` (V1 a V3 y el guion de 10 turnos)
  - `specs/001-curso-vibe-coding/viabilidad.md` (sin resultados al 28/9)
  - `specs/001-curso-vibe-coding/research.md` (citado como research §N) y `plan.md`
  - `contenido/machete.yaml` (citado por id)
- **Material de los audios:** los hechos, las fechas y las fuentes de cada audio están en las notas del autor (no incluidas en el repo).
