import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from '../src/App.tsx'
import { NOMBRE_CURSO } from '../src/lib/marca.ts'
import { nombreCurso } from '../src/lib/nombre.ts'
import { json, simularFetch } from './ayudas.ts'

afterEach(() => vi.unstubAllGlobals())

function abrir(ruta: string) {
  render(
    <MemoryRouter initialEntries={[ruta]}>
      <App />
    </MemoryRouter>,
  )
}

describe('App', () => {
  it('muestra el nombre del curso (el de VITE_NOMBRE_CURSO) y la portada', async () => {
    simularFetch({
      'GET /api/config': json({ turnstile_site_key: null, aviso_prueba: false }),
      'GET /api/legal/consentimientos': json({ version: 'x', textos: {}, texto_md: '' }),
      'GET /api/yo': json({ detalle: 'no' }, 401),
    })
    abrir('/')
    expect(await screen.findByRole('heading', { level: 1, name: /de lo que imaginás a algo que existe/i })).toBeInTheDocument()
    expect(NOMBRE_CURSO).toBe(nombreCurso(import.meta.env.VITE_NOMBRE_CURSO))
    expect(screen.getAllByText(NOMBRE_CURSO).length).toBeGreaterThan(0)
    expect(document.title).toContain(NOMBRE_CURSO)
  })

  it('una ruta que no existe ofrece volver al principio', async () => {
    simularFetch({ 'GET /api/config': json({ turnstile_site_key: null, aviso_prueba: false }) })
    abrir('/no-existe')
    expect(await screen.findByText(/no encontramos esta página/i)).toBeInTheDocument()
  })

  it('sin sesión, una página privada lleva a entrar', async () => {
    simularFetch({
      'GET /api/config': json({ turnstile_site_key: null, aviso_prueba: false }),
      'GET /api/yo': json({ detalle: 'Tu sesión venció. Entrá de nuevo con tu mail.' }, 401),
    })
    abrir('/inicio')
    expect(await screen.findByRole('button', { name: /mandame el código/i })).toBeInTheDocument()
  })
})
