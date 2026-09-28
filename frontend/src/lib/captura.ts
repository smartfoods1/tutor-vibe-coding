/** Achica las capturas antes de subirlas: 1.440 px en el lado largo (unos 1.700 tokens). */

export const LADO_MAXIMO = 1440
const FORMATOS_ACEPTADOS = new Set(['image/png', 'image/jpeg', 'image/webp'])
const MAX_BYTES_SIN_TOCAR = 4 * 1024 * 1024
const CALIDAD_JPEG = 0.85

export function medidasAchicadas(ancho: number, alto: number, maximo = LADO_MAXIMO) {
  const largo = Math.max(ancho, alto)
  if (largo <= maximo) return { ancho, alto }
  const escala = maximo / largo
  return { ancho: Math.round(ancho * escala), alto: Math.round(alto * escala) }
}

interface Dibujable {
  width: number
  height: number
  close?: () => void
}

async function cargar(archivo: Blob): Promise<{ imagen: CanvasImageSource & Dibujable; liberar: () => void }> {
  if (typeof createImageBitmap === 'function') {
    try {
      const bitmap = await createImageBitmap(archivo, { imageOrientation: 'from-image' })
      return { imagen: bitmap, liberar: () => bitmap.close?.() }
    } catch {
      /* sigue con <img> */
    }
  }
  const url = URL.createObjectURL(archivo)
  try {
    const imagen = new Image()
    imagen.decoding = 'async'
    await new Promise<void>((listo, fallo) => {
      imagen.onload = () => listo()
      imagen.onerror = () => fallo(new Error('No se pudo leer la imagen.'))
      imagen.src = url
    })
    const dibujable = Object.assign(imagen, { width: imagen.naturalWidth, height: imagen.naturalHeight })
    return { imagen: dibujable, liberar: () => URL.revokeObjectURL(url) }
  } catch (error) {
    URL.revokeObjectURL(url)
    throw error
  }
}

/**
 * Devuelve la imagen lista para subir: si ya es chica y en un formato que acepta el servidor,
 * la misma; si no, redibujada en canvas a 1.440 px en el lado largo y en JPEG.
 */
export async function achicarImagen(archivo: File | Blob): Promise<Blob> {
  if (!archivo.type.startsWith('image/')) {
    throw new Error('Ese archivo no es una imagen. Probá con una captura o una foto de la pantalla.')
  }
  let cargada
  try {
    cargada = await cargar(archivo)
  } catch {
    throw new Error('No pudimos abrir esa imagen. Probá con otra captura.')
  }
  const { imagen, liberar } = cargada
  try {
    const { ancho, alto } = medidasAchicadas(imagen.width, imagen.height)
    const yaSirve =
      FORMATOS_ACEPTADOS.has(archivo.type) &&
      ancho === imagen.width &&
      alto === imagen.height &&
      archivo.size <= MAX_BYTES_SIN_TOCAR
    if (yaSirve) return archivo

    const lienzo = document.createElement('canvas')
    lienzo.width = ancho
    lienzo.height = alto
    const contexto = lienzo.getContext('2d')
    if (!contexto) throw new Error('Tu navegador no pudo preparar la imagen.')
    // Fondo blanco: las capturas con transparencia quedan legibles en JPEG.
    contexto.fillStyle = '#ffffff'
    contexto.fillRect(0, 0, ancho, alto)
    contexto.drawImage(imagen, 0, 0, ancho, alto)
    return await new Promise<Blob>((listo, fallo) => {
      lienzo.toBlob(
        (blob) => (blob ? listo(blob) : fallo(new Error('Tu navegador no pudo preparar la imagen.'))),
        'image/jpeg',
        CALIDAD_JPEG,
      )
    })
  } finally {
    liberar()
  }
}
