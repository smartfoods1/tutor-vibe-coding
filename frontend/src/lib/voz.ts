/** Prepara el texto del tutor para escucharlo de a una frase (máx. 600 caracteres por pedido). */

export const MAX_FRASE = 600

export function textoPlano(markdown: string): string {
  return markdown
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/!\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/`([^`]*)`/g, '$1')
    .replace(/^\s{0,3}#{1,6}\s+/gm, '')
    .replace(/^\s{0,3}>\s?/gm, '')
    .replace(/^\s*(?:[-*+]|\d+[.)])\s+/gm, '')
    .replace(/(\*\*|__)(.*?)\1/g, '$2')
    .replace(/(^|[^\w*])[*_]([^*_\n]+)[*_](?=[^\w*]|$)/g, '$1$2')
    .replace(/[ \t]+/g, ' ')
    .split('\n')
    .map((linea) => linea.trim())
    .join('\n')
    .trim()
}

function partirLarga(frase: string, maximo: number): string[] {
  const partes: string[] = []
  let actual = ''
  for (const palabra of frase.split(/\s+/)) {
    if (!palabra) continue
    if (palabra.length > maximo) {
      if (actual) partes.push(actual)
      for (let i = 0; i < palabra.length; i += maximo) partes.push(palabra.slice(i, i + maximo))
      actual = ''
      continue
    }
    const junto = actual ? `${actual} ${palabra}` : palabra
    if (junto.length > maximo) {
      partes.push(actual)
      actual = palabra
    } else {
      actual = junto
    }
  }
  if (actual) partes.push(actual)
  return partes
}

export function frasesParaVoz(markdown: string, maximo = MAX_FRASE): string[] {
  const plano = textoPlano(markdown)
  const frases: string[] = []
  for (const bloque of plano.split(/\n+/)) {
    const limpio = bloque.trim()
    if (!limpio) continue
    const partes = limpio.match(/[^.!?…]+(?:[.!?…]+["”»)]*|$)/g) ?? [limpio]
    for (const parte of partes) {
      const frase = parte.trim()
      if (!frase) continue
      if (frase.length <= maximo) frases.push(frase)
      else frases.push(...partirLarga(frase, maximo))
    }
  }
  return frases
}
