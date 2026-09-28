---
name: guardar-version
description: Guarda una copia de la carpeta sitio/ en versiones/, con fecha, hora y un nombre corto opcional, para poder volver atrás. Usala antes de cada cambio grande, después de cada paso que funcionó o cuando la persona lo pida.
---

# Guardar versión

1. Elegí el nombre de la carpeta nueva: `versiones/AAAA-MM-DD_HHMM-nombre/`, con la fecha y la
   hora de ahora.
   - Si la persona escribió un nombre al llamar la skill (por ejemplo, "primera"), usá ese. Si no,
     preguntale en una frase si le quiere poner uno; si no quiere, dejá solo la fecha y la hora.
   - Si la usás por tu cuenta antes de un cambio grande, poné un nombre que lo describa, como
     `antes-del-menu`.
   - El nombre va en minúsculas, sin acentos y con guiones en lugar de espacios: "Mi primera" queda
     `mi-primera`.
2. Si ya existe una carpeta con ese nombre, no la toques: agregale `-2` al final.
3. Copiá la carpeta `sitio/` completa, con todo lo que tiene adentro, a la carpeta nueva. Si copiar
   necesita un comando, explicá en una frase qué hace y esperá el sí antes de correrlo.
4. Comprobá que la copia tiene los mismos archivos que `sitio/`.
5. En `bitacora.md`, en la sesión de hoy, anotá "Versión guardada:" con el nombre de la carpeta y,
   en una frase, qué tenía. Actualizá también "Última versión guardada".
6. Contale a la persona que la versión quedó guardada, que la puede ver en la carpeta `versiones`
   desde el Finder (Mac) o el Explorador de archivos (Windows) y que puede volver a ella con
   `volver-version`.

Nunca borres, cambies ni sobrescribas una carpeta que ya está en `versiones/`. No copies
`practica/` ni nada que no sea `sitio/`. Trabajá solo dentro de esta carpeta.
