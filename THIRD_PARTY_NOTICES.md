# Avisos de terceros

Este repositorio incluye o usa trabajo de otras personas y proyectos. Cada uno conserva su
licencia. Lo propio del proyecto está en [LICENSE](LICENSE) (código, MIT),
[LICENSE-CONTENIDO](LICENSE-CONTENIDO) (contenido y documentación de diseño, CC BY 4.0) y
[contenido/kit/LICENCIA.txt](contenido/kit/LICENCIA.txt) (kit, ejemplos y machete, CC0 1.0).

## spec-kit (GitHub)

El proyecto se diseñó con [spec-kit](https://github.com/github/spec-kit) (versión 0.11.1). Estos
archivos vienen de spec-kit, algunos con ajustes menores, y siguen bajo su licencia MIT:

- `.specify/scripts/`, `.specify/templates/`, `.specify/extensions/`, `.specify/workflows/` e
  `.specify/integrations/`
- `.specify/extensions.yml`, `.specify/init-options.json`, `.specify/integration.json` y
  `.specify/feature.json`
- `.claude/skills/speckit-*/` (los comandos de spec-kit para Claude Code)

No vienen de spec-kit, aunque se hayan escrito con sus plantillas: `.specify/memory/` (la
constitución del proyecto) y `specs/`, que son contenido propio bajo CC BY 4.0.

```text
MIT License

Copyright GitHub, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Tipografías

La web usa dos familias que se instalan como dependencias de npm (paquetes de
[Fontsource](https://fontsource.org)) y quedan dentro del build (`frontend/dist/assets/`):

| Familia | Autoría | Paquete | Licencia |
|---|---|---|---|
| Source Serif 4 | Adobe | `@fontsource/source-serif-4` | SIL Open Font License 1.1 |
| IBM Plex Mono | IBM Corp. | `@fontsource/ibm-plex-mono` | SIL Open Font License 1.1 |

El texto completo de la licencia viene en el archivo `LICENSE` de cada paquete, dentro de
`frontend/node_modules/@fontsource/`, y en [openfontlicense.org](https://openfontlicense.org).
La OFL permite usar, incluir y redistribuir las fuentes con cualquier software, pero no venderlas
solas.

## ffmpeg

El backend llama a [ffmpeg](https://ffmpeg.org) como programa externo para convertir el audio del
dictado y de la voz del tutor. No está incluido en el repositorio ni se distribuye con él: se
instala aparte en el servidor y, si probás la voz o corrés sus tests, en tu compu, con la licencia
de esa instalación (LGPL o GPL, según cómo se haya compilado).

## Dependencias

Las dependencias del backend (`backend/pyproject.toml`) y del frontend (`frontend/package.json` y
`frontend/package-lock.json`) no están copiadas en el repositorio: se instalan con pip o uv y con
npm, y cada una conserva su propia licencia. El build del frontend (`frontend/dist/`, que no se
versiona) incluye código de esas dependencias, con los avisos que ellas mismas traen.

## Servicios externos

El curso funciona con servicios de terceros que se contratan aparte y tienen sus propios términos:
Anthropic (Claude), Google (Gemini), Resend (mails) y, si lo activás, Cloudflare Turnstile, cuyo
script se carga desde `challenges.cloudflare.com` y no está en el repositorio. Este proyecto no
tiene relación con ninguna de esas empresas.

## Íconos

Los íconos de `frontend/public/` (favicon, íconos de la app y del celular) son de diseño propio y
están cubiertos por la licencia MIT junto con el resto del frontend.
