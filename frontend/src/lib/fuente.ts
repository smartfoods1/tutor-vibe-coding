/** La fuente de inscripción (?ref= de la landing): minúsculas, números y guiones, hasta 64. */

const CLAVE = 'vibe-fuente'

export function limpiarFuente(valor: string | null | undefined): string | null {
  if (!valor) return null
  const limpia = valor
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9-]/g, '')
    .slice(0, 64)
  return limpia || null
}

/** Lee ?ref= y lo recuerda en la pestaña, por si la persona pasa por otra página antes de inscribirse. */
export function fuenteDeLaVisita(busqueda: string): string | null {
  const deLaUrl = limpiarFuente(new URLSearchParams(busqueda).get('ref'))
  try {
    if (deLaUrl) {
      sessionStorage.setItem(CLAVE, deLaUrl)
      return deLaUrl
    }
    return limpiarFuente(sessionStorage.getItem(CLAVE))
  } catch {
    return deLaUrl
  }
}
