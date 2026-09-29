# contenido/

Todo lo que ven los alumnos y no es código. Lo leen el backend (en cada pedido, desde disco) y el
armado del kit. Cada cambio pasa por un PR con los tests de contenido, y nada llega a los alumnos
sin la aprobación del autor del curso (Constitución IV).

| Carpeta o archivo | Qué va |
|---|---|
| `prompts/` | Prompt base del tutor de la web: persona, reglas y protocolo de malestar |
| `web/` | Por módulo de la web (1 a 3): la guía para el tutor (`modulo-N.md`) y la guía escrita para cuando el tutor no está disponible (`guia-modulo-N.md`) |
| `kit/` | Plantilla del kit (ver `specs/001-curso-vibe-coding/contracts/kit.md`) |
| `machete.yaml` | Datos que se vencen, con fuente oficial, fecha de verificación y si se probó en la realidad. Viaja en cada kit como `curso/machete.md` |
| `mails/` | Textos de los mails del curso |
| `legal/` | Aviso de privacidad, textos de consentimiento y pie legal de los mails, con su versión |
| `audios/` | Audios del autor por módulo (`modulo-N.mp3`) y sus transcripciones (`modulo-N.md`). No se versionan: cada instalación pone los suyos. Qué cuenta cada uno está en `curriculo.md` |
| `ejemplos/` | El kit mínimo de las pruebas de viabilidad |
| `investigacion/` | Informes con fuentes que sostienen el currículo |
| `curriculo.md` | Mapa del curso: objetivo, conceptos, ejercicio y criterio de "terminado" de cada módulo |

Todo el texto para alumnos va en español rioplatense, con voseo y sin emojis.

## Marcadores

El backend reemplaza estos marcadores al servir el contenido o al armar el kit, con lo que diga la
configuración de cada instalación:

- `{{AUTOR}}`: el nombre del autor del curso (`AUTOR_NOMBRE`). Si está vacío, queda "el autor del
  curso". Escribí las frases para que se lean bien con las dos cosas: sin empezar una oración con
  el marcador y sin ponerlo después de "de" o "a" (quedaría "de el autor").
- `{{NEWSLETTER}}`: el nombre del servicio donde el autor publica sus novedades
  (`NEWSLETTER_NOMBRE`). Si está vacío, no hay casilla de novedades y el consentimiento queda en 0;
  si forkeás sin newsletter, sacá las partes de `legal/` que hablan de ella.
- `{{SIGUIENTE_PASO}}`: solo en `legal/`. Cómo se nombra el siguiente paso que ofrece la instalación
  (`SIGUIENTE_PASO_NOMBRE`, con su artículo, porque va después de "cuando abra"); si está vacío, queda
  "el siguiente paso". Las partes entre `{{#SIGUIENTE_PASO}}` y `{{/SIGUIENTE_PASO}}` se muestran solo
  con la función activa (spec 002). El kit y las lecciones no lo usan.
- Los demás (`{{AYUDA}}`, `{{URL_CURSO}}`, `{{ENLACE_BAJA}}` y compañía) los llena el backend con
  datos del machete, del alumno o del mail que se arma.

## Licencias

El contenido del curso (todo `contenido/` salvo `kit/`, `ejemplos/` y `machete.yaml`) va con
licencia CC BY 4.0: lo podés usar, adaptar y compartir, citando al autor. `kit/`, `ejemplos/` y
`machete.yaml` van con CC0 1.0 (dominio público): la carpeta y la página de cada alumno son suyas, y
el machete viaja dentro de cada kit (`curso/machete.md` y las líneas de ayuda de `AGENTS.md`).
`kit/LICENCIA.txt` viaja en cada kit. El detalle está en la raíz del repo.

## Si forkeás el curso

- Cambiá la configuración (`AUTOR_NOMBRE`, `NEWSLETTER_NOMBRE`) antes de tocar los textos: los
  marcadores ya ponen tu nombre donde corresponde.
- `legal/` es el borrador argentino (Ley 25.326) de la instalación del autor. No es asesoramiento
  legal: adaptalo a tu país, tu responsable y tus proveedores.
- `machete.yaml` tiene fechas de verificación: revisalas antes de mostrarlo a tus alumnos.
