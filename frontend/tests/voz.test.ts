import { describe, expect, it } from 'vitest'
import { MAX_FRASE, frasesParaVoz, textoPlano } from '../src/lib/voz.ts'

describe('textoPlano', () => {
  it('saca las marcas de markdown para que no se lean en voz alta', () => {
    expect(textoPlano('## Paso 1\n**Hola** [tu idea](https://x.com) y `carpeta`.\n- uno\n- dos')).toBe(
      'Paso 1\nHola tu idea y carpeta.\nuno\ndos',
    )
  })
})

describe('frasesParaVoz', () => {
  it('corta el texto en frases', () => {
    expect(frasesParaVoz('Hola. ¿Cómo estás? Bien, gracias.')).toEqual(['Hola.', '¿Cómo estás?', 'Bien, gracias.'])
  })

  it('usa los saltos de línea como cortes', () => {
    expect(frasesParaVoz('Primero esto\n\nDespués aquello')).toEqual(['Primero esto', 'Después aquello'])
  })

  it('ninguna frase pasa de 600 caracteres', () => {
    expect(MAX_FRASE).toBe(600)
    const larga = Array.from({ length: 200 }, (_, i) => `palabra${i}`).join(', ')
    const frases = frasesParaVoz(larga)
    expect(frases.length).toBeGreaterThan(1)
    for (const frase of frases) expect(frase.length).toBeLessThanOrEqual(600)
    expect(frases.join(' ').replace(/\s+/g, ' ')).toBe(larga)
  })

  it('un texto vacío no da frases', () => {
    expect(frasesParaVoz('  \n ')).toEqual([])
  })
})
