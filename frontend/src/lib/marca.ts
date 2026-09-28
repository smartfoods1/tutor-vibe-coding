import { nombreCurso } from './nombre.ts'

/** El nombre del curso: se cambia con VITE_NOMBRE_CURSO (ver frontend/.env.example), no acá. */
export const NOMBRE_CURSO: string = nombreCurso(import.meta.env.VITE_NOMBRE_CURSO)

/**
 * La opción de uso como contenido (Mostrar y Mis datos): nombra al autor si la instalación lo
 * configuró (AUTOR_NOMBRE en el backend) y, si no, al curso.
 */
export function textoUsoContenido(autor: string | null): string {
  return `${autor ?? 'El curso'} lo puede usar como contenido, por ejemplo para mostrarlo en sus redes.`
}

export const TITULOS_MODULOS: Record<number, string> = {
  1: 'Cómo piensa un vibe coder',
  2: 'Tu idea en una página',
  3: 'Tu taller',
  4: 'Primera victoria',
  5: 'Construir',
  6: 'Cuando se rompe',
  7: 'Terminar y mostrar',
}

export const RESUMEN_MODULOS: Record<number, string> = {
  1: 'Qué es esto de construir conversando con una máquina, y qué te frena.',
  2: 'Tu idea, contada en una página que se lee en dos minutos.',
  3: 'Elegís tu herramienta, la instalás y bajás tu kit.',
  4: 'Tu idea andando y publicada con un link.',
  5: 'La mejorás paso a paso.',
  6: 'Qué hacer cuando algo se rompe.',
  7: 'La versión final, publicada y registrada.',
}
