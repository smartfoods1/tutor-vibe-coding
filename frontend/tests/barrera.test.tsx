import { render, screen } from '@testing-library/react'
import { Suspense } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Barrera, lazyConRecarga } from '../src/componentes/Barrera.tsx'

afterEach(() => {
  sessionStorage.clear()
  vi.restoreAllMocks()
})

function Pagina() {
  return <p>Página cargada</p>
}

function montar(Componente: React.ComponentType) {
  render(
    <Barrera>
      <Suspense fallback={<p>Cargando</p>}>
        <Componente />
      </Suspense>
    </Barrera>,
  )
}

describe('lazyConRecarga', () => {
  it('carga la página normalmente', async () => {
    montar(lazyConRecarga(async () => ({ default: Pagina })))
    expect(await screen.findByText('Página cargada')).toBeInTheDocument()
  })

  it('si el archivo de la página ya no existe, recarga una sola vez', async () => {
    const recargar = vi.fn()
    montar(lazyConRecarga(() => Promise.reject(new TypeError('Failed to fetch dynamically imported module')), recargar))
    await vi.waitFor(() => expect(recargar).toHaveBeenCalledTimes(1))
    expect(sessionStorage.getItem('vibe-recargado')).toBe('1')
  })

  it('si ya recargó y sigue fallando, muestra el aviso para recargar', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    sessionStorage.setItem('vibe-recargado', '1')
    const recargar = vi.fn()
    montar(lazyConRecarga(() => Promise.reject(new TypeError('Failed to fetch')), recargar))
    expect(await screen.findByRole('button', { name: /recargar la página/i })).toBeInTheDocument()
    expect(recargar).not.toHaveBeenCalled()
  })
})
