/**
 * El nombre del curso sale de una sola variable, VITE_NOMBRE_CURSO (en frontend/.env; ver
 * .env.example). La usan la app (src/lib/marca.ts), el título de index.html y el manifest de la
 * app instalable (vite.config.ts). Este archivo no depende del navegador ni de Vite: también lo
 * importa vite.config.ts.
 */

export const NOMBRE_POR_DEFECTO = 'Curso de vibe coding'

/** El nombre configurado, sin espacios de más; si no hay, el nombre por defecto. */
export function nombreCurso(valor: string | null | undefined): string {
  const limpio = typeof valor === 'string' ? valor.trim() : ''
  return limpio || NOMBRE_POR_DEFECTO
}
