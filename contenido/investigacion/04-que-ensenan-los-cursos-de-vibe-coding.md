# Qué enseñan los cursos de vibe coding para no programadores

> **Pregunta:** cómo están armados los cursos que existen (temario, primer proyecto, duración, formato, herramienta, forma de publicar, trato del miedo y de la forma de pensar) y qué huecos dejan para un curso como este.
> **Fecha:** 2026-09-28.
> **Método:** tres investigadores buscaron en paralelo desde tres ángulos: la oferta en español; la oferta oficial y en inglés, más la investigación académica; y los primeros proyectos, la publicación y las fricciones. Después, las 15 afirmaciones clave pasaron por una verificación adversarial, con dos verificadores independientes por afirmación. Resultado: 2 quedaron confirmadas, 11 se corrigieron a una versión más débil y 2 fueron refutadas: que ningún curso pida anotar lo esperado antes del pedido, y que la app de escritorio de Codex sea solo paga. Las corregidas aparecen en su versión corregida y las refutadas se reemplazaron por lo que sí encontraron los verificadores. No se agregó ninguna afirmación sin fuente.

## Resumen

- **Publicar en la primera hora ya es lo normal en los cursos gratis, pero siempre con el ejemplo del profesor.** En los dos cursos gratuitos de YouTube revisados en detalle, la primera página publicada llega cerca de la hora: entre los 59 y los 62 minutos en el de Cordero y a los 34 en el de Medina. En los dos casos es un negocio inventado por el profesor (una clínica dental, una colchonería) [1][3]. Build with Andrew promete una app andando en menos de 30 minutos sin instalar nada [15]. Lo que diferencia al curso no es la velocidad sino que la primera publicación sea con la idea propia. Ojo con el otro filo: en un estudio chico con estudiantes, varios de los que tuvieron dificultades terminaron creyendo que les había ido mejor de lo real [32].
- **Ningún curso de gran alcance se organiza alrededor del proyecto del alumno.** Casi todos se ordenan por herramienta o por funciones de la herramienta: Scrimba dedica 4 de sus 5 cursos a una herramienta cada uno, y Cordero y Medina van de los tokens a las skills y los subagentes [18][1][3]. Platzi se ordena por las capas de un proyecto que elige el profesor [6]. El antecedente más cercano, Claude Code for Everyone, ya usa la app de escritorio como tutor y planifica con una entrevista, pero construye un quiz predefinido y publica con GitHub y Vercel [17]. El hueco está en la idea propia, en el público y en el orden, no en el mecanismo del tutor.
- **El hueco de "predecir antes de pedir" es más angosto de lo que parecía.** La idea de que ningún curso pide anotar lo esperado quedó refutada. Platzi incluye un campo de resultado esperado en el prompt y enseña a probar comparando lo esperado con lo encontrado. Medina arma un "contrato" con criterios de éxito y de fracaso antes de ejecutar [6][3]. Pero ahí lo esperado es una instrucción para la IA. Lo que no enseña ningún curso revisado es la predicción como ejercicio del alumno, para calibrar su propio modelo mental. La evidencia a favor es indirecta y modesta [23][28][31].
- **Nadie trata como tema el miedo del principiante a la herramienta.** Aparece como frase tranquilizadora al pasar, como miedo a gastar tokens o, en el epílogo de Medina, como relato emprendedor sobre hacer las cosas con miedo [1][3]. "Mentalidad" se usa en clave de negocio, de lanzamiento o de compromiso para terminar el curso [7][11][1][9]. El hueco está confirmado. Lo que no hay es evidencia de que tratarlo como contenido mejore algo.
- **El costo cambia la elección de herramienta.** La pestaña Code de la app de Claude exige plan Pro, Max, Team o Enterprise, y los artifacts (la vía de publicación con menos pasos) también [22][21]. En Codex, según las páginas de precios de OpenAI al 28/9/2026, los planes Free y Go tienen acceso limitado en la app de escritorio, sujeto a despliegue gradual [44]. No sabemos si ese acceso gratis alcanza para construir y publicar una página. Hay que probarlo antes de grabar y decir el costo de entrada.
- **Publicar sigue siendo la parte más frágil.** Todos los cursos relevados publican creando una cuenta en un hosting externo [1][3][17]. Las vías "sin cuenta" se endurecieron: Netlify Drop protege con contraseña los sitios anónimos, da una hora para reclamarlos y borra los que nadie reclama [40]. Los artifacts de Claude publican una página que nace privada y se comparte con un link público desde Share [21]. Las trabas grandes aparecen en lo que rodea a la página: login, dominio, conectar una planilla [38][39]. La evidencia de que la instalación sea el peor momento es más débil de lo que parecía [1].
- **Guardar versiones es central, y la red de la herramienta no alcanza.** El checkpointing de Claude Code no registra cambios hechos con comandos de terminal, borra las copias a los ~30 días y, según su documentación, no reemplaza a git [20]. El mercado enseña a volver atrás a mitad del curso y con Git [1][3][9]. En este curso tiene que arrancar con la primera publicación.
- **Siempre abierto y sin vivos es la decisión que más cuestiona la evidencia, aunque de forma indirecta.** En los MOOC de Harvard y MIT, la baja finalización no mejoró en seis años [42], y los cursos pagos se apoyan en cohortes, vivos o mentoría [7][8][9][11]. Son datos de otra población y de 2012 a 2018. No invalidan el formato, pero obligan a compensarlo y a medir la finalización desde el primer día.

## Hallazgos

Criterio de fuerza:

- **Fuerte:** documentación oficial o fuente primaria leída y verificada, o un estudio grande con resultados claros.
- **Media:** un estudio empírico con limitaciones claras (muestra chica, población distinta, autorreporte), páginas de cursos o datos de plataforma.
- **Débil:** un caso único, la opinión de un practicante, material promocional o datos relativos difíciles de interpretar.

Las afirmaciones clave llevan además el resultado de la verificación: *verificada* o *corregida*. Cuando una fue refutada, se aclara y se da la versión que sostienen las fuentes. El resto no pasó por la verificación adversarial y conserva la fuerza que le asignó la investigación. Ninguna fuente estudió a adultos de 30 a 60 años sin experiencia y con miedo a la tecnología, así que ningún efecto llega a "fuerte" para este público.

### 1. Mapa de la oferta: formato, duración, herramienta y público

- **En español domina el video único, gratis y siempre disponible, de 3 a 7 horas.** Cordero con Claude Code (6 h 17 min, unas 849.000 vistas desde el 31/7/2026) [1] y con Codex (4 h 54 min, 56.000) [2]; MoureDev (3 h, 194.000) [5]; Medina (6 h 45 min, unas 40.000 vistas desde el 20/9/2026) [3]; Josema Fernández con Codex (17.000) [4] (media; las vistas y fechas de Cordero y Medina se verificaron).
- **Funcionan como puerta de entrada a comunidades pagas.** Imperio Agéntico, la comunidad de Cordero, cobra US$59 por mes, tiene 3.800 miembros y 6 vivos por semana, y apunta a founders y agencias [2] (media).
- **Los cursos pagos o institucionales se apoyan en cohortes, vivos o mentoría** (media):
  - Platzi: 15 clases, unas 2 h de contenido [6].
  - EducaciónIT: 18 h en vivo, 2 veces por semana, grupos de 20 [7].
  - Universidad del Rosario: 36 h en 7 semanas con Cursor, 950.000 COP [8].
  - Escuela de VibeCoding: presencial en Madrid, 15 cupos [9].
  - Fuggini: cohorte con mentoría y garantía de 14 días. La duración figura como 3 semanas en buscadores y como 4 en su sitio [11].
- **En inglés y en la oferta oficial** (media):
  - **Anthropic Academy** no tiene un puente entre entender la IA y construir. AI Fluency es para todo público pero no construye nada. Claude Code 101 (unas 2 h) pide manejar un editor y la terminal, y no tiene paso de publicación [12].
  - **OpenAI Academy** ofrece a principiantes sin experiencia solo un webinar de 1 hora sobre Codex (21/4/2026). El Bootcamp 101/201/301 apunta a builders e ingenieros [13].
  - **DeepLearning.AI** tiene Vibe Coding 101 con Replit (1 h 34 min, gratis; aclara que ayuda tener algo de experiencia) [14] y Build with Andrew (alrededor de 1 h, para quien nunca programó) [15].
  - **Scrimba en Coursera:** 5 cursos, unas 15 h, 22.143 inscriptos, nivel principiante sin experiencia previa (inscriptos y nivel verificados). Figura con 4,4/5 en 413 reseñas [18].
  - **Codecademy:** alrededor de 1 h con Cursor, 9.059 inscriptos. **Microsoft Learn:** Copilot en VS Code; recomienda conocer el proceso de desarrollo [19].
- **Los temarios de mayor alcance no se organizan alrededor del proyecto del alumno** (media, corregida: la versión original generalizaba desde Scrimba y omitía su quinto curso).
  - La especialización de Scrimba dedica 4 de sus 5 cursos (unas 7 h) a una herramienta o protocolo cada uno: Cursor, GitHub Copilot, Claude Code y MCP. El quinto, "Learn to code with AI", es el más largo (8 h). Enseña fundamentos de HTML, CSS y JavaScript con proyectos que arma el profesor: portfolio, juegos, extensiones de Chrome, apps con base de datos, una app móvil y deploy en Netlify [18].
  - Cordero ordena el temario por funciones de la herramienta: instalación, interfaz, primer proyecto, tokens, permisos, CLAUDE.md, skills, MCP, subagentes y automatización. Medina hace algo parecido y, según la investigación, también Josema y MoureDev [1][3][4][5].
  - Platzi no se ordena por herramienta sino por las capas de un proyecto del profesor, una billetera personal: interfaz, memoria, inteligencia, integraciones y monetización [6].
  - Según uno de los verificadores, los cursos que sí giran en torno al proyecto del alumno (cursodevibecoding.com y el proyecto final de la Escuela de VibeCoding) son pagos y chicos [11][9] (débil).
  - En español nadie ayuda a elegir entre Claude Code y Codex. Cordero tiene dos cursos separados [1][2] (media).
- **Le hablan a gente que quiere un negocio o ingresos.** Los primeros proyectos son la landing de una clínica dental inventada [1], la de una colchonería inventada [3], una app de gastos con monetización [6], un CRM con Stripe [11], una app de partes [4] y un sistema de gestión de leads [7] (media).
  - El único curso que arranca desde ideas sueltas y sensaciones es el de Domestika, con 273 alumnos y 6 reseñas [10] (débil: los verificadores no pudieron abrir la página, y la baja tracción puede deberse al precio, la plataforma o la difusión, no necesariamente a la falta de demanda).
- **Los modelos mentales van de un extremo al otro.** La Universidad del Rosario les enseña HTML, CSS, JavaScript, Python y bases de datos a no programadores [8]. Cordero, antes del primer pedido, solo explica que un proyecto es una carpeta con archivos relacionados [1] (media).

### 2. Primer proyecto y primera victoria

- **En los dos cursos gratis hispanos revisados en detalle, la primera publicación llega cerca de la primera hora, y lo publicado es un ejemplo del profesor** (media, corregida: se ajustaron los minutos, la cantidad de pedidos y el ejemplo de Medina; no se pudo comprobar que sean "los más vistos").
  - Cordero despliega en Vercel hacia el minuto 59 y deja la versión final a los 62. Lo presenta como "dos prompts", pero en pantalla hay al menos cuatro pedidos, además de la creación manual de la cuenta de Vercel. El segundo pedido ("súbelo") terminó en un artifact de claude.ai, y él lo redirigió a Vercel. Después tuvo que corregir porque había publicado en una cuenta vieja. El ejemplo es una clínica dental inventada, que él mismo llama ridícula [1].
  - Medina arranca el proyecto en el minuto 24 y lo publica en Netlify hacia el 34, arrastrando la carpeta a mano. El ejemplo es una colchonería inventada, con la indicación de inventar los datos [3].
  - En el curso de Codex de Cordero, la primera landing sale en el minuto 55 [2] (media).
- **En los pagos e institucionales, la publicación llega al final**: Platzi en la clase 11 de 15, EducaciónIT en la unidad 6 de 7, Rosario en el módulo 8 y Fuggini en el módulo 3 de 3. Además, todos van mucho más allá de una página: base de datos, login, pagos, automatizaciones [6][7][8][11] (media).
- **En inglés pasa lo mismo** (media):
  - Build with Andrew promete una app funcionando en menos de 30 minutos sin instalar nada: el chatbot genera un archivo y el alumno lo abre en el navegador [15].
  - Lovable promete construir y publicar en unos 10 minutos, con la web de un café como primer proyecto [16].
  - Los proyectos los pone el curso: una tarjeta de cumpleaños [15], un analizador SEO y una app de votación [14], un quiz de personalidad [17], el tablero Upvote de Lovable Academy [16] y un portfolio personal [18].
- **Excepciones parciales** (media):
  - El Blueprint de Lovable Academy convierte tu propia idea en una cadena de prompts, como alternativa para quien ya tiene una visión [16].
  - Codecademy arranca con un proyecto personal que sale de una ideación con la IA [19].
  - Build with Andrew cierra con un proyecto final propio [15].
  - En Claude Code for Everyone el quiz es fijo, pero cada alumno define las preguntas y los resultados [17] (verificado).
- **Qué terminan los principiantes en las primeras horas** (media).
  - En el track para principiantes de una hackatón de la NYU (unas 2 h sugeridas) salieron un diario de ánimo con guardado local, pomodoros, un monitor de presión arterial y un armador de CV [26].
  - También aparecen portfolios y quizzes [17][18].
  - Técnicamente, estas páginas funcionan mejor como un solo archivo HTML, sin paso de build y con los datos en localStorage [27]. Letra chica: localStorage vale por navegador y por origen, se borra en modo privado y, si se abre el archivo local, el comportamiento no está definido [27].
- **Los equipos que idean solos tienden a cerrar la idea temprano** (débil, corregida: la población era de experiencia mixta y mayormente de computación, y varias cifras estaban mal).
  - En una hackatón educativa de 9 horas en una universidad pública de Brasil participaron 31 estudiantes de grado en 9 equipos. La mayoría estudiaba computación: solo 4 de los 27 encuestados venían de otras carreras. Los autores observaron convergencia prematura en la ideación. 23 de los 27 encuestados dijeron que su equipo consideró cinco ideas o menos, apenas algo más de la mitad estuvo de acuerdo en que las ideas se revisaron y el 40% dijo haber trabajado una sola idea [25].
  - Casi todos llegaron a un prototipo: 19 de 27 consideraron su app funcional (casi siempre "mayormente"), 6 parcialmente funcional y 2 no funcional, con calidad de código despareja. Los autores sostienen que el formato corto les dio confianza a los recién llegados, pero la evidencia de eso es escasa [25].
  - Lo novato en ese grupo era sobre todo la experiencia en hackatones (para 20 de 27 era la primera), no la programación [25].
  - En la NYU, una participante sin experiencia hizo una app casi igual al demo del taller [26] (media).
- **La victoria rápida tiene doble filo.**
  - En un ensayo aleatorizado con 69 chicos de 10 a 17 años, el grupo con generador de código se sintió algo menos estresado (p=.056, marginal) y con más ganas de seguir programando (p=.025) [33] (media).
  - En un estudio cualitativo con 21 estudiantes de un curso introductorio de programación en EE.UU. (ICER 2024), 20 completaron la tarea con IA. La mitad mostró dificultades metacognitivas durante la sesión, y varios de ellos terminaron creyendo que les había ido mejor de lo real ("ilusión de competencia"). Los que avanzaban bien usaron la IA para acelerar lo que ya sabían hacer. Los autores sugieren que la IA podría ensanchar la brecha entre unos y otros, pero no midieron el aprendizaje ni la brecha, y no hubo grupo de control [32] (media, corregida: lo de la brecha es una hipótesis, no un resultado).

### 3. Instalación, cuentas y costo

- **La instalación aparece como punto de fricción, pero la evidencia es más débil de lo que parecía** (débil, corregida).
  - En el curso de Cordero, el comienzo del módulo de instalación con la app de escritorio (26:25 a 30:11) marca 0,90 en el mapa de "lo más repetido" de YouTube. Es el cuarto tramo más alto de 100: el máximo (1,0) está en la parte de Skills, y el primer proyecto llega a 0,92 [1].
  - Un comentario muy votado (unos 403 likes, el tercero, detrás de uno de 755 y del fijado por el autor) cuenta que un paso que en el video parece de 30 segundos puede llevarle 15 a 20 minutos a quien arranca de cero: tuvo que descubrir que necesitaba Git, instalarlo y después instalar VS Code. Pero ese paso es la instalación de la extensión en VS Code, que el video menciona al pasar como alternativa opcional, no el camino principal por la app de escritorio [1].
  - Los verificadores advierten que los picos al comienzo de un capítulo suelen reflejar saltos desde el índice, así que el pico no prueba que haya dificultad [1].
  - En el curso de MoureDev, el máximo del mapa caería en la instalación [5] (sin verificar; la fuente quedó sin URL).
- **En estudiantes no técnicos, la fricción principal fue la alfabetización informática básica.** Se vio en estudiantes de ICT, marketing, periodismo y comunicación: la estructura de archivos, dónde se instala cada cosa y las dependencias. Arrancaron intimidados y terminaron entusiasmados [35] (débil).
- **La app de escritorio de Claude Code pide elegir una carpeta de proyecto y necesita Git.** En Windows hay que instalar Git for Windows si aparece el aviso [22][35] (media).
- **"Sin terminal" no quiere decir sin herramientas de terminal.** La sección de problemas de Claude Code for Everyone admite que pueden hacer falta Node.js y la herramienta de línea de comandos de GitHub, que Claude instala y corre por el alumno. El curso da por hecho que el alumno tiene cuentas de GitHub y Vercel [17] (media, verificada).
- **Costo** (corregida en parte: lo de Claude se confirmó; lo de Codex estaba al revés y fue refutado).
  - La pestaña Code de la app de escritorio de Claude (Claude Code) requiere suscripción Pro, Max, Team o Enterprise. El plan gratis de claude.ai no la incluye; la pestaña Chat de la app no es paga. La CLI también funciona con una cuenta de Console (API, pago por uso) o con proveedores cloud. La app de escritorio usa inicio de sesión y no lee claves de API [22] (fuerte: documentación oficial, verificada).
  - En OpenAI, según chatgpt.com/pricing y la página de precios de Codex leídas el 28/9/2026, los planes Free y Go tienen acceso limitado a ChatGPT Work/Codex en la app de escritorio, sujeto a despliegue gradual. La web, la CLI, la extensión de IDE e iOS aparecen recién desde Plus [44] (media: páginas oficiales que cambian seguido; uno de los verificadores no pudo abrir chatgpt.com/pricing). La versión original decía lo contrario, que el escritorio estaba solo desde Plus. El error vino de leer una tabla cuyas columnas arrancan en Plus.
  - Claude Code for Everyone avisa que su curso gratis requiere Claude Pro o Max (desde USD 20 por mes) [17] (verificada).
- **La traba grande está en lo que rodea a la página** (media).
  - Karpathy armó MenuGen en local muy rápido, pero sintió que el "80% listo" era en realidad un 20%. Lo que costó fue la autenticación, el dominio y el DNS, las APIs, las variables de entorno que no llegaban a Vercel y los pagos con Stripe [38].
  - Entre 33 estudiantes con poca experiencia que hicieron una encuesta en un solo HTML, el obstáculo más citado fue conectarla con Google Sheets (15 menciones), antes que el HTML (7) y el prompting (6) [39].

### 4. Cómo publican

- **Todos los cursos relevados publican creando una cuenta en un hosting externo**: Vercel [1][7][9][11][17], Netlify [3][18], un VPS con dominio propio [4], GitHub [11], el dominio de Lovable [10] o Firebase/AI Studio [6] (media). Ninguna página de curso menciona la publicación integrada (artifacts de Claude o sitios de ChatGPT).
  - Aun así, la vía integrada aparece en la práctica. En la hackatón de la NYU, algunos participantes publicaron con el link de un artifact de Claude [26]. Y en el video de Cordero, cuando pidió "súbelo", la propia herramienta armó un artifact de claude.ai antes de que él la redirigiera a Vercel [1].
- **Los artifacts de Claude Code** (fuerte: documentación oficial; corregida: el link no nace público).
  - Publican una sola página autocontenida, sin backend propio, de hasta 16 MiB renderizada. La política de seguridad bloquea todas las imágenes externas, así que hay que embeberlas; sí se permiten Google Fonts y scripts de algunos CDN [21].
  - La página se publica en una URL de claude.ai que al principio solo ve su autor. Para compartirla hay que generar un link público desde Share, que cualquiera abre sin cuenta. En Pro y Max, ese link público es la única forma de compartir. En Team y Enterprise viene apagado hasta que un Owner lo habilita [21].
  - Requieren plan Pro, Max, Team o Enterprise y sesión iniciada con una cuenta de claude.ai: no funcionan con clave de API ni con Bedrock o Vertex. En la app de escritorio hace falta la versión 1.13576.0 o posterior [21].
  - Quien abre un link público sin sesión, o desde fuera de la organización, ve la leyenda "Content is user-generated and unverified." [21].
  - Según la investigación, cada publicación queda como versión en el mismo link y la función se lanzó en la semana del 15/6/2026 [21] (sin verificar).
- **Las vías "sin cuenta" ya casi no lo son** (media, corregida).
  - Según el blog de Netlify, los sitios subidos a Netlify Drop sin cuenta quedan protegidos con contraseña hasta que alguien los reclama (desde 2024), hay una hora para reclamarlos y un tope de 3 por IP (desde 2022), y los que no se reclaman se suspenden y se borran una semana después (desde 2025). El post no dice que esas reglas se hayan revertido. La documentación oficial solo corrobora la ventana de una hora [40].
  - Por separado, Netlify informa que más del 60% de quienes se registraron en junio de 2026 hicieron su primer deploy por la vía de arrastrar y soltar. Es una métrica interna, no auditada, y esa vía comparte infraestructura con los deploys que hacen agentes y constructores de IA, así que no todo es gente arrastrando una carpeta [40].
  - GitHub Pages pide cuenta, un repo público en el plan gratis y 7 pasos, y puede tardar hasta 10 minutos. Vercel ofrece "claim deployments" para agentes, con un código válido por 24 horas [41] (media).
- **Publicar es sacar una foto.** Lovable avisa que el sitio publicado no se actualiza solo: después de cada cambio hay que volver a publicar [16] (media).
- **Codex:** no se pudo confirmar si tiene un equivalente a los artifacts. Su documentación de escritorio hoy redirige a la de la app de escritorio de ChatGPT [22] (débil).

### 5. Forma de pensar y método de trabajo

- **"Mentalidad" se usa en claves distintas, y ninguna tiene que ver con el miedo del principiante** (media, corregida: no es "casi siempre" en clave de negocio).
  - En clave de negocio o de lanzamiento: EducaciónIT tiene una unidad de negocio y mindset del consultor IA [7], y aprendevibecoding propone pensar como un indie hacker y lanzar sin perfeccionismo [11].
  - En clave de compromiso: Cordero pide mirar el curso como si lo hubieras pagado, para terminarlo [1].
  - Sin una clave definida: la Escuela de VibeCoding abre con "el mindset del VibeCoder" [9].
- **Los ciclos que declaran los cursos no tienen un paso llamado predicción, pero escribir lo esperado antes del pedido sí aparece, como especificación para la IA** (media; la versión original, que decía que ningún temario pide anotar lo esperado, fue refutada).
  - Ciclos declarados: la Escuela de VibeCoding enseña describir, generar, revisar e iterar [9]. El método oficial de Platzi es dirigir con un prompt claro, revisar el resultado y mejorar con evidencia; la fórmula "dirigir, revisar, corregir y conectar piezas" es una respuesta del profesor en los comentarios, no parte del temario [6]. Cordero, en Codex, usa pedir, revisar y corregir [2] (sin verificar).
  - Platzi incluye un campo de "resultado esperado" dentro del prompt y define el caso de uso como situación, acción y resultado esperado. En la clase de pruebas con Codex pide anotar el resultado esperado, el resultado encontrado, la evidencia y un veredicto de pasa o falla [6].
  - Medina usa desde el minuto 21 la idea de "condición de parada". Hacia 1:02 pide definir criterios de éxito e iterar hasta verificarlos, y hacia las 2 h arma "el contrato" antes de ejecutar: objetivo, alcance, referencias, supuestos y qué cuenta como fracaso. También habla de la distancia entre lo que uno espera y lo que recibe [3].
  - Lo que no apareció en ningún curso revisado es la predicción como ejercicio del alumno: anotar qué cree que va a pasar para calibrar su propio modelo mental, no para instruir a la IA. No se pudo verificar cuántos temarios se revisaron en total (el borrador hablaba de unos 14).
  - En inglés, lo más cercano son la consigna de Replit de arrancar por lo que tiene que ser cierto cuando la app funciona [14], la regla de Lovable de hacer un cambio y revisar [16] y el loop de descripción y discernimiento de AI Fluency [12] (media).
- **Primero principios, después construir.** Vibe Coding 101 abre con 18 minutos de principios de desarrollo agéntico y resume cinco habilidades: pensamiento procedural, conocer frameworks, checkpoints, debugging sistemático y contexto selectivo [14] (media). Lovable enseña cinco principios de prompting, entre ellos saber qué construís antes de pedir y avanzar de a una pieza [16] (media).
- **Pero la charla inicial se saltea.** En el curso de Cordero, los primeros 15 minutos (bienvenida, mapa, "las dos reglas" y pedido de compromiso) tienen reproducción casi nula en el mapa de YouTube, de 0,00 a 0,05 [1] (débil: es un dato relativo, el público es emprendedor y el mapa muestra que se saltea, no por qué).
- **Saber escribir es una ventaja.** En un estudio preregistrado con 100 estudiantes terciarios, la escritura predijo el desempeño en vibe coding, igual que el rendimiento en computación, aun controlando las habilidades cognitivas generales [30] (media).
- **Los no desarrolladores verifican algo menos y abandonan más cuando no entienden, pero la diferencia es chica** (media, corregida: la versión original decía que "casi no verifican").
  - En una encuesta autorreportada a 162 vibe coders reclutados en Prolific (54 no desarrolladores, 54 novatos y 54 profesionales), los no desarrolladores fueron el único grupo en el que alguien dijo no chequear nunca el código generado: alrededor del 6% de ellos. La mitad dijo chequear a menudo o siempre [28].
  - Dijeron repetir el pedido en vez de depurar más que los profesionales, pero no más que los novatos. También dijeron abandonar la depuración por no entender el código más que los otros dos grupos [28].
  - Los efectos son chicos. En la regresión se explican mejor por el tiempo usando la herramienta y las horas de programación sin IA que por el grupo en sí [28].
  - Una revisión de 101 fuentes de práctica (518 relatos) describe la "trampa del novato", un loop de repedir y pegar. Hubo abandono en el 11% de los relatos de experiencia [29] (media).
  - En un estudio con Replit, los estudiantes de nivel inicial casi nunca miraban el código y sus pedidos venían sin contexto [43] (débil; citado de segunda mano).
- **Cómo se usa la IA se asocia con cuánto se aprende** (media, corregida: la relación entre patrones de uso y puntajes no es causal).
  - En un ensayo aleatorizado de Anthropic con 52 ingenieros que aprendían una librería nueva, mayormente juniors y con al menos un año de Python, el grupo con IA sacó 50% en un quiz inmediato contra 67% del grupo sin IA [23].
  - En un análisis cualitativo dentro del grupo con IA, con 2 a 7 personas por patrón, delegar todo el código o depurar pidiéndole arreglos a la IA se asoció a promedios por debajo de 40%. Pedir código con explicación, hacer preguntas de seguimiento o hacer solo preguntas conceptuales se asoció a 65% o más. Los autores aclaran que no establecen un vínculo causal y que no saben si el quiz predice el aprendizaje a largo plazo [23].
  - Son programadores con experiencia, así que aplicarlo a quien nunca programó es una inferencia.
  - En un preprint con 78 novatos, una "puerta de explicación" antes de aceptar código no cambió cuántos terminaban (alrededor del 90%). Pero al arreglar un bug sin IA falló el 39%, contra el 77% del grupo con IA libre. Costó unos 14 minutos extra y al 72% le pareció molesta al principio [31] (media; son novatos con algo de JavaScript).
- **Las fallas típicas son silenciosas.** En apps generadas con Claude, DeepSeek y Lovable a lo largo de 4 iteraciones aparecieron funciones que la interfaz anuncia pero que no hacen nada, reglas que se pierden y cambios que rompen lo que ya andaba. 11 de 23 fallas eran una relación rota entre una acción del usuario y un efecto visible [34] (débil; sin usuarios reales).
- **Las herramientas vienen hechas para actuar solas** (media).
  - En 500.000 interacciones de código, Claude Code fue 79% automatización, contra 49% en Claude.ai. HTML/CSS (28%) y JS/TS (31%) fueron los lenguajes más consultados [24].
  - Según la investigación, desde la v2.1.283 el modo por defecto en la terminal y en VS Code es auto: un clasificador aprueba las acciones por vos. La app de escritorio tiene modo Manual (muestra el diff y pide aprobar cada cambio) y modo Plan (propone sin editar) [20].
- **Los estilos de salida de Claude Code** (media). Explanatory agrega el porqué de cada cambio. Learning le pide al usuario que escriba partes del código (marcadas TODO(human)), así que no sirve para quien no programa. La documentación aclara que un estilo es una instrucción, no una garantía, y para lo que tiene que pasar siempre recomienda hooks [20].

### 6. Cuando se rompe y guardar versiones

- **El gesto estándar en español es la captura** (media). Medina, cuando falla un deploy, hace una captura, se la pasa a la IA y explica que no hace falta entender qué pasó [3]. Cordero marca como error más común dar por hecho que Claude terminó, y en su propio video termina publicando en una cuenta vieja de Vercel y tiene que corregir [1]. Platzi pone "depurar con prompts pequeños" temprano, en la clase 4, y presenta el versionado como lo que permite iterar sin miedo [6].
- **Volver atrás se enseña a mitad del curso y con herramientas técnicas** (media). Cordero ve checkpoints y rewind en el módulo 6 (1 h 31 min). Josema enseña Git y GitHub en el capítulo 9, y Medina ve Git a las 2 h 32 min. La Escuela de VibeCoding tiene un módulo 6 de control de versiones [1][3][4][9]. Claude Code for Everyone sube el código a GitHub en la lección 2.4, antes de publicar [17].
- **La red nativa de la herramienta no alcanza** (fuerte: documentación oficial, verificada).
  - El checkpointing de Claude Code guarda el estado antes de cada pedido que inicia un turno, y se vuelve con /rewind o apretando Esc dos veces. No registra los cambios hechos con comandos de terminal, borra las instantáneas alrededor de 30 días después de la última sesión (el plazo se puede ampliar) y la documentación dice que no reemplaza al control de versiones [20].
  - Otras limitaciones: guarda solo los últimos 100 checkpoints por sesión y, en general, no registra ediciones de subagentes, cambios manuales hechos fuera de Claude Code ni mensajes enviados a mitad de un turno [20].
  - La documentación de la app de escritorio no menciona /rewind ni los checkpoints, y avisa que los comandos que abren un diálogo de terminal se comportan distinto en la pestaña Code. Hay que probar /rewind ahí antes de enseñarlo [20].
  - Cordero reconoce en cámara que el rewind no siempre devuelve el archivo a su versión original [1] (débil).
- **Donde sí se presenta como red:** Lovable guarda cada edición como versión restaurable y presenta el historial como red de seguridad [16]. Replit trata los checkpoints como una habilidad central [14] (media).
- **Una regla útil de las buenas prácticas de Claude Code:** si corregiste lo mismo dos veces, conviene empezar de nuevo con un pedido mejor [20] (media).

### 7. Miedo, identidad e historia del autor

- **Ningún curso hispano revisado trata como tema el miedo del principiante a la herramienta**, es decir, el miedo a romper algo, a no entender o a equivocarse (media, corregida: el miedo sí es tema en el epílogo de Medina, aunque en otra clave). Aparece de estas formas:
  - como frase tranquilizadora al pasar, en Cordero y en Medina [1][3];
  - como miedo a gastar tokens, en Cordero (hacia 1 h 24 min) [1];
  - como algo que el versionado permite dejar atrás, en Platzi [6];
  - como presión para lanzar, en cursodevibecoding.com, que cierra diciendo que las ideas no valen nada si quedan en la cabeza [11];
  - como relato motivacional de emprendedor, en el epílogo de Medina (unos 15 minutos): el miedo a entregarle el primer proyecto a un cliente, la vergüenza de publicar videos y la idea de que las cosas se hacen con miedo y se entregan [3].
  - La página de Domestika no se pudo verificar [10].
- **En inglés tampoco aparece en las páginas públicas.** Lo más cercano es la lección de setup y mentalidad de Claude Code for Everyone, cuyo contenido no se pudo ver [17] (débil).
- **Identidad.** Build with Andrew cierra con una lección titulada "You're a builder now!" [15]. En el resto, el "ya sos developer" es una promesa de marketing, no contenido [14][17][18] (media).
- **Historia del autor.** El epílogo de Medina es lo más parecido a lo que quiere hacer el curso: largo, con vergüenza explícita y centrado en el miedo. Según la investigación, también cuenta su vida (lo echaron del colegio, trabajó en fábricas, pasó por una ruptura) y termina en éxito económico [3]. Pero está al final del curso y en clave de emprendedor. Cordero abre con credenciales y alcance [1]. Nadie reparte la historia en piezas cortas a lo largo del recorrido (débil).

### 8. Alcance: por qué una sola página

- **Seguridad.** Una auditoría revisó 200 apps desplegadas, sobre un total de 9.041 hechas con Claude Code y Lovable. El 91% tenía al menos una vulnerabilidad: 1.186 en total, 65,8% críticas o altas, sobre todo control de acceso roto, inyección y autenticación. Mejores prompts las reducen, pero no las eliminan [36] (media).
- En el showcase de Lovable, 170 de 1.645 proyectos (10,3%) tenían mal configurada la seguridad de su base de datos (CVE-2025-48757) [37] (media).
- GitHub Pages pide no usar sus sitios para contraseñas ni tarjetas [41]. Lovable recomienda dejar el login y la base de datos fuera de la primera versión [16] (media).

### 9. Formato siempre abierto y finalización

- **La baja finalización de los cursos abiertos es histórica y no mejoró** (fuerte para esa población, verificada). Con datos de Harvard y MIT en edX, la gran mayoría de los alumnos de MOOC nunca vuelve después de su primer año, y las bajas tasas de finalización no mejoraron en seis años [42]. Tres cuidados: los datos cubren de 2012 a 2018; "no vuelve" quiere decir que no se inscribe en otro curso al año siguiente, no que abandona el que está haciendo; y es una población de cursos masivos, gratuitos y sin acompañamiento, en la que muchos inscriptos nunca pensaron terminar [42].
- **Los propios autores gratuitos lo admiten.** Cordero pide tomar su curso como si lo hubieras pagado, porque según sus números casi nadie termina sin ese compromiso. En su video, las repeticiones caen a 0,03-0,33 en la última hora [1] (débil).
- **Los programas para no programadores con mejores condiciones tienen fecha o acompañamiento**: Stanford Continuing Studies (5 semanas con clases en vivo), el taller GAIDE (8 semanas con mentores) y la hackatón de un día de Brasil [25][43] (débil; lo de Stanford y GAIDE es de segunda mano).

### 10. El antecedente más cercano

- **Claude Code for Everyone, de Carl Vellotti** (media, corregida en la secuencia; es la descripción del propio autor, no una evaluación independiente, y el curso no está afiliado a Anthropic):
  - Es gratuito y es para gente sin experiencia en código ni en terminal. Corre principalmente dentro de la app de escritorio de Claude, con Claude como tutor que guía cada lección. Requiere Claude Pro o Max (desde USD 20 por mes) [17].
  - Según la investigación, el módulo 1 (unas 3 h) cubre fundamentos: archivos, agentes y memoria CLAUDE.md [17] (sin verificar).
  - En el módulo de vibe coding, la lección 2.2 planifica con una entrevista que arma un documento de requisitos. La 2.3 construye una app predefinida, un quiz de personalidad cuyas preguntas y resultados define el alumno. La 2.4 sube el código a un repositorio de GitHub y da por hecho que ya tenés cuenta. La 2.5, la última, publica en Vercel con la herramienta de línea de comandos de Vercel, conectada a ese repositorio [17].
  - Su sección de problemas admite que pueden hacer falta Node.js y la herramienta de línea de comandos de GitHub [17].
- **Tensión:** un investigador afirmaba que ningún curso ofrece un tutor que acompañe el proyecto de cada alumno. Eso vale para la oferta hispana. Claude Code for Everyone ya usa la herramienta como tutor, aunque con un proyecto fijo.

## Qué confirma y qué cuestiona del diseño actual

**Primera victoria temprana: se sostiene, pero ya no diferencia.**
- El mercado ya la adoptó: los cursos gratis hispanos revisados publican cerca de la primera hora [1][3] y Build with Andrew lo logra en menos de 30 minutos sin instalar nada [15]. Lo que diferencia es que sea con la idea propia.
- En el diseño, la primera victoria llega en el módulo 4, después de mentalidad, idea e instalación. La evidencia de que la instalación sea el peor momento es débil [1][35], pero la fricción alrededor de la publicación está mejor documentada [38][39][40]. Los investigadores leían distinto este orden. La síntesis razonable es sumar una micro-victoria visible en la web del curso (un borrador de cómo se vería la página de la idea, en el módulo 1 o 2) y dejar la primera publicación real en el módulo 4.
- La victoria sola no garantiza autonomía. Puede bajar algo el estrés [33], pero en un estudio chico varios estudiantes con dificultades terminaron con ilusión de competencia [32].

**Predecir antes de pedir: se sostiene como diferencial, pero más angosto y con evidencia solo indirecta.**
- Escribir lo esperado antes de pedir ya existe en el mercado como especificación para la IA: el campo de resultado esperado de Platzi y el "contrato" de Medina [6][3]. Platzi incluso enseña a comparar el resultado esperado con el encontrado al probar [6]. El curso no puede presentarlo como algo que nadie hace.
- Lo que sí es propio: que el alumno prediga para calibrar su propio modelo mental, en cada pedido, y después compare. Eso no apareció en ningún curso revisado.
- A favor, de forma indirecta y modesta: los no desarrolladores reportan abandonar más la depuración cuando no entienden y repetir pedidos más que los profesionales, aunque con efectos chicos [28]. Pedir explicaciones se asoció, sin causalidad probada, con mejores puntajes [23]. Una puerta de explicación redujo a la mitad las fallas al arreglar sin IA [31]. Y las fallas típicas son una acción que no produce el efecto visible esperado [34], justo lo que una predicción concreta detecta.
- Matiz: todas las muestras son de estudiantes, programadores o chicos, y la fricción cuesta tiempo y molesta al principio (al 72%) [31]. La forma importa: una línea por pedido, concreta, presentada como juego y no como examen.

**Un paso por vez: se sostiene.** Lovable lo pone como regla central [16] y Replit enseña el pensamiento procedural [14]. El loop de repedir y pegar [29] y el abandono cuando no se entiende [28] son justo lo que esta regla previene. Se puede concretar con la regla de "dos correcciones y empezar de nuevo" [20].

**El tutor explica antes de actuar: se sostiene, pero no viene de fábrica.**
- La evidencia sobre aprendizaje lo respalda, aunque sin causalidad probada y con programadores [23][31].
- Pero las herramientas empujan a automatizar [24], el modo por defecto en la terminal y en VS Code es auto, y un estilo de salida es una instrucción, no una garantía [20].
- Hay que configurarlo a propósito en el kit: modo Manual o Plan, un estilo propio y hooks para lo que tiene que pasar siempre. El estilo Learning no sirve para este público [20].

**Guardar versiones como red de seguridad: se sostiene como práctica, pero la evidencia contradice presentarla recién en el módulo 6.**
- Replit y Lovable la tratan como algo central [14][16].
- El rewind nativo no registra todo, vence y no reemplaza a git; ni siquiera está documentado para la app de escritorio [20]. El mercado la enseña tarde y con Git [1][3][4][9].
- Tiene que activarse con la primera publicación del módulo 4, con guardados con nombre que haga el tutor.

**El miedo tratado como tema: el hueco está confirmado; lo que se cuestiona es el formato de charla.**
- Ningún curso revisado trata el miedo del principiante a la herramienta [1][3][6][11].
- El antecedente más cercano, el epílogo de Medina, lo trata al final, largo y en clave de emprendedor [3]. El tono dominante del mercado es de presión para lanzar [11], que probablemente espante a la tribu.
- El riesgo es que una introducción de "mentalidad" se saltee [1] (débil).
- Los estudiantes no técnicos arrancaron intimidados y terminaron entusiasmados cuando hicieron algo [35], lo que sugiere tratar el miedo haciendo, no solo hablando.
- No hay evidencia de que trabajar el miedo como contenido mejore la finalización.

**La idea propia como hilo de todo el curso: es un diferencial real, con matices en la entrada.**
- Los cursos de gran alcance no lo hacen [1][14][15][17][18]. Las excepciones son parciales (el Blueprint de Lovable [16], Codecademy [19], las preguntas propias del quiz de Claude Code for Everyone [17]) o son cursos pagos y chicos [11][9].
- Riesgos: en una hackatón con estudiantes, los equipos convergieron temprano en una idea [25], y con un solo ejemplo una participante lo copió [26]. Ninguno de los dos estudios es con el público del curso.
- **Tensión entre investigadores:** uno proponía mostrar primero un ejemplo resuelto de otra persona de la tribu; otro advertía que un único ejemplo funciona como molde. La síntesis es mostrar varios ejemplos cortos y bien distintos, y abrir 2 o 3 variantes antes de achicar.
- La demanda de lo expresivo no está probada [10].

**Audios cortos del autor: respaldo débil, sin evidencia en contra.**
- La vulnerabilidad del autor ya se usa en el mercado hispano: el epílogo de Medina habla de miedo y vergüenza, pero al final del curso y con un cierre de éxito económico [3].
- Repartirla en piezas cortas pegadas a cada miedo no tiene antecedentes, ni a favor ni en contra.

**Curso siempre abierto, sin fechas ni vivos: es la decisión que más cuestiona la evidencia.**
- La baja finalización de los cursos abiertos es robusta y no mejoró [42]. Los autores gratuitos lo admiten [1], y los cursos pagos se apoyan en cohortes, vivos o mentoría [7][8][9][11].
- Atenuantes: los datos de MOOC son de 2012 a 2018 y de otra población [42], y la meta (una página publicada) es mucho más corta que un MOOC.
- No invalida el formato, pero obliga a compensarlo.

**Otras decisiones que salen de la evidencia:**
- **Una sola página, sin login, pagos ni datos compartidos: confirmada.** Por seguridad [36][37], por fricción [38][39] y porque lo recomiendan las plataformas [16]. Además, es un hueco frente a los cursos que prometen CRMs y apps con pagos [6][7][8][11].
- **Curso gratis: choca con el costo de Claude Code, no necesariamente con el de Codex.** Claude Code y sus artifacts exigen plan pago [22][21]. Codex tiene acceso limitado en el plan gratis, sujeto a despliegue [44], pero no sabemos si alcanza para el recorrido completo. Hay que decirlo de entrada y probar el camino gratis.
- **"Las herramientas son el medio, no el tema": se sostiene, con un matiz.** Saber de computación sigue prediciendo el desempeño [30], así que hace falta un mínimo de modelos mentales, entre el extremo académico [8] y el "un proyecto es una carpeta" de Cordero [1].

## Implicancias para el curso

**Transversal**
- Medir la finalización desde el día uno, por módulo, y registrar en qué paso abandonan. Los candidatos son la instalación, el pago y la publicación [1][22][40][42].
- Compensar la falta de fechas [42]:
  - un tutor que retome donde quedaste;
  - una meta chica por sesión;
  - el cuaderno como registro visible del avance;
  - recordatorios opcionales;
  - una galería de páginas publicadas por la tribu;
  - quizás una cohorte mensual optativa, sin vivos obligatorios.
- Decidir un camino principal de publicación por herramienta y dejarlo probado antes de grabar [21][40][41].
- Poner fecha a todo dato de precios y planes que aparezca en el curso, porque esas páginas cambian seguido [44].

**Módulo 1: cómo piensa un vibe coder**
- Que sea algo para hacer y no una charla, y que termine con un gesto concreto, como anotar la idea en una línea [1].
- Si se puede, una micro-victoria visible: que el tutor web muestre un primer borrador de cómo podría verse la página de la idea [15].
- Tratar el miedo del principiante a la herramienta con ejemplos y con el primer audio del autor, sin el tono de presión del mercado [3][11].
- Decir el costo de entrada, con fecha: Claude Code exige un plan pago (desde Pro) [22]; Codex tiene un acceso gratis limitado en la app de escritorio, sujeto a despliegue [44].
- Decir por qué el curso se queda en una sola página, para que no parezca poco al lado de cursos que prometen apps con pagos [6][36].
- Vocabulario puente: describir y discernir, del marco de AI Fluency [12]. Remarcar que saber escribir es una ventaja real para la tribu [30].

**Módulo 2: tu idea en una página**
- Antes de achicar, abrir 2 o 3 variantes de la idea [25][26].
- Si se muestran ejemplos, que sean varios y bien distintos, nunca uno solo [26]. Mezclar lo íntimo con lo útil, porque no está probado qué mueve a la tribu [10].
- Ubicar la idea en una forma que la IA resuelve bien en un solo archivo: página personal, herramienta chica, registro personal, quiz o guía [26][27].
- Si la forma es un registro local, avisar que cada visitante ve sus propios datos [27].
- Detectar los pedidos que se salen del alcance (que la gente se registre, que las respuestas lleguen a una planilla) y redirigirlos a una versión sin backend, por ejemplo un botón que abre un mail o un WhatsApp con el texto armado [38][39].
- Cerrar definiendo la versión mínima garantizada (un título más una frase de la idea) que se publica sí o sí en el módulo 4.

**Módulo 3: tu taller**
- Elección guiada entre Claude Code y Codex, algo que no existe en español [1][2]. Poner el costo como criterio explícito: Claude pide plan pago y tiene la vía de publicación integrada documentada [22][21]; Codex tiene una puerta gratis limitada, pero no confirmamos cómo se publica desde ahí [44][22]. Insistir en elegir una herramienta y quedarse con ella [18].
- Instalación acompañada, con capturas por sistema operativo. Anticipar Git en Windows [22][35] y la posibilidad de que la herramienta tenga que instalar otras piezas por detrás [17].
- Una mini lección sobre "tu carpeta del proyecto": dónde vive, cómo encontrarla, por qué no moverla [35].
- Tres o cuatro modelos mentales mínimos, dados justo cuando hacen falta [1][8][30]: tu página es una carpeta; el link es esa carpeta publicada; una versión es una foto de la carpeta; publicar es sacar otra foto.
- Resolver acá la cuenta y el plan. En Claude, los artifacts piden sesión iniciada con cuenta de claude.ai y la app de escritorio actualizada [21]. Si se usa un hosting externo, crear la cuenta acá, para que el módulo 4 no se trabe en un formulario ni en una ventana de una hora que vence [40][41].

**Módulo 4: primera victoria**
- Publicar la versión mínima de la idea propia en la primera sesión [1][15].
- Con Claude Code, publicar como artifact y preparar al alumno para cuatro cosas [21]:
  - que la página nace privada y que compartirla con el link público de Share es una decisión consciente;
  - la leyenda de contenido no verificado que ve quien abre el link sin sesión, para que no la viva como un error;
  - que las imágenes propias hay que pedir que se embeban;
  - la diferencia entre la versión compartida y la versión de trabajo.
- Explicar que después de cada cambio hay que volver a publicar [16].
- El kit arranca en modo Manual o Plan y con un estilo de salida propio que explica en castellano llano qué va a hacer y por qué [20].
- Primer guardado con nombre apenas se publica, por ejemplo "versión que funciona 1", sin depender de /rewind, que además hay que probar en la app de escritorio [20].
- Cerrar con una reflexión de tres preguntas: qué pediste, qué esperabas y qué pasó [32].

**Módulo 5: construir**
- Un cambio por vez, y mirar el resultado [16][29].
- Cuaderno de predicción liviano: una línea, "si hago X, debería ver Y", concreta (qué botón, qué texto, cómo se ve en el celular) [34]. Se puede tomar el formato de pruebas de Platzi (esperado, encontrado, veredicto) [6], con una diferencia a propósito: la predicción es del alumno sobre lo que cree que va a pasar, no una instrucción para la IA.
- Después de cada cambio, releer 2 o 3 predicciones viejas para detectar lo que se rompió sin avisar [34].
- Presentar funciones de la herramienta solo cuando el proyecto las pide, al revés que el mercado [1][18].
- Guardado con nombre después de cada logro.
- Cuidar la fricción: las puertas de explicación molestan al principio [31].

**Módulo 6: cuando se rompe**
- Incluir el gesto del mercado (captura más descripción) [3] y sumarle una capa propia: qué esperabas, qué viste y qué te dice la diferencia [28].
- Regla del kit: si el alumno repite el mismo pedido o corrige lo mismo dos veces, el tutor frena, propone volver a la última versión que andaba y pedir algo más chico [20][29].
- Chequear que la tarea de verdad terminó y que se publicó donde tenía que publicarse [1].
- Medir si el alumno puede recuperarse de un error, no solo si publicó [32].

**Módulo 7: terminar y mostrar**
- Una charla breve sobre qué no poner en la página: claves, contraseñas y datos personales de otros [36][41].
- Explicar por qué el curso no incluye login ni pagos, y cuál es el camino para quien quiera seguir [36][38].
- Un mensaje de identidad de cierre, del tipo "ya sos alguien que hace cosas" [15].
- Un audio del autor sobre la vergüenza de mostrar. El antecedente es el epílogo de Medina, pero acá corto y sin la clave de éxito económico [3].
- Sumar la página a una galería de la tribu, como compensación del formato siempre abierto [42].

## Lo que no sabemos

- **Finalización:** no hay datos públicos de cuántos terminan ningún curso gratis de vibe coding. El mapa de YouTube es relativo, no una curva de retención, y sus picos pueden reflejar saltos desde el índice [1].
- **Dónde se traban de verdad:** la idea de que la instalación es el peor momento quedó debilitada. El pico del mapa no prueba dificultad y el comentario citado habla de un camino opcional [1]. El dato de MoureDev no tiene URL [5].
- **Predecir antes de pedir:** no hay evidencia directa de que funcione con adultos no programadores, ni de cuánto lo saltean. Todos los estudios son con estudiantes de programación, programadores o chicos [23][28][31]. Tampoco se revisó la literatura de predecir-observar-explicar ni la de metacognición, y no se pudo verificar cuántos temarios se revisaron en total.
- **Tiempo real:** no hay datos de cuánto tarda un adulto no técnico de 30 a 60 años, con apps de escritorio y sin terminal, desde que instala hasta que publica por primera vez.
- **Ejemplo resuelto o idea propia desde el principio:** la literatura de carga cognitiva sobre ejemplos resueltos podría cuestionar que se arranque con una idea abierta. No se verificó. La evidencia de convergencia prematura viene de estudiantes mayormente de computación [25].
- **Qué mueve a la tribu:** lo expresivo e íntimo, o también lo útil o económico. La baja tracción de Domestika es ambigua y su página no se pudo verificar [10]. Hay que validarlo con entrevistas antes de fijar los ejemplos del módulo 2.
- **Codex:**
  - si el acceso limitado del plan gratis en la app de escritorio alcanza para construir una página, qué quiere decir "limitado" y para quién está desplegado [44];
  - si tiene un equivalente a los artifacts y cómo se publica desde la app de escritorio [22];
  - cómo se comparten hoy los sitios o canvas de ChatGPT.
- **Modo por defecto y rewind en la app de escritorio de Claude Code:** está documentado el modo de la terminal y de VS Code (auto), no el del escritorio, y la documentación de escritorio no menciona /rewind [20].
- **Costo real para la tribu:** qué proporción puede o quiere pagar Pro o Plus, y si el camino gratis de Codex es viable aunque sea más torpe.
- **La leyenda de contenido no verificado:** no sabemos cómo la perciben el alumno y quien recibe el link [21].
- **Contenido interno de las lecciones cercanas al miedo:** no se pudo ver la lección de setup y mentalidad de Claude Code for Everyone ni el interior de Build with Andrew [15][17].
- **Audios del autor:** no hay evidencia sobre su efecto.
- **Cursos que no se buscaron:** hispanos para mayores de 50 o para mujeres, talleres de fundaciones (Telefónica, Laboratoria), los cursos propios de Replit, la oferta de Google y Gemini, cohortes en Maven, y Stanford Continuing Studies (solo citado de segunda mano).
- **Datos sueltos pendientes:**
  - la fecha de lanzamiento de Platzi;
  - el precio de Domestika;
  - la duración de Fuggini (3 o 4 semanas);
  - la segunda de "las dos reglas" de Cordero;
  - la fecha de Build with Andrew (un investigador no vio fecha y otro registra 2026-01-07);
  - si Cordero y Medina están de verdad entre los cursos más vistos.
- **Límite del método:** los tres investigadores agotaron el cupo de búsquedas y trabajaron en buena parte abriendo URLs directas. Varias fuentes quedaron sin URL registrada, y solo las 15 afirmaciones clave pasaron por la verificación adversarial.

## Fuentes

Formato: autor u organización. Título. Fecha. Tipo. URL. Estado. "Verificada" quiere decir que los verificadores leyeron la fuente y confirmaron lo que se le atribuye; "parcial", que la leyeron y hubo que corregir o acotar lo que se le atribuía; "sin verificar", que no pasó por la verificación adversarial.

1. Benjamín Cordero (Imperio Agéntico). *CLAUDE CODE 2026: Curso Completo en Español (actualizado)*: descripción, transcripción automática, mapa de "lo más repetido" y comentarios (extraídos el 2026-09-28). 2026-07-31. Curso y datos de plataforma. https://www.youtube.com/watch?v=h49d1-d_fYk . **Parcial:** se confirman las vistas, la fecha, la publicación entre los minutos 59 y 62 y el ejemplo inventado. Los "dos prompts" fueron al menos cuatro pedidos; el comentario sobre Git no es el más votado (es el tercero) y habla del camino opcional por VS Code; el pico del mapa en la instalación existe, pero no prueba dificultad. El resto de los datos de esta fuente (checkpoints en el módulo 6, rewind, primeros 15 minutos, última hora) está sin verificar.
2. Benjamín Cordero. *CODEX 2026: Curso Completo en Español*, más la página "about" de Imperio Agéntico en Skool (URL no registrada). 2026-09-17. Curso y datos de plataforma. https://www.youtube.com/watch?v=XcUOWCXP5u8 . **Sin verificar.**
3. Agustín Medina (AI Agency Academy / AILINK). *Claude Code 2026: Curso Completo (7 Horas) Sin Programar*: capítulos y transcripción. 2026-09-20. Curso. https://www.youtube.com/watch?v=w_pyNNAnoAc . **Parcial:** la publicación es hacia el minuto 34 (el 24 es el inicio del capítulo) y el ejemplo es una colchonería, no una clínica dental. El epílogo trata el miedo como tema en clave emprendedora. Se confirmaron la condición de parada, los criterios de éxito y "el contrato".
4. Josema Fernández. *Curso COMPLETO de ChatGPT Codex 2026: De Cero a Experto*. 2026-08-20. Curso. https://www.youtube.com/watch?v=H3c_-f2OJu0 . **Sin verificar.**
5. MoureDev. Curso de Claude Code (3 h) y su mapa de reproducciones. 2026-08-13. Curso. URL no registrada. **Sin verificar** (sin URL).
6. Rafael Andrés Herrera (Platzi). *Curso de Vibe Coding para Crear Apps sin Programar*. Sin fecha visible (consultado el 2026-09-28). Curso. https://platzi.com/cursos/vibecoding/ ; lecciones: https://platzi.com/cursos/vibecoding/crea-apps-sin-codigo-con-google-ai-studi/ , https://platzi.com/cursos/vibecoding/disena-el-dia-cero-de-tu-app-con-ia/ y https://platzi.com/cursos/vibecoding/prueba-tu-app-con-un-agente-de-codex/ . **Parcial:** el método oficial es dirigir, revisar y mejorar con evidencia (la fórmula de cuatro pasos es un comentario del profesor). Se confirmaron el campo de resultado esperado, la prueba de lo esperado contra lo encontrado, "iterar sin miedo" y el orden por capas de un proyecto. El resto (cantidad de clases, publicación en la clase 11, depuración en la clase 4) está sin verificar.
7. EducaciónIT. Curso de vibe coding: página y plan de estudios (PDF). Sin fecha. Curso. https://www.educacionit.com/curso-de-vibe-coding (la URL del PDF no se registró). **Parcial:** se confirmó el módulo "Negocio y mindset del consultor IA"; la duración, los grupos y el resto del temario están sin verificar.
8. Universidad del Rosario, Educación Continua. *Vibe Coding - Programa sin ser Programador*. 2026 (inicio 20/4/2026). Curso. https://educacioncontinua.urosario.edu.co/escuela-ingenieria-ciencia-tecnologia/curso/programacion-para-no-programadores . **Sin verificar.**
9. Óscar de la Torre. *Escuela de VibeCoding — Madrid 2026* (temario). 2026 (próxima edición 23/10/2026). Curso. https://escueladevibecoding.com/ . **Parcial:** se confirmaron el ciclo describir, generar, revisar e iterar (módulo 03) y el módulo de mindset, cuya clave no es claramente empresarial. El resto está sin verificar.
10. Ramón Iborra (Domestika). *VibeCoding: Crea tus propias Mini-Herramientas Creativas*. Sin fecha visible. Curso. https://www.domestika.org/es/courses/6434-vibecoding-crea-tus-propias-mini-herramientas-creativas . **Sin verificar** (los verificadores no pudieron abrir la página).
11. Páginas de cursos hispanos: aprendevibecoding.com (https://aprendevibecoding.com/), cursodevibecoding.com (https://cursodevibecoding.com/), Fuggini (landing) y NocodeHackers (URLs no registradas; el subdominio de Fuggini no respondió). Consultadas el 2026-09-28. Curso. **Parcial:** se confirmaron la "mentalidad del vibe coder" en clave de indie hacker (aprendevibecoding) y el cierre con presión para lanzar (cursodevibecoding.com, no Fuggini). Fuggini y NocodeHackers, sin verificar.
12. Anthropic Academy. *Claude Code 101* (Coursera) y catálogo en anthropic.skilljar.com (AI Fluency: Framework & Foundations, AI Fluency for Builders, Claude Code in Action). Actualizado en 2026-09. Curso. https://www.coursera.org/learn/claude-code-101 . **Sin verificar.**
13. OpenAI Academy (Aaron Wilkowitz). *Codex for Beginners* (evento). 2026-04-21. Curso/webinar. https://academy.openai.com/public/events/codex-for-beginners-wsz3p1tg0r . **Sin verificar.**
14. Michele Catasta y Matt Palmer (DeepLearning.AI / Replit). *Vibe Coding 101 with Replit*. 2025-03-26. Curso. https://www.deeplearning.ai/courses/vibe-coding-101-with-replit . **Sin verificar** (coincidieron 2 investigadores).
15. Andrew Ng (DeepLearning.AI). *Build with Andrew*. 2026-01-07 según un investigador; sin fecha visible según otro. Curso. https://www.deeplearning.ai/courses/build-with-andrew/ y https://learn.deeplearning.ai/courses/build-with-andrew . **Sin verificar** (coincidieron 2 investigadores; la fecha está en tensión).
16. Lovable. *Docs: Quick start* y guía de prompting de Lovable Academy. Sin fecha visible. Oficial. https://docs.lovable.dev/introduction/getting-started . **Sin verificar** (coincidieron 2 investigadores).
17. Carl Vellotti. *Claude Code for Everyone* (incluye el módulo 2, Vibe Coding). © 2026, consultado el 2026-09-28. Curso de practicante. https://ccforeveryone.com/ ; https://ccforeveryone.com/vibe-coding ; https://ccforeveryone.com/vibe-coding/plan ; https://ccforeveryone.com/vibe-coding/github ; https://ccforeveryone.com/vibe-coding/go-live . **Parcial:** se confirmaron el público, la gratuidad, la app de escritorio como tutor, la entrevista, el quiz predefinido y el requisito de Pro o Max. Se corrigió la secuencia: GitHub en la 2.4 y Vercel con su CLI en la 2.5. Es la descripción del propio autor y el curso no está afiliado a Anthropic.
18. Scrimba (Per Harald Borgen, Guil Hernandez, Maham Codes). *Vibe Coding Essentials - Build Apps with AI Specialization* (Coursera). Consultado el 2026-09-28. Curso. https://www.coursera.org/specializations/vibe-coding . **Parcial:** se confirmaron los 22.143 inscriptos, el nivel principiante y los cuatro cursos por herramienta; se agregó el quinto curso, el más largo, armado por proyectos. Las reseñas están sin verificar.
19. Codecademy, *Intro to Vibe Coding*, y Microsoft Learn, módulo de vibe coding con GitHub Copilot (actualizado en jul-2026). Curso. URLs no registradas. **Sin verificar** (sin URL).
20. Anthropic. *Claude Code Docs*: Checkpointing, Output styles, Best practices, modos de permisos y app de escritorio. Consultado el 2026-09-28. Oficial. https://code.claude.com/docs/en/checkpointing ; https://code.claude.com/docs/en/output-styles ; https://code.claude.com/docs/en/desktop . **Verificada** en lo de checkpointing y en que la documentación de escritorio no menciona /rewind. Output styles, buenas prácticas y modos de permisos, sin verificar.
21. Anthropic. *Claude Code Docs: Share session output as artifacts*. Consultado el 2026-09-28. Oficial. https://code.claude.com/docs/en/artifacts . **Parcial:** se confirmaron los datos técnicos, los planes y la leyenda; se corrigió que el link nace privado y que compartir es un paso aparte. La fecha de lanzamiento y el versionado en el mismo link están sin verificar.
22. Anthropic. *Claude Code Docs: Get started with the desktop app* y *Set up Claude Code*. Consultado el 2026-09-28. Oficial. https://code.claude.com/docs/en/desktop-quickstart ; https://code.claude.com/docs/en/setup . **Verificada** en el requisito de plan pago y en la opción de Console para la CLI. Lo de Git y la carpeta de proyecto está sin verificar. La afirmación sobre Codex que se apoyaba en esta fuente fue refutada y reemplazada con [44].
23. Anthropic. *How AI assistance impacts the formation of coding skills* (paper: Shen y Tamkin, *How AI Impacts Skill Formation*). 2026-01-29. Investigación (ensayo aleatorizado). https://www.anthropic.com/research/AI-assistance-coding-skills ; https://arxiv.org/abs/2601.20245 . **Parcial:** las cifras se confirman; los participantes eran mayormente juniors, y la relación entre patrones de uso y puntajes no es causal (grupos de 2 a 7 personas).
24. Anthropic. *Anthropic Economic Index: AI's impact on software development*. 2025-04-28. Datos de plataforma. https://www.anthropic.com/research/impact-software-development . **Sin verificar.**
25. Gama, Calegario, Jackson, Nolte, Morais y Garcia. *"Can you feel the vibes?": An exploration of novice programmer engagement with vibe coding*. 2025-12-02. Paper (preprint). https://arxiv.org/abs/2512.02750 . **Parcial:** eran 9 equipos de experiencia mixta y mayoría de computación; la cifra es "cinco ideas o menos"; 19 de 27 consideraron su app funcional; la evidencia sobre la confianza es escasa.
26. Chen, Cao, Shao, Karri y Shafique (NYU). *Code for All: Educational Applications of the "Vibe Coding" Hackathon*. 2026-04-24. Paper (preprint). https://arxiv.org/html/2604.22747v1 . **Sin verificar.**
27. Simon Willison, *Useful patterns for building HTML tools* (2025-12-10), y MDN, documentación de localStorage. Practicante y referencia técnica. URLs no registradas. **Sin verificar** (sin URL).
28. Ahmed Fawzy, Amjed Tahir y Kelly Blincoe. *From Prompting to Verification: How Experience Shapes Vibe Coding Practices*. 2026-05-23. Paper (preprint). https://arxiv.org/abs/2605.24521 . **Parcial:** el "nunca chequea" es cerca del 6% de los no desarrolladores; repiten pedidos más que los profesionales pero no más que los novatos; los efectos son chicos y se explican mejor por la práctica; es autorreporte.
29. *Vibe Coding in Practice: a Grey Literature Review* (arXiv 2510.00328). 2025-09-30. Paper (revisión). https://arxiv.org/abs/2510.00328 (URL armada desde el identificador). **Sin verificar.**
30. Sverrir Thorgeirsson, Theo B. Weidmann y Zhendong Su. *Computer Science Achievement and Writing Skills Predict Vibe Coding Proficiency*. 2026-03-14. Paper (preregistrado). https://arxiv.org/abs/2603.14133 . **Sin verificar.**
31. *Mitigating "Epistemic Debt" in Generative AI-Scaffolded Novice Programming* (arXiv 2602.20206). 2026-03-31 (v2). Paper (preprint). https://arxiv.org/html/2602.20206v2 . **Sin verificar.**
32. Prather et al. *The Widening Gap* (ICER 2024). 2024-05-28. Paper. https://arxiv.org/abs/2405.17739 . **Parcial:** es un estudio cualitativo; la clasificación se hizo por conducta observada, y el ensanchamiento de la brecha es una hipótesis de los autores, no un resultado medido.
33. Kazemitabaar et al. *Studying the effect of AI Code Generators on Supporting Novice Learners* (CHI 2023). 2023. Paper. URL no registrada. **Sin verificar** (sin URL).
34. *FlowCheck: Helping End-Users Specify and Verify Intent in Vibe-Coded Web Apps* (arXiv 2608.28880). 2026-08-28. Paper (preprint). https://arxiv.org/html/2608.28880v1 . **Sin verificar.**
35. *Vibe coding before the trend* (arXiv 2605.07751). 2026-05-08. Paper (preprint). https://arxiv.org/html/2605.07751v1 . **Sin verificar.**
36. Junquan Deng, Zhiyu Fan y Ruijie Meng. *Understanding the (In)Security of Vibe-Coded Applications*. 2026-06-22 (revisado en 2026-09). Paper (preprint). https://arxiv.org/abs/2606.23130 . **Sin verificar** (coincidieron 2 investigadores).
37. Matt Palmer. *Statement on CVE-2025-48757*. 2025-05-29. Practicante. URL no registrada. **Sin verificar** (sin URL).
38. Andrej Karpathy. *Vibe coding MenuGen*. 2025-04-27. Practicante. https://karpathy.bearblog.dev/vibe-coding-menugen/ . **Sin verificar.**
39. *Feasibility of AI-Assisted Programming for End-User Development* (arXiv 2512.05666). 2025-12-05. Paper (preprint). https://arxiv.org/abs/2512.05666 (URL armada desde el identificador). **Sin verificar.**
40. Netlify (Gehrig Kunz). *Thirteen years of Netlify Drop*. 2026-07-27. Blog corporativo con datos de plataforma. https://www.netlify.com/blog/thirteen-years-of-netlify-drop/ ; documentación: https://docs.netlify.com/deploy/create-deploys/ . **Parcial:** las reglas antiabuso se confirman en el blog, y la documentación solo corrobora la hora para reclamar. El 60% es una métrica interna que no se puede leer como "a pesar de las trabas" y que incluye deploys hechos por agentes.
41. GitHub Docs, *Creating a GitHub Pages site*, y Vercel Docs, *Claim Deployments* (2026-08-21). Oficial. URLs no registradas. **Sin verificar** (sin URL).
42. Justin Reich y José A. Ruipérez-Valiente. *The MOOC pivot*. Science, 2019-01. Paper. DOI 10.1126/science.aav7958; resumen en https://api.semanticscholar.org/graph/v1/paper/DOI:10.1126/science.aav7958?fields=title,abstract,year,authors,venue . **Verificada** (datos de 2012 a 2018; "no vuelve" se refiere a volver a inscribirse).
43. Menciones de segunda mano: Stanford Continuing Studies (vía el comparativo de VibeCodeSource, mar-2026), el marco GAIDE (taller de 8 semanas con mentores) y Geng et al. 2025 (pensamiento en voz alta con Replit). Sin URL. **Sin verificar** (no se consultaron directamente).
44. OpenAI. Página de precios de ChatGPT y página de precios de Codex. Leídas el 2026-09-28. Oficial. https://chatgpt.com/pricing ; https://learn.chatgpt.com/docs/pricing (destino de https://developers.openai.com/codex/pricing) . **Verificada** por los dos verificadores de la afirmación sobre el costo (uno no pudo abrir chatgpt.com/pricing y se apoyó en la página de Codex). Son páginas que cambian seguido.
