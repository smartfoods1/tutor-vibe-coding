import { describe, expect, it } from 'vitest'
import { leerConfig } from '../src/componentes/Configuracion.tsx'

describe('leerConfig', () => {
  it('toma el autor, el newsletter, el modo demo y la aprobación manual de /api/config', () => {
    expect(
      leerConfig({
        turnstile_site_key: 'clave',
        aviso_prueba: true,
        autor_nombre: ' Ana ',
        newsletter: 'Boletín del curso',
        modo_demo: true,
        aprobacion_manual: true,
      }),
    ).toEqual({
      turnstileSiteKey: 'clave',
      avisoPrueba: true,
      autorNombre: 'Ana',
      newsletter: 'Boletín del curso',
      modoDemo: true,
      aprobacionManual: true,
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
    }
    expect(leerConfig({ autor_nombre: '   ', newsletter: '', modo_demo: 'true', aprobacion_manual: 1 })).toEqual(vacia)
    expect(leerConfig({ turnstile_site_key: null, aviso_prueba: false })).toEqual(vacia)
    expect(leerConfig(null)).toEqual(vacia)
  })
})
