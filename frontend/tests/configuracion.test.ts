import { describe, expect, it } from 'vitest'
import { leerConfig } from '../src/componentes/Configuracion.tsx'

const SIGUIENTE_PASO = {
  nombre: 'el curso de prueba',
  pregunta: '¿Tenés un negocio que ya vende?',
  texto: 'Más adelante abre un curso para armar el sistema que lo gestiona.',
}

describe('leerConfig', () => {
  it('toma el autor, el newsletter, el modo demo, la aprobación manual y el siguiente paso de /api/config', () => {
    expect(
      leerConfig({
        turnstile_site_key: 'clave',
        aviso_prueba: true,
        autor_nombre: ' Ana ',
        newsletter: 'Boletín del curso',
        modo_demo: true,
        aprobacion_manual: true,
        siguiente_paso: { ...SIGUIENTE_PASO, nombre: ' el curso de prueba ' },
      }),
    ).toEqual({
      turnstileSiteKey: 'clave',
      avisoPrueba: true,
      autorNombre: 'Ana',
      newsletter: 'Boletín del curso',
      modoDemo: true,
      aprobacionManual: true,
      siguientePaso: SIGUIENTE_PASO,
    })
  })

  it('lo vacío o raro queda en null o en false (config de un servidor viejo incluida)', () => {
    const vacia = {
      turnstileSiteKey: null,
      avisoPrueba: false,
      autorNombre: null,
      newsletter: null,
      modoDemo: false,
      aprobacionManual: false,
      siguientePaso: null,
    }
    expect(leerConfig({ autor_nombre: '   ', newsletter: '', modo_demo: 'true', aprobacion_manual: 1 })).toEqual(vacia)
    expect(leerConfig({ turnstile_site_key: null, aviso_prueba: false, siguiente_paso: null })).toEqual(vacia)
    expect(leerConfig(null)).toEqual(vacia)
  })

  it('el siguiente paso queda apagado (null) si le falta alguno de sus tres textos', () => {
    expect(leerConfig({ siguiente_paso: SIGUIENTE_PASO }).siguientePaso).toEqual(SIGUIENTE_PASO)
    expect(leerConfig({ siguiente_paso: { ...SIGUIENTE_PASO, texto: '   ' } }).siguientePaso).toBeNull()
    expect(leerConfig({ siguiente_paso: { nombre: 'el curso de prueba', pregunta: '¿Sí?' } }).siguientePaso).toBeNull()
    expect(leerConfig({ siguiente_paso: { ...SIGUIENTE_PASO, pregunta: 7 } }).siguientePaso).toBeNull()
    expect(leerConfig({ siguiente_paso: 'si' }).siguientePaso).toBeNull()
    expect(leerConfig({ siguiente_paso: true }).siguientePaso).toBeNull()
  })
})
