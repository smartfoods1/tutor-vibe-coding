import { describe, expect, it } from 'vitest'
import { NOMBRE_CURSO, textoUsoContenido } from '../src/lib/marca.ts'
import { NOMBRE_POR_DEFECTO, nombreCurso } from '../src/lib/nombre.ts'

describe('nombre del curso', () => {
  it('sin VITE_NOMBRE_CURSO usa el nombre por defecto', () => {
    expect(NOMBRE_POR_DEFECTO).toBe('Curso de vibe coding')
    expect(nombreCurso(undefined)).toBe(NOMBRE_POR_DEFECTO)
    expect(nombreCurso('')).toBe(NOMBRE_POR_DEFECTO)
    expect(nombreCurso('   ')).toBe(NOMBRE_POR_DEFECTO)
  })

  it('con VITE_NOMBRE_CURSO usa ese nombre, sin espacios de más', () => {
    expect(nombreCurso('  Taller de páginas  ')).toBe('Taller de páginas')
  })

  it('el nombre que usa la app sale de VITE_NOMBRE_CURSO', () => {
    expect(NOMBRE_CURSO).toBe(nombreCurso(import.meta.env.VITE_NOMBRE_CURSO))
    expect(NOMBRE_CURSO.trim()).not.toBe('')
  })
})

describe('texto de uso como contenido', () => {
  it('nombra al autor si está configurado', () => {
    expect(textoUsoContenido('Ana')).toBe('Ana lo puede usar como contenido, por ejemplo para mostrarlo en sus redes.')
  })

  it('sin autor habla del curso', () => {
    expect(textoUsoContenido(null)).toBe(
      'El curso lo puede usar como contenido, por ejemplo para mostrarlo en sus redes.',
    )
  })
})
