# Adaptar el curso a tu comunidad

El repo trae un curso completo, escrito para gente de Argentina que nunca programó. Para darlo con
tu nombre, a tu comunidad o en tu país, estos son los pasos, en el orden en que conviene hacerlos.
Casi todo es texto en `contenido/` o configuración: no hace falta tocar código (la excepción es la
zona horaria, en el paso 8). Los comandos de esta guía se corren desde la raíz del repo.

Antes de empezar:

- **Licencias.** El contenido es CC BY 4.0: podés adaptarlo libremente, incluso para cobrar, con
  una línea de atribución (hay una modelo en [LICENSE-CONTENIDO](../LICENSE-CONTENIDO)). El kit,
  los ejemplos y el machete son CC0: la carpeta de cada alumno es suya y el machete viaja adentro.
  Lo que no cubre la licencia es el nombre, la voz y la identidad del autor original: tu curso va
  con tu nombre y tu voz.
- **Probalo en local mientras cambiás.** Con el modo demo ves cada cambio sin gastar. Ver
  [desarrollo-local.md](desarrollo-local.md).
- **Los tests cuidan el contenido.** `cd backend && .venv/bin/pytest` revisa el esquema del
  machete, que nada diga "gratis" sin haberlo probado, los marcadores y el tamaño del kit. Corrélos
  después de cada cambio.

Para encontrar lo que es propio de Argentina (leyes, líneas de ayuda, impuestos, zona horaria),
desde la raíz del repo:

```bash
grep -rn "Argentina\|argentin" contenido backend/vibe_tutor frontend/src --exclude-dir=investigacion
```

## 1. Recursos de ayuda y emergencias de tu país

Es lo primero, porque es lo más delicado. Si un alumno cuenta un malestar serio, el tutor de la web
y el del kit responden con cuidado, no diagnostican y le pasan líneas de ayuda profesional. Esas
líneas salen de `contenido/machete.yaml`, de los datos con `tema: ayuda` (en el kit llegan por el
marcador `{{AYUDA}}`).

Reemplazalas por las de tu país: una línea de salud mental, una de prevención del suicidio si
existe y el número de emergencias. Cada una con su fuente oficial y la fecha en que la verificaste,
como el resto del machete (paso 5):

```yaml
- id: ayuda-emergencias
  tema: ayuda
  aplica_a: [codex, claude]
  sistema: [mac, windows]
  texto: >-
    Si hay riesgo inmediato: <número de emergencias de tu país>.
  fuente: <página oficial donde lo verificaste>
  verificado: 2026-10-01
  probado: false
```

Verificá cada número en la fuente oficial el mismo día que lo cargás, y revisá también el protocolo
de malestar del prompt en `contenido/prompts/base.md`.

## 2. Textos legales

Están en `contenido/legal/`:

| Archivo | Qué es |
|---|---|
| `privacidad.md` | El aviso de privacidad: responsable, qué datos se guardan, para qué, con quién se comparten, cuánto tiempo y cómo ejercer los derechos |
| `consentimientos.md` | Los textos cortos de las casillas de la inscripción y su explicación |
| `pie-mails.md` | El pie legal de los mails |

Los que vienen son borradores para Argentina (Ley 25.326) y nombran los proveedores y países de la
instalación original. Adaptalos a tu ley, a quien sea responsable de los datos (vos o tu
organización) y a tus proveedores reales: dónde está tu servidor, qué servicios usás y en qué
países. No son asesoramiento legal: hacelos revisar por alguien que ejerza en tu país antes de
abrir la inscripción.

Cada archivo tiene una `version` en su encabezado. Cuando cambies un texto, cambiá la versión: la
inscripción guarda con qué versión aceptó cada alumno.

Ojo con un detalle de la ley argentina: el permiso de "transferencia" (datos que pasan por
proveedores de otros países) es obligatorio en la inscripción. Si en tu país no aplica, cambiá el
texto; sacar la casilla requiere tocar el backend y el frontend.

## 3. Nombre, autor y newsletter

| Qué | Dónde | Ejemplo |
|---|---|---|
| Nombre del curso en la web, la pestaña y la app instalada | `VITE_NOMBRE_CURSO` en `frontend/.env` (copiá `frontend/.env.example`; se toma al compilar) | `VITE_NOMBRE_CURSO=Vibe coding para docentes` |
| Nombre corto, debajo del ícono en el celular (12 letras o menos) | `VITE_NOMBRE_CORTO` en `frontend/.env` | `VITE_NOMBRE_CORTO=Vibe docente` |
| Quién da el curso | `AUTOR_NOMBRE` en `/etc/vibe-tutor/.env` | `AUTOR_NOMBRE="Laura"` |
| Tu newsletter | `NEWSLETTER_NOMBRE` en `/etc/vibe-tutor/.env` | `NEWSLETTER_NOMBRE="mi boletín"` |

En los textos de `contenido/`, `{{AUTOR}}` se reemplaza por `AUTOR_NOMBRE` (o por "el autor del
curso" si lo dejás vacío) y `{{NEWSLETTER}}` por `NEWSLETTER_NOMBRE`. Usalos en vez de escribir tu
nombre a mano, así el contenido sirve para cualquiera que lo forkee después.

Si `NEWSLETTER_NOMBRE` está vacío, la inscripción no muestra la casilla de novedades y nadie queda
anotado. Si tiene valor, la casilla aparece desmarcada y, desde `/admin`, bajás el CSV con los
mails de quienes aceptaron (`/api/admin/novedades.csv`, una columna `email`), listo para importar
en tu plataforma de newsletter.

## 4. Colores e íconos

- **Colores**: son variables en el bloque `@theme` de `frontend/src/index.css`: `--color-papel`
  (fondo), `--color-tinta` (texto), `--color-oro` y `--color-oro-hondo` (lo que se toca),
  `--color-oxido` (estado actual y errores), `--color-linea` (líneas) y otros tonos
  (`--color-hoja`, `--color-marron`, `--color-alumno`). Cambiá los valores y mantené un buen
  contraste entre texto y fondo.
- **Color de la app instalada**: `theme_color` y `background_color` del manifest, en
  `frontend/vite.config.ts`, y la etiqueta `theme-color` de `frontend/index.html`.
- **Íconos**: en `frontend/public/`. `favicon.svg` (pestaña), `apple-touch-icon.png` (180 × 180),
  `icono-192.png` y `icono-512.png` (app instalada) e `icono-maskable-512.png` (512 × 512, con el
  dibujo dentro del círculo central, para Android). Reemplazalos con los mismos nombres y tamaños.
- **Tipografías**: Source Serif 4 e IBM Plex Mono, instaladas con Fontsource. Si las cambiás,
  cambiá también los `import` de `frontend/src/main.tsx` y las variables `--font-*`.

## 5. El machete: datos que se vencen

`contenido/machete.yaml` guarda todo lo que cambia con el tiempo: planes y precios de las
herramientas, cómo instalarlas, cómo ver la página, cómo publicarla, límites y líneas de ayuda. El
tutor de la web lo consulta y cada kit lleva una copia con su fecha (por eso el machete es CC0).
Cada dato tiene:

| Campo | Qué va |
|---|---|
| `id` | Un nombre único, en minúsculas y con guiones |
| `tema` | `planes`, `instalar`, `ver`, `publicar`, `limites`, `volver-atras` o `ayuda` |
| `aplica_a` | `codex`, `claude` o los dos |
| `sistema` | `mac`, `windows` o los dos |
| `texto` | Lo que lee el alumno, en segunda persona |
| `fuente` | La página oficial donde lo verificaste |
| `verificado` | La fecha de esa verificación (AAAA-MM-DD) |
| `probado` | `true` solo si alguien lo hizo de verdad, de punta a punta |

Reglas: nada que prometa que algo no se paga ("gratis", "sin costo", "sin tarjeta") puede figurar
sin `probado: true` (un test lo impide), y un dato con más de 45 días sin verificar aparece como
vencido en `/admin`. Revisá el machete una vez por mes. Si tu público paga en otra moneda o con
otros impuestos, decilo en los textos de `planes`.

## 6. Contenido de los módulos y del kit

El recorrido tiene 7 módulos: los 1 a 3 en la web, con el tutor, y los 4 a 7 en el kit, dentro de
Claude Code o Codex. El mapa completo, con el porqué pedagógico de cada decisión y sus fuentes,
está en `contenido/curriculo.md`.

| Qué | Dónde |
|---|---|
| Personalidad y reglas del tutor de la web | `contenido/prompts/base.md` |
| Guía del tutor para cada módulo de la web | `contenido/web/modulo-1.md` a `modulo-3.md` |
| Guía escrita que ve el alumno si el tutor no está disponible (por ejemplo, al llegar al tope) | `contenido/web/guia-modulo-1.md` a `guia-modulo-3.md` |
| Plantilla de "mi idea en una página" | `contenido/web/plantilla-idea.md` |
| Mails del curso | `contenido/mails/` |
| Instrucciones del kit para cada herramienta | `contenido/kit/AGENTS.md` (Codex) y `contenido/kit/CLAUDE.md` (Claude Code) |
| Lecciones 4 a 7 | `contenido/kit/curso/` |
| Habilidades del kit (guardar versión, volver, publicar) | `contenido/kit/skills/` |
| Títulos y resúmenes de los módulos en la web | `frontend/src/lib/marca.ts` |

Algunas reglas que conviene mantener:

- Todo el texto para alumnos va en un solo registro (el original usa español rioplatense con
  voseo) y sin emojis. Si cambiás de registro, cambialo en todos los archivos.
- El tutor nunca se presenta como vos ni imita tu voz.
- Las instrucciones del kit tienen que ser cortas: Codex tiene un límite para ellas y las
  instrucciones largas se cumplen peor. Los tests fallan si `AGENTS.md` pasa de 8 KiB o de 200
  líneas.
- Los datos que se vencen no se escriben en las lecciones: van al machete y se citan desde ahí.
- Marcadores como `{{URL_CURSO}}`, `{{URL_AUDIOS}}` o `{{AYUDA}}` los completa el backend al armar
  el kit o al servir el texto: no los borres.

## 7. Audios (opcionales)

Cada módulo puede abrir con un audio corto tuyo, de 2 a 3 minutos, con su transcripción. Los
audios no se versionan (git los ignora): viven en tu copia local y `desplegar.sh` los sube con el
resto del contenido.

- Formato: `contenido/audios/modulo-N.mp3` y su transcripción `contenido/audios/modulo-N.md`, con
  N de 1 a 7.
- Si falta el mp3 de un módulo, ese módulo arranca sin audio. La transcripción es opcional, pero
  conviene: no todos pueden escuchar.
- La web muestra los que haya, y el kit enlaza a los de los módulos 4 a 7 en
  `https://<tu dominio>/audios/modulo-N.mp3`.
- Ojo: `desplegar.sh` sincroniza la carpeta, así que si borrás un audio de tu compu, también se
  borra del servidor.

## 8. Zona horaria (si no estás en Argentina)

El mes del tope de gasto, las fechas del machete y las de la web se cuentan con la hora de Buenos
Aires. Para otra zona, cambiá `ZONA_ARGENTINA` en `backend/vibe_tutor/costos.py` (el resto del
backend la toma de ahí) y `timeZone` en `frontend/src/paginas/Admin.tsx` y
`frontend/src/paginas/MiIdea.tsx`, por ejemplo a `America/Mexico_City`. Es de lo poco que se
cambia en el código.

## 9. Un siguiente paso al terminar (opcional)

Si después del curso vas a abrir algo más (otro curso, un taller), la web se lo puede contar a
quien termina, sin vender nada en el camino. Viene apagado. Con la función prendida, la primera vez
que un alumno registra el link de su página la web le pregunta si tiene un negocio que ya vende; si
dice que sí, ve tu texto y una casilla desmarcada para que le avisen cuando abra. No aparece en el
kit ni en las lecciones, y no llama al tutor ni a ningún servicio pago.

| Qué | Dónde | Ejemplo |
|---|---|---|
| Prenderlo | `SIGUIENTE_PASO` en `/etc/vibe-tutor/.env` | `SIGUIENTE_PASO=true` |
| Cómo se llama en los textos legales, con su artículo (va después de "cuando abra") | `SIGUIENTE_PASO_NOMBRE` | `SIGUIENTE_PASO_NOMBRE="el curso de sistemas para negocios"` |
| La pregunta | `SIGUIENTE_PASO_PREGUNTA` | `SIGUIENTE_PASO_PREGUNTA="¿Tenés un negocio que ya vende?"` |
| El texto que ve quien contesta que sí | `SIGUIENTE_PASO_TEXTO` | `SIGUIENTE_PASO_TEXTO="En marzo abre un curso para construir el sistema que gestiona tu negocio."` |

Hacen falta los cuatro: si falta un texto, la función queda apagada y `/admin` te dice cuál. No
pongas precios en la pregunta ni en el texto: el curso no vende.

Cómo cuida los datos:

- La respuesta se cuenta sin guardar quién contestó: suma a un total de "sí" y otro de "no". De
  cada alumno queda solo que ya contestó, para no volver a preguntarle.
- El aviso es un permiso aparte (`siguiente_paso`), con su fecha y la versión del texto legal que
  aceptó, como los demás. El alumno lo ve y lo saca desde "Mis datos" (y lo pide ahí mientras la
  función esté prendida); viaja en la descarga de sus datos y se borra con ellos.
- La lista de avisos no se exporta. En `/admin` ves solo tres números: cuántos contestaron, cuántos
  dijeron que tienen un negocio y cuántos tienen el aviso activo. El curso todavía no manda el
  aviso: eso se construye junto con tu siguiente paso, desde el mismo sistema, nunca exportando la
  lista.

Si la apagás después de usarla, la pregunta deja de salir; los avisos que ya existen siguen en
"Mis datos", se pueden sacar y siguen contando en el reporte.

Los textos legales de `contenido/legal/` ya describen el permiso en bloques que se muestran solo
con la función prendida, y `{{SIGUIENTE_PASO}}` se reemplaza por `SIGUIENTE_PASO_NOMBRE`. Revisalos
como el resto (paso 2) antes de prenderla.

## Lista para antes de abrir la inscripción

- [ ] Líneas de ayuda y emergencias de tu país, con fuente y fecha.
- [ ] Textos legales adaptados y revisados, con versión nueva.
- [ ] `VITE_NOMBRE_CURSO`, `AUTOR_NOMBRE` y, si corresponde, `NEWSLETTER_NOMBRE`.
- [ ] Si ofrecés un siguiente paso: `SIGUIENTE_PASO` y sus tres textos, sin precios, con los textos
  legales revisados.
- [ ] Colores e íconos propios.
- [ ] Machete verificado en los últimos 45 días.
- [ ] Zona horaria, si no estás en Argentina.
- [ ] Tests en verde.
- [ ] Una persona de tu comunidad hizo el curso completo y publicó su página.
- [ ] `AVISO_PRUEBA=false` en `/etc/vibe-tutor/.env` el día que abrís la inscripción (y reiniciá el
  servicio).
