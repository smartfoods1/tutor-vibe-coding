/**
 * El sitio va a tener una CSP estricta ("script-src 'self'", "style-src 'self'", sin otros dominios
 * salvo Cloudflare Turnstile cuando está activado). Estos tests cuidan que la base del sitio no pida
 * nada afuera ni traiga scripts o estilos en línea.
 */
/// <reference types="node" />
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import indexHtml from '../index.html?raw'
import paquete from '../package.json?raw'
import mainTsx from '../src/main.tsx?raw'
import viteConfig from '../vite.config.ts?raw'
import { NOMBRE_POR_DEFECTO } from '../src/lib/nombre.ts'

const ARCHIVOS: Record<string, string> = {
  'index.html': indexHtml,
  'src/main.tsx': mainTsx,
  'vite.config.ts': viteConfig,
}
const leer = (archivo: string) => ARCHIVOS[archivo]
// Vite no deja importar archivos .env* (con razón): este se lee del disco.
const envEjemplo = readFileSync(resolve(import.meta.dirname, '../.env.example'), 'utf-8')

describe('el sitio no depende de otros dominios', () => {
  it('index.html no pide fuentes ni nada a otros dominios', () => {
    const html = leer('index.html')
    expect(html).not.toMatch(/fonts\.googleapis\.com|fonts\.gstatic\.com/)
    // Ningún src o href absoluto a otro sitio (los links a recursos van con ruta relativa al sitio).
    expect(html).not.toMatch(/(?:src|href)\s*=\s*["']?(?:https?:)?\/\//i)
  })

  it('index.html no tiene scripts ni estilos en línea', () => {
    const html = leer('index.html')
    const scripts = [...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)]
    expect(scripts.length).toBeGreaterThan(0)
    for (const [, atributos, cuerpo] of scripts) {
      expect(atributos).toMatch(/\bsrc=/)
      expect(cuerpo.trim()).toBe('')
    }
    expect(html).not.toMatch(/<style\b/i)
    expect(html).not.toMatch(/\sstyle\s*=/i)
    expect(html).not.toMatch(/\son[a-z]+\s*=/i)
  })

  it('las fuentes salen de los paquetes @fontsource, no de Google Fonts', () => {
    const entrada = leer('src/main.tsx')
    expect(entrada).toMatch(/@fontsource\/source-serif-4/)
    expect(entrada).toMatch(/@fontsource\/ibm-plex-mono/)
    const config = leer('vite.config.ts')
    expect(config).not.toMatch(/googleapis|gstatic/)
  })

  it('el service worker se registra con un archivo, no con un script en línea', () => {
    const config = leer('vite.config.ts')
    expect(config).toMatch(/injectRegister:\s*['"]script['"]/)
  })
})

describe('el nombre del curso tiene una sola fuente', () => {
  it('index.html toma el nombre de VITE_NOMBRE_CURSO', () => {
    const html = leer('index.html')
    expect(html).toMatch(/<title>%VITE_NOMBRE_CURSO%<\/title>/)
    expect(html).not.toContain(NOMBRE_POR_DEFECTO)
  })

  it('el manifest usa el mismo nombre, leído con loadEnv', () => {
    const config = leer('vite.config.ts')
    expect(config).toMatch(/loadEnv\(/)
    expect(config).toMatch(/nombreCurso\(\s*env\.VITE_NOMBRE_CURSO\s*\)/)
    expect(config).toMatch(/name:\s*nombre\b/)
    expect(config).not.toContain(NOMBRE_POR_DEFECTO)
  })

  it('.env.example documenta VITE_NOMBRE_CURSO con el nombre por defecto', () => {
    expect(envEjemplo).toMatch(new RegExp(`^VITE_NOMBRE_CURSO=${NOMBRE_POR_DEFECTO}$`, 'm'))
  })
})

describe('el frontend se puede publicar como código abierto', () => {
  it('declara la licencia MIT', () => {
    expect(JSON.parse(paquete).license).toBe('MIT')
  })

  // Todo el código del frontend (y lo que arma el sitio) queda en el repo público.
  const codigo: Record<string, string> = {
    ...import.meta.glob<string>('../src/**/*.{ts,tsx,css}', { query: '?raw', import: 'default', eager: true }),
    'index.html': indexHtml,
    'vite.config.ts': viteConfig,
    '.env.example': envEjemplo,
  }

  it('no nombra a una persona ni a un servicio de novedades en textos fijos', () => {
    expect(Object.keys(codigo).length).toBeGreaterThan(20)
    for (const [archivo, texto] of Object.entries(codigo)) {
      expect(texto, archivo).not.toMatch(/andr[eé]s/i)
      expect(texto, archivo).not.toMatch(/substack/i)
    }
  })

  it('no tiene rutas de una compu ni IPs propias', () => {
    for (const [archivo, texto] of Object.entries(codigo)) {
      expect(texto, archivo).not.toMatch(/\/Users\//)
      // La única IP es la del proxy local de desarrollo.
      const ips = texto.match(/\b\d{1,3}(?:\.\d{1,3}){3}\b/g) ?? []
      expect(ips.filter((ip) => ip !== '127.0.0.1'), archivo).toEqual([])
      // Tampoco con guiones, como en los nombres que apuntan a una IP (1-2-3-4.algo). Se pide el
      // punto y la letra después para no confundirla con el trazo de un ícono (d="m21 16-5-5-9 9").
      expect(texto, archivo).not.toMatch(/\b\d{1,3}(?:-\d{1,3}){3}\.[a-z]/i)
    }
  })
})
