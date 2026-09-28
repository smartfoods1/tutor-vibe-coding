# Audios del autor

Cada módulo abre con un audio corto del autor del curso (2 a 3 minutos, grabado una sola vez).
Los audios **no se versionan**: son la voz de una persona y viven solo en el servidor. Esta carpeta
queda en el repo para mostrar el formato.

| Archivo | Qué es |
|---|---|
| `modulo-N.mp3` (N de 1 a 7) | El audio del módulo N |
| `modulo-N.md` | Su transcripción, en markdown |

Son opcionales: si un módulo no tiene audio, la web y el kit siguen sin él. nginx los sirve en
`/audios/modulo-N.mp3` y `/audios/modulo-N.md` (ver `deploy/nginx-vibe-tutor.conf.plantilla`), y el
kit enlaza los de los módulos 4 a 7.

Qué cuenta cada audio (una traba real, no un logro; nada que se venza, como precios o nombres de
botones) está descrito módulo por módulo en `contenido/curriculo.md`.
