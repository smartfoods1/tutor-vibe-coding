import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from '../src/App.tsx'
import { json, llamadasA, simularFetch } from './ayudas.ts'

afterEach(() => vi.unstubAllGlobals())

const CONFIG = { 'GET /api/config': json({ turnstile_site_key: null, aviso_prueba: false }) }

const PASOS = {
  herramienta: 'claude',
  sistema: 'windows',
  texto_md:
    'Los pasos para Claude (la app de escritorio, pestaña Code) en una computadora con Windows.\n\n' +
    '## Antes de empezar\n\n1. Guardá esta carpeta en un lugar fijo.\n2. No borres nada.\n\n' +
    '## La primera vez\n\nPara arrancar la lección 4, escribí: `empecemos`\n',
}

function abrir() {
  render(
    <MemoryRouter initialEntries={['/seguir']}>
      <App />
    </MemoryRouter>,
  )
}

describe('Seguir', () => {
  it('muestra los pasos para la herramienta y la computadora elegidas, con lo que hay que escribir', async () => {
    simularFetch({ ...CONFIG, 'GET /api/kit/pasos': json(PASOS) })
    abrir()
    expect(await screen.findByRole('heading', { level: 1, name: /cómo seguir en tu computadora/i })).toBeInTheDocument()
    expect(await screen.findByRole('heading', { level: 2, name: 'Antes de empezar' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2, name: 'La primera vez' })).toBeInTheDocument()
    expect(screen.getByText('empecemos').tagName).toBe('CODE')
    expect(screen.getByText(/para claude en windows/i)).toBeInTheDocument()
  })

  it('ofrece volver al módulo 3 (para cerrarlo, bajar el kit de nuevo o cambiar la elección) y al inicio', async () => {
    simularFetch({ ...CONFIG, 'GET /api/kit/pasos': json(PASOS) })
    abrir()
    await screen.findByRole('heading', { level: 2, name: 'Antes de empezar' })
    // El LEEME manda "volver a la web para cerrar el módulo 3": ese camino tiene que estar a la vista.
    expect(screen.getByText(/si todavía te falta cerrar el módulo 3/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /^volver al módulo 3$/i })).toHaveAttribute('href', '/modulo/3')
    expect(screen.getByRole('link', { name: /^volver al inicio$/i })).toHaveAttribute('href', '/inicio')
  })

  it('si todavía no eligió herramienta y computadora, lo dice y lleva a elegirlas', async () => {
    simularFetch({
      ...CONFIG,
      'GET /api/kit/pasos': json(
        {
          detalle: 'Para ver cómo seguir en tu computadora todavía falta: Elegir tu herramienta: Codex o Claude.',
          falta: ['Elegir tu herramienta: Codex o Claude.'],
        },
        409,
      ),
    })
    abrir()
    expect(await screen.findByText(/todavía falta: elegir tu herramienta/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /elegir mi herramienta y mi computadora/i })).toHaveAttribute('href', '/modulo/3')
    expect(screen.queryByRole('heading', { level: 2 })).toBeNull()
  })

  it('si falla la carga, lo dice y deja reintentar', async () => {
    let intentos = 0
    const espia = simularFetch({
      ...CONFIG,
      'GET /api/kit/pasos': () => {
        intentos += 1
        return intentos === 1 ? json({ detalle: 'El kit no está disponible en este momento.' }, 503) : json(PASOS)
      },
    })
    abrir()
    expect(await screen.findByRole('alert')).toHaveTextContent(/no está disponible/i)
    fireEvent.click(screen.getByRole('button', { name: /reintentar/i }))
    expect(await screen.findByRole('heading', { level: 2, name: 'Antes de empezar' })).toBeInTheDocument()
    expect(llamadasA(espia, 'GET /api/kit/pasos')).toHaveLength(2)
  })
})
