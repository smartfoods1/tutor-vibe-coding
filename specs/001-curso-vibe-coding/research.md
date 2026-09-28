# Research: Curso gratuito de vibe coding para la tribu

**Fecha**: 2026-09-28 · **Plan**: [plan.md](plan.md)

Decisiones técnicas del plan, con los datos verificados que las sostienen. Los datos de
herramientas, planes y precios se consultaron en fuentes oficiales el 27 y el 28/9/2026; los que
se muestran a los alumnos pasan al machete con su fecha (Constitución IV). La investigación de
producto (planes de Claude y ChatGPT, dónde publicar, cursos en español) está en las notas del
autor (no incluidas).

## 1. Base de código: fork de un proyecto anterior del autor

- **Decision**: copiar el backend de un proyecto anterior del autor a `backend/vibe_tutor` y
  adaptarlo. Se conservan `auth`, `costos`, `db`, `voz`, `tutor`, `api`, `config` y `main` con sus
  tests, y se saca lo exclusivo de ese proyecto. El frontend se escribe de nuevo.
- **Rationale**: el núcleo del proyecto anterior ya resuelve el ciclo del tutor con streaming y
  manejo de errores, el login por código con límites, el registro de costos con tope y la voz, con
  cerca de 5.000 líneas de tests. Es lo más rápido y lo más probado.
- **Alternatives considered**: plataforma compartida entre el proyecto anterior y este curso (se
  descarta por la Constitución VI hasta que exista un tercer curso); empezar de cero (más lento y
  sin tests).

## 2. Modelo del tutor de la puerta

- **Decision**: `claude-sonnet-5` (elegido por Andrés el 27/9), con `thinking: {type: "adaptive"}`
  y `output_config.effort` en `low` para la conversación y `medium` cuando el tutor guarda la idea
  o cierra un módulo. Streaming como en el proyecto anterior. Sin el beta de respaldo ante rechazos
  (sus destinos son `claude-opus-5` y `claude-opus-4-8`) y sin compactación (cada módulo es una
  conversación corta). Un `stop_reason: "refusal"` se muestra con un mensaje amable, como en el
  proyecto anterior.
- **Rationale**: Sonnet 5 cuesta US$2 y US$10 por millón de tokens de entrada y de salida, y
  respeta el esfuerzo al pie de la letra en el nivel bajo, lo que controla el costo. La referencia
  oficial recomienda probar pensamiento adaptativo con esfuerzo bajo antes que apagarlo; con el
  pensamiento apagado, Sonnet 5 usa menos las herramientas.
- **Alternatives considered**: Opus 5 (unos US$0,90 por alumno), Haiku 4.5 (más
  barato y más flojo para la entrevista), pensamiento apagado (se mide en la prueba de costo; se
  adopta solo si el costo se pasa de la meta sin perder calidad).

## 3. Caché y estructura del prompt

- **Decision**: el prompt de sistema se arma en dos bloques fijos e iguales para todos los alumnos
  de un módulo: el prompt base (persona, reglas, protocolo de malestar) y la guía del módulo. Van
  primero y con caché. Lo propio de cada alumno (su idea, su resumen del módulo anterior, su
  herramienta y su sistema) va después del punto de caché, en el primer mensaje de la sesión.
- **Rationale**: en Sonnet 5 el mínimo cacheable es de 1.024 tokens; la escritura de 5 minutos
  cuesta 1,25 veces la entrada (US$2,50 por millón), la de 1 hora 2 veces (US$4) y la lectura 0,1
  vez (US$0,20). La caché se comparte dentro del workspace, así que un prefijo idéntico entre
  alumnos se mantiene caliente con el tráfico. Sin caché, el tutor pasa de unos US$0,19 a unos
  US$0,73 por alumno.
- **Alternatives considered**: prompt por alumno completo (rompe la caché), TTL de 1 hora (se
  evalúa con tráfico real; al principio alcanza con 5 minutos).

## 4. Capturas de pantalla

- **Decision**: el cliente achica la captura a 1.440 px en el lado largo antes de subirla; viaja
  como bloque `image` en base64 solo en la llamada en curso; en la base se guarda el texto
  "[captura de pantalla enviada]". Límite de 5 MB y formatos PNG, JPEG y WebP.
- **Rationale**: Claude cuenta ⌈ancho/28⌉ × ⌈alto/28⌉ tokens por imagen. Una captura de
  1.440 × 900 son 1.716 tokens (US$0,0034); una de pantalla Retina sin achicar se reescala y llega
  a 4.698 tokens. No guardar la imagen cumple FR-011 y la Constitución III.
- **Alternatives considered**: guardar la captura para mostrarla en el historial (descartado por
  privacidad), subirla sin achicar (hasta 2,7 veces más cara).

## 5. Voz

- **Decision**: se conserva el módulo de voz del proyecto anterior. Transcripción con
  `gemini-2.5-flash` (con el pensamiento apagado). Voz del tutor con
  `gemini-3.8-flash-tts`, o `gemini-3.8-flash-lite-tts` si la calidad alcanza en el piloto, con una
  voz de síntesis distinta de la de Andrés. **La voz del tutor viene apagada** y el alumno la
  prende con "Escuchar las respuestas"; el dictado sí está siempre disponible.
- **Rationale**: la voz del tutor es el costo más grande por alumno. Con `gemini-3.8-flash-tts`,
  10 minutos cuestan unos US$0,14 hasta el 31/12/2026 y US$0,27 desde el 1/1/2027 (se factura a 25
  tokens por segundo; US$9 por millón de tokens de audio, US$18 desde 2027). La versión lite cuesta
  US$6 y después US$12. Transcribir 5 minutos con `gemini-2.5-flash` cuesta unos US$0,01. Desde el
  18/9/2026 Google limita los modelos 2.5 a quienes ya los usaban: una clave nueva puede no tener
  acceso; en ese caso, usar `gemini-3.5-transcribe`. La tabla de precios en `costos.py` tiene fecha
  de vigencia para el cambio de enero.
- **Alternatives considered**: `gemini-3.5-transcribe` (GA desde el 26/8/2026, unos US$0,005 por
  minuto; queda como reemplazo si Google corta el acceso a 2.5), voz del tutor siempre prendida
  (más cara y menos cómoda en público).

## 6. Frontend

- **Decision**: React 19 + Vite + TypeScript + Tailwind 4, como PWA. El chat lee eventos SSE; el
  micrófono usa MediaRecorder; la captura se achica en el navegador con un canvas antes de subir.
  Diseño pensado primero para el celular.
- **Rationale**: es el stack que el autor ya usó en otros proyectos, incluido el proyecto anterior,
  donde resolvió chat con streaming, micrófono y audio en el celular. El autor ya lo conoce.
- **Alternatives considered**: HTML renderizado en el servidor con HTMX (menos piezas, pero el
  streaming, la grabación de audio y el estado del chat quedan más frágiles).

## 7. Inscripción y antiabuso

- **Decision**: el login por código del proyecto anterior, abierto a cualquier mail, con Cloudflare Turnstile
  en el pedido del código (se valida en el servidor con `siteverify`, chequeando `hostname` y
  `action`), 5 códigos por mail por hora y 20 por IP por hora. Los consentimientos se aplican
  recién al verificar. El admin es el mail de `ADMIN_EMAIL`.
- **Rationale**: Turnstile es gratis (challenges ilimitados, hasta 20 widgets y 10 hostnames por
  widget) y funciona aunque el sitio se sirva desde el servidor sin pasar por el proxy de Cloudflare. El
  token dura 300 segundos y es de un solo uso. Resend advierte que los ataques al formulario de
  alta queman la reputación del dominio con rebotes; Turnstile más los límites cubren ese riesgo.
- **Alternatives considered**: solo límites por IP (no frena bots distribuidos), hCaptcha (sin
  ventaja frente a Turnstile).

## 8. Mails

- **Decision**: Resend con llamadas HTTP directas (como el proyecto anterior, sin sumar el SDK), desde un
  subdominio propio verificado. Cada mail del curso lleva `List-Unsubscribe` y
  `List-Unsubscribe-Post: List-Unsubscribe=One-Click`; el endpoint de baja acepta POST y da la baja
  al instante. Arranca en el plan gratis y pasa al Pro (US$20 por mes) antes del lanzamiento.
- **Rationale**: el plan gratis tiene 3.000 mails por mes y **100 por día**, y cada código de
  acceso cuenta. Un día de lanzamiento con más de 50 inscripciones lo agota (código + bienvenida).
  Resend no agrega solo las cabeceras de baja en los mails transaccionales: hay que mandarlas.
  Recomienda un subdominio para aislar la reputación.
- **Alternatives considered**: Broadcasts de Resend (maneja bajas, pero no dispara por avance del
  alumno), una herramienta de mail aparte (descartada por Andrés el 27/9).

## 9. Lista y novedades

- **Decision**: la base del curso es la lista maestra. `/api/admin/novedades.csv` exporta una sola
  columna de mails, solo de quienes aceptaron recibir las novedades del autor (consentimiento
  `novedades`); el autor la importa a mano en su plataforma de newsletter, que se nombra en la
  configuración (`NEWSLETTER_NOMBRE`). Si `NEWSLETTER_NOMBRE` está vacío, la casilla no se muestra
  y el consentimiento queda en 0. La migración 3 renombra el consentimiento que usaba la primera
  versión.
- **Rationale**: la plataforma de newsletter del autor importa CSV con mails y no importa nombres;
  pide confirmar que cada persona dio su consentimiento explícito, y las listas sin consentimiento
  pueden hacer que restrinjan la publicación. No tiene API oficial para sumar suscriptores (la de
  2026 solo lee datos públicos).
- **Alternatives considered**: sumar a todos los inscriptos a la newsletter (viola el
  consentimiento separado del spec y arriesga la cuenta).

## 10. Costo por alumno (estimación)

Supuestos: 40 respuestas del tutor en los módulos 1 a 3, prompt de sistema de unos 6.000 tokens
con caché, 300 tokens de salida por respuesta, 2 capturas, 10 minutos de voz del tutor, 5 minutos
de dictado y 4 mails.

| Ítem | US$ |
|---|---|
| Tutor (Sonnet 5, con caché) | 0,19 a 0,29 |
| 2 capturas | 0,01 a 0,02 |
| Voz del tutor, 10 min (`gemini-3.8-flash-tts`) | 0,14 (0,27 desde 2027) |
| Dictado, 5 min | 0,01 a 0,03 |
| Mails | 0 (plan gratis) |
| **Total con voz del tutor** | **0,36 a 0,48** (0,50 a 0,61 desde 2027) |
| **Total sin voz del tutor** | **0,22 a 0,34** |

Riesgos: el pensamiento suma hasta US$0,20 si se alarga; la caché fría sube el tutor a US$0,73.
Con la voz del tutor apagada por defecto y la versión lite, el promedio queda debajo de la meta
de US$0,50 (SC-005) también en 2027. La prueba de costo del [quickstart](quickstart.md) lo mide
con el modelo real antes del piloto. Con el tope de US$50 por mes alcanza para unos 100 a 200
alumnos por mes que usen el tutor; si la difusión funciona, el aviso del 80% le deja a Andrés la
decisión de subirlo.

## 11. Kit: instrucciones compartidas entre Claude Code y Codex

- **Decision**: `AGENTS.md` es la fuente única de instrucciones del tutor. `CLAUDE.md` tiene solo
  dos líneas de importación: `@AGENTS.md` y `@bitacora.md`. Las lecciones son archivos comunes que
  el tutor abre cuando empieza cada una (no skills). Tres procedimientos van como skills
  (`guardar-version`, `volver-version`, `publicar`) con copias idénticas en `.claude/skills/` y
  `.agents/skills/`, generadas al armar el zip. `.claude/settings.json` endurece los permisos.
  Detalle en [contracts/kit.md](contracts/kit.md).
- **Rationale** (docs oficiales al 28/9/2026):
  - Claude Code lee `AGENTS.md` por su cuenta solo si no hay `CLAUDE.md`; la importación
    `@AGENTS.md` dentro de `CLAUDE.md` funciona (rutas relativas, hasta 4 saltos, no se expande
    entre comillas invertidas) y no duplica contenido. La app de escritorio usa el mismo motor.
  - Codex lee `AGENTS.md` (32 KiB combinados), no lee `CLAUDE.md` y no documenta importaciones.
  - Claude Code lee skills solo de `.claude/skills/`; Codex solo de `.agents/skills/` (lo trata como
    solo lectura). El frontmatter es compatible si se limita a `name` y `description`.
  - Los enlaces simbólicos no son confiables en Windows y en un zip: se copian los archivos.
  - Al iniciar sesión, Claude carga `CLAUDE.md` con sus importaciones (así `bitacora.md` llega
    siempre); en Codex, `AGENTS.md` le pide leer `bitacora.md` antes de la primera respuesta.
- **Alternatives considered**: las lecciones como skills (se cargarían solas por descripción, pero
  de forma menos predecible que "abrí la lección N"); un estilo de salida propio de Claude
  (`.claude/output-styles/tutor.md`), que se prueba en V2 solo si Claude no sigue bien el rol con
  `AGENTS.md`; `.codex/config.toml` para endurecer Codex (solo carga si el alumno marca la carpeta
  como de confianza; se prueba en V2).

## 12. Publicación de los alumnos

- **Decision**: con Codex, Netlify Drop: el tutor prepara la carpeta `sitio/` y el alumno la
  arrastra a la página de Netlify, con cuenta creada con Google. Con Claude Code (Pro), la página
  pública de Claude (`/publicar`, Share, "Anyone with the link") **solo si la prueba V3 confirma
  que el link abre sin cuenta**: la documentación de Claude Code dice que no hace falta iniciar
  sesión, pero un artículo de soporte modificado el 23/9/2026 dice que quien abre el link necesita
  cuenta de Claude. Si V3 lo confirma así, los alumnos de Claude también publican con Netlify Drop y
  la página de Claude queda como vista previa para compartir. La lección 4 enseña a publicar poco y
  probar en la propia computadora (las dos apps tienen un navegador integrado que abre el HTML
  local; si no, doble clic en `sitio/index.html`).
- **Rationale**: son los caminos con menos pasos y sin terminal para cada herramienta
  (investigación del 27/9). El plan gratis de Netlify da 300 créditos por mes, unas 20
  publicaciones, y si se agotan pausa todos los sitios. La página de Claude es una sola página
  estática de hasta 16 MB, sin backend, con el aviso "Content is user-generated and unverified".
- **Alternatives considered**: la línea de comandos de Netlify con reclamo anónimo (requiere
  Node.js, el paso más frágil para un principiante; queda como opción avanzada), Cloudflare con
  cuenta temporal (plan B si falla Netlify), GitHub Pages (exige GitHub con 2FA y repo público),
  ChatGPT Sites (beta, solo planes pagos y con información oficial contradictoria).

## 13. Volver a una versión anterior (lección 6)

- **Decision**: dos skills propias del kit, iguales en las dos herramientas: `guardar-version`
  copia `sitio/` a `versiones/AAAA-MM-DD_HHMM/` y `volver-version` restaura la elegida (antes guarda
  la actual). El tutor guarda una versión antes de cada cambio grande. Git queda fuera del curso;
  los checkpoints de Claude se mencionan como extra para quien usa Claude.
- **Rationale**: Claude Code crea checkpoints en cada pedido y los restaura con `/rewind` (no
  revierte cambios hechos por comandos, duran unos 30 días y no está documentado en la app de
  escritorio). Codex no tiene un deshacer de archivos: su "Revert all" exige un repositorio git. Git
  obliga a instalar software en Windows y en Mac. Copiar carpetas funciona igual en las dos
  herramientas, sin instalar nada, y enseña la idea de versión con algo que el alumno ve.
- **Alternatives considered**: git con los botones de cada app (instalación extra y un concepto
  más en la semana del miedo), solo los checkpoints de Claude (deja afuera a Codex).

## 13 bis. Permisos de fábrica (Constitución V)

- **Decision**: el kit endurece los permisos desde su carpeta. En Claude, `.claude/settings.json`
  con `permissions.defaultMode: "acceptEdits"`, `ask` para `Bash` y `deny` para `sudo` y el borrado
  recursivo. En Codex, la regla "explicar y esperar el sí antes de cada comando" vive en
  `AGENTS.md`, y `versiones/` es la red de seguridad.
- **Rationale**: desde agosto de 2026 las sesiones nuevas de Claude Pro arrancan en modo
  automático, sin preguntar antes de actuar. Sin este ajuste, el kit no cumpliría "pedir permiso
  antes de instalar". Un archivo del proyecto no puede aflojar permisos (los modos más permisivos se
  ignoran si vienen de la carpeta), solo endurecerlos; el alumno igual puede elegir otro modo. El
  modo de fábrica de la app de Codex edita y corre comandos dentro de la carpeta sin preguntar, y
  endurecerlo desde la carpeta exige que el alumno la marque como de confianza. La prueba V2 lo
  mide en las dos herramientas.
- **Alternatives considered**: dejar los permisos de fábrica (no cumple la Constitución V en
  Claude), pedirle al alumno que cambie el modo a mano (una decisión técnica más en la primera
  sesión).

## 14. Machete y revisión mensual

- **Decision**: `contenido/machete.yaml` con fuente, fecha de verificación y marca `probado` por
  dato. Una revisión mensual programada (rutina de Claude en la nube, con la skill
  `revisar-machete` del repo) compara cada dato con su fuente oficial y abre un PR con los cambios
  y las fuentes. Un GitHub Action corre los tests de contenido en cada PR. Aprobar el PR es
  publicar: en el VPS, un timer de systemd trae `contenido/` desde GitHub cada 15 minutos con una
  clave de despliegue de solo lectura, y el backend lee el contenido desde disco en cada pedido.
- **Rationale**: cumple "nada llega a los alumnos sin el OK de Andrés" usando GitHub como paso de
  aprobación, sin construir una pantalla de aprobaciones. El contenido se actualiza sin
  redesplegar código.
- **Alternatives considered**: tarea mensual en el VPS con la API de Claude y aprobación por una
  pantalla propia (más código propio), actualización manual (depende de que alguien se acuerde).

## 15. Malestar serio y derivación

- **Decision**: el prompt base de la puerta y `AGENTS.md` del kit incluyen un protocolo corto:
  responder con cuidado, no diagnosticar, no hablar de métodos, no presentar el suicidio como
  salida ni atribuirlo a una sola causa, y ofrecer siempre los recursos. Ante riesgo inminente,
  911 o 107. Los recursos viven en el machete con fecha de verificación, como cualquier dato que se
  vence:

  | Recurso | Número | Horario | Verificado |
  |---|---|---|---|
  | Línea Nacional de Orientación y Apoyo en la Urgencia de Salud Mental (Ministerio de Salud) | 0800-999-0091 | 24 h, todos los días | 10/9/2026, argentina.gob.ar |
  | Centro de Asistencia al Suicida (ONG) | 135 (CABA y GBA), 0800-345-1435 (todo el país) | de 8 a 24 | asistenciaalsuicida.org.ar, sin fecha |
  | Emergencias | 911 (todo el país), 107 SAME | 24 h | argentina.gob.ar/tema/emergencias |

- **Rationale**: son los que tienen confirmación oficial vigente. La línea de CABA (0800-333-1665)
  tiene su última confirmación oficial en 2025 y la de la Provincia (0800-222-5462) anunció que
  pasará a 24 horas sin confirmación de que ya rija: quedan fuera hasta verificarlas. No hay guía
  oficial argentina para chatbots; las pautas vienen de la Ley 27.130 y de las recomendaciones del
  Ministerio de Salud para medios, alineadas con la OMS.
- **Alternatives considered**: solo el 135 (no atiende las 24 horas), listar todas las líneas
  (algunas sin confirmar en 2026).

## 16. Datos personales (Ley 25.326)

- **Decision**:
  - Aviso de privacidad en `contenido/legal/privacidad.md`, visible antes de inscribirse, con lo
    que exige el art. 6: finalidad, destinatarios, identidad y domicilio del responsable, qué datos
    son obligatorios, consecuencias y derechos; más la leyenda textual de la AAIP que pide la
    Resolución AAIP 14/2018 (la Disposición 10/2008 está derogada). Hay un borrador para que lo
    revise un abogado antes del lanzamiento.
  - Consentimiento expreso y separado: mails del curso (obligatorio), novedades de Andrés (opcional) y
    la transferencia a proveedores en Estados Unidos (Anthropic, Google, Resend), que no es un país
    con protección adecuada según la AAIP.
  - Los mails del curso llevan la baja destacada y la transcripción del art. 27 inc. 3 de la ley y
    del art. 27 párrafo 3 del Decreto 1558/2001 (Disposición 4/2009).
  - El tutor no pide datos de salud y, si el alumno los cuenta, no los repite ni los guarda en la
    idea ni en los resúmenes. Cada conversación se borra 30 días después de terminar su módulo;
    las de módulos sin terminar, 12 meses después de la última actividad (decidido por Andrés el
    28/9/2026; el spec se actualizó).
- **Rationale**: el consentimiento tiene que ser libre, expreso e informado (art. 5). No publicar el
  domicilio del responsable puede ser infracción muy grave (Res. AAIP 126/2024). La base de datos
  excede el uso personal, así que hay que inscribirla en el Registro Nacional de Bases de Datos
  (trámite gratuito en TAD con clave fiscal nivel 2). Lo que un alumno cuenta de su salud es un dato
  sensible (arts. 2 y 7) y las fuentes están en tensión sobre cómo tratarlo sin una ley que lo
  autorice: guardarlo el menor tiempo posible reduce el riesgo. No hay una ley nueva que reemplace
  a la 25.326 al 28/9/2026 (hay proyectos sin aprobar).
- **Alternatives considered**: guardar las conversaciones 12 meses como decía el spec original
  (más útil para revisar el tutor, más riesgo legal), no guardarlas nunca (el alumno no podría
  retomar una conversación a medias).

## 17. Despliegue

- **Decision**: como el proyecto anterior: usuario de sistema `vibe-tutor`, código en
  `/opt/vibe-tutor`, datos en `/srv/vibe-tutor/{data,contenido}`, secretos en
  `/etc/vibe-tutor/.env`, servicio systemd propio en un puerto libre, nginx con certbot.
  `deploy/desplegar.sh` construye el frontend, sube con rsync, reinicia el servicio y corre los
  chequeos de humo. Antes y después se compara la lista de servicios del servidor.
- **Rationale**: es el patrón que ya funcionó con el proyecto anterior sin tocar otros servicios
  del servidor.
- **Alternatives considered**: contenedor Docker (una pieza más para mantener).

## 18. Dominio

- **Decision**: un subdominio de un dominio propio del autor (`curso.example.com` en estos
  documentos; el nombre se define con el nombre del curso); el registro DNS lo crea el autor. Para
  probar antes de tener el dominio sirve un nombre provisorio con HTTPS; Turnstile y el remitente
  de Resend se configuran con el dominio definitivo. Cada instalación pone su dominio en
  `deploy/despliegue.env` (`VIBE_DOMINIO`), que no se versiona.
- **Rationale**: el dominio propio da confianza en la landing y en los mails; el nombre provisorio
  permite probar y hacer el piloto sin esperar el DNS.
- **Alternatives considered**: un dominio nuevo con el nombre del curso (se decide cuando exista
  el nombre).

## 19. Tareas fuera del código antes del lanzamiento

| Tarea | Quién | Por qué |
|---|---|---|
| Grabar los 7 audios | Andrés | FR-005 |
| Conseguir 5 personas de la tribu para el piloto (al menos una con Windows) | Andrés | Piloto y prueba V3 |
| Definir el nombre público del curso y crear el registro DNS | Andrés | §18 |
| Definir el responsable de la base y su domicilio para el aviso de privacidad | Andrés | §16 |
| Inscribir la base en el Registro Nacional de Bases de Datos (TAD) | Andrés | §16 |
| Revisión del aviso de privacidad por un abogado | Andrés (recomendado) | §16 |
| Pasar Resend al plan Pro (US$20 por mes) antes del lanzamiento | Andrés | §8 |
| Crear el sitio de Turnstile y verificar el subdominio en Resend | Andrés | §7, §8 |
| Aprobar el contenido del curso | Andrés | Constitución, flujo de trabajo |
