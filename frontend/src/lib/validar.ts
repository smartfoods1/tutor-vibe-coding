export const MENSAJE_MAIL = 'Revisá el mail: no parece una dirección válida.'
export const MENSAJE_MAILS_CURSO = 'Para hacer el curso necesitamos mandarte mails del curso.'
// Igual que el mensaje del backend (backend/vibe_tutor/auth.py) para el 422 por consentimientos.
export const MENSAJE_TRANSFERENCIA =
  'El curso funciona con proveedores en Estados Unidos y Brasil; sin ese permiso no podemos darte el curso.'

const PATRON_EMAIL = /^[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}$/

export function normalizarEmail(email: string): string {
  return email.trim().toLowerCase()
}

export function emailValido(email: string): boolean {
  return email.length <= 320 && PATRON_EMAIL.test(email)
}

/** Deja un link listo para mandar: agrega https:// si falta; rechaza http:// y lo que no es un link. */
export function normalizarLink(valor: string): { url: string } | { error: string } {
  let url = valor.trim()
  if (!url) return { error: 'Pegá el link de tu página.' }
  if (/^http:\/\//i.test(url)) {
    return { error: 'El link tiene que empezar con https:// (con s). Copialo tal cual desde la barra del navegador.' }
  }
  if (!/^[a-z][a-z0-9+.-]*:\/\//i.test(url)) url = `https://${url}`
  let leido: URL
  try {
    leido = new URL(url)
  } catch {
    return { error: 'Eso no parece un link. Copialo tal cual desde la barra del navegador.' }
  }
  if (leido.protocol !== 'https:' || !leido.hostname.includes('.')) {
    return { error: 'Eso no parece un link. Copialo tal cual desde la barra del navegador.' }
  }
  if (url.length > 500) return { error: 'El link es demasiado largo.' }
  return { url }
}

export function esLinkSeguro(url: unknown): url is string {
  if (typeof url !== 'string') return false
  try {
    return new URL(url).protocol === 'https:'
  } catch {
    return false
  }
}
