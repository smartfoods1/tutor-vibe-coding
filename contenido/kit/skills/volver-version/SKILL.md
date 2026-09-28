---
name: volver-version
description: Muestra las versiones guardadas en versiones/ y, si la persona confirma, deja sitio/ igual a la versión elegida, guardando antes la actual. Usala cuando algo se rompió, cuando la persona quiere volver atrás o para practicar cómo volver.
---

# Volver a una versión

1. Listá las carpetas de `versiones/`, de la más nueva a la más vieja, con su fecha, su nombre y
   lo que dice `bitacora.md` de cada una. Si la persona cree que "se perdió todo", empezá por acá:
   mostrale que sus versiones están.
2. Preguntá a cuál quiere volver. Si quiere verla antes, que abra con doble clic el `index.html` de
   esa carpeta.
3. Antes de tocar nada, guardá la versión actual con `guardar-version`, con el nombre
   `antes-de-volver`.
4. Con un sí explícito, dejá `sitio/` igual a la versión elegida: copiá sus archivos a `sitio/` y,
   si en `sitio/` quedan archivos que esa versión no tiene, sacalos (la copia del paso 3 los
   guarda). Si hace falta un comando, explicá en una frase qué hace y esperá el sí antes de
   correrlo.
5. Mostrale cómo ver el resultado (vista previa de la app o doble clic en `sitio/index.html`) y
   pedile que te cuente qué ve.
6. Anotá en `bitacora.md` a qué versión volvió.

La versión elegida se copia, no se mueve: su carpeta queda como estaba. Nunca borres ni cambies
nada dentro de `versiones/`. Trabajá solo dentro de esta carpeta.
