import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import Markdown from '../src/componentes/Markdown.tsx'

describe('Markdown', () => {
  it('no carga imágenes: muestra solo el texto alternativo entre corchetes', () => {
    const { container } = render(<Markdown texto={'Mirá esto: ![x](https://afuera.example/p.png) y seguí.'} />)
    expect(container.querySelector('img')).toBeNull()
    expect(screen.getByText(/\[x\]/)).toBeInTheDocument()
    expect(container.innerHTML).not.toContain('afuera.example')
  })

  it('una imagen sin texto alternativo tampoco se carga', () => {
    const { container } = render(<Markdown texto={'![](https://afuera.example/rastreo.gif?dato=1)'} />)
    expect(container.querySelector('img')).toBeNull()
    expect(container.innerHTML).not.toContain('afuera.example')
  })

  it('una imagen dentro de un link deja el link con el texto alternativo', () => {
    const { container } = render(<Markdown texto={'[![Mi página](https://afuera.example/p.png)](https://mi.example)'} />)
    expect(container.querySelector('img')).toBeNull()
    expect(screen.getByRole('link', { name: '[Mi página]' })).toHaveAttribute('href', 'https://mi.example')
  })

  it('los links abren aparte y sin referencia', () => {
    render(<Markdown texto={'[Netlify](https://netlify.com)'} />)
    const link = screen.getByRole('link', { name: 'Netlify' })
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })
})
