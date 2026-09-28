# Machete

Datos que cambian seguido, con la fecha en que se verificaron. Si algo de acá no coincide con lo
que ves en la pantalla, avisale a la persona y seguí con lo que ves.

**Verificado:** 27 y 28/9/2026 contra la documentación oficial. **Probado en la realidad:**
pendiente. Este es un kit de prueba: los pasos marcados "(verificar)" se confirman en la prueba de
viabilidad V3.

## Ver la página en la computadora

- En cualquier herramienta: doble clic en `sitio/index.html` desde la carpeta.
- Claude (app de escritorio): el navegador integrado abre archivos HTML de la carpeta; se abre con
  Cmd/Ctrl + Shift + B (verificar).
- Codex (app de ChatGPT): el navegador integrado se abre con Cmd/Ctrl + Shift + B (verificar).

## Publicar con Netlify Drop

Para Codex, y para Claude si su link público pide cuenta.

1. Abrí https://app.netlify.com/drop en el navegador.
2. Creá una cuenta o entrá con tu cuenta de Google (verificar).
3. Arrastrá solo la carpeta `sitio` al recuadro de la página, nunca la carpeta entera del kit:
   `mi-idea.md`, `bitacora.md` y `cuaderno.md` quedarían públicos.
4. Esperá unos segundos: aparece un link que termina en `.netlify.app`.
5. Si la cuenta es nueva (creada desde el 28/7/2026), el proyecto nace privado. Entrá a
   Project configuration, General, Visitor access, Project visibility, y hacelo público.
   Recién ahí cualquiera puede abrir el link (verificar).

Límite: el plan Free de Netlify alcanza para unas 20 publicaciones por mes y, si se pasa, se pausan todos
los sitios. Publicá poco.

## Publicar con la página pública de Claude

Solo con Claude Pro.

1. Pedile a Claude: "Publicá `sitio/index.html` como artifact".
2. Si la app pregunta, aprobá la publicación.
3. Abrí el link que te da Claude.
4. Tocá "Share", elegí que lo pueda ver cualquiera con el link y copiá el link (verificar).

Pendiente de prueba: si el link abre sin cuenta de Claude. Si pide cuenta, usá Netlify Drop.
