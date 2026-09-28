import { afterEach, describe, expect, it, vi } from 'vitest'
import { LADO_MAXIMO, achicarImagen, medidasAchicadas } from '../src/lib/captura.ts'

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('medidasAchicadas', () => {
  it('lleva el lado largo a 1440 px y mantiene la proporción', () => {
    expect(LADO_MAXIMO).toBe(1440)
    expect(medidasAchicadas(4000, 3000)).toEqual({ ancho: 1440, alto: 1080 })
    expect(medidasAchicadas(1170, 2532)).toEqual({ ancho: 665, alto: 1440 })
  })

  it('no agranda una imagen chica', () => {
    expect(medidasAchicadas(800, 600)).toEqual({ ancho: 800, alto: 600 })
    expect(medidasAchicadas(1440, 900)).toEqual({ ancho: 1440, alto: 900 })
  })
})

function simularCanvas() {
  const dibujar = vi.fn()
  const contexto = { drawImage: dibujar, fillStyle: '', fillRect: vi.fn() }
  vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(
    contexto as unknown as CanvasRenderingContext2D,
  )
  const aBlob = vi
    .spyOn(HTMLCanvasElement.prototype, 'toBlob')
    .mockImplementation(function (this: HTMLCanvasElement, listo: BlobCallback, tipo?: string) {
      listo(new Blob([`${this.width}x${this.height}`], { type: tipo }))
    })
  return { dibujar, aBlob }
}

function simularBitmap(width: number, height: number) {
  const bitmap = { width, height, close: vi.fn() }
  vi.stubGlobal('createImageBitmap', vi.fn(async () => bitmap))
  return bitmap
}

describe('achicarImagen', () => {
  it('achica una captura grande con canvas y la pasa a JPEG', async () => {
    const bitmap = simularBitmap(2880, 1800)
    const { dibujar, aBlob } = simularCanvas()
    const archivo = new File(['png'], 'captura.png', { type: 'image/png' })

    const resultado = await achicarImagen(archivo)

    expect(dibujar).toHaveBeenCalledWith(bitmap, 0, 0, 1440, 900)
    expect(aBlob).toHaveBeenCalledTimes(1)
    expect(resultado.type).toBe('image/jpeg')
    expect(await resultado.text()).toBe('1440x900')
    expect(bitmap.close).toHaveBeenCalled()
  })

  it('deja tal cual una imagen chica en un formato que acepta el servidor', async () => {
    simularBitmap(1200, 800)
    const { dibujar } = simularCanvas()
    const archivo = new File(['png'], 'chica.png', { type: 'image/png' })

    const resultado = await achicarImagen(archivo)

    expect(resultado).toBe(archivo)
    expect(dibujar).not.toHaveBeenCalled()
  })

  it('convierte a JPEG un formato que el servidor no acepta, aunque sea chico', async () => {
    simularBitmap(1000, 750)
    const { dibujar } = simularCanvas()
    const archivo = new File(['heic'], 'foto.heic', { type: 'image/heic' })

    const resultado = await achicarImagen(archivo)

    expect(dibujar).toHaveBeenCalledWith(expect.anything(), 0, 0, 1000, 750)
    expect(resultado.type).toBe('image/jpeg')
  })

  it('avisa si el archivo no es una imagen', async () => {
    const archivo = new File(['hola'], 'nota.txt', { type: 'text/plain' })
    await expect(achicarImagen(archivo)).rejects.toThrow(/imagen/i)
  })
})
