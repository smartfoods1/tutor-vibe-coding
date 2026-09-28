import { useEffect, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { NOMBRE_CURSO } from '../lib/marca.ts'

interface Props {
  /** Para la pestaña del navegador. */
  titulo?: string
  /** "privada": muestra el acceso a Inicio; "publica": muestra Entrar; "ninguna": solo el nombre. */
  navegacion?: 'privada' | 'publica' | 'ninguna'
  children: ReactNode
}

export default function Pagina({ titulo, navegacion = 'ninguna', children }: Props) {
  useEffect(() => {
    document.title = titulo ? `${titulo} · ${NOMBRE_CURSO}` : NOMBRE_CURSO
  }, [titulo])

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="border-b border-linea">
        <div className="mx-auto flex min-h-14 max-w-2xl items-center justify-between gap-4 px-4 py-2">
          <Link to={navegacion === 'privada' ? '/inicio' : '/'} className="font-semibold no-underline">
            {NOMBRE_CURSO}
          </Link>
          {navegacion === 'privada' && (
            <Link to="/inicio" className="enlace">
              Inicio
            </Link>
          )}
          {navegacion === 'publica' && (
            <Link to="/entrar" className="enlace">
              Entrar
            </Link>
          )}
        </div>
      </header>
      <main className="mx-auto w-full max-w-2xl flex-1 px-4 pt-6 pb-10">{children}</main>
      <Pie />
    </div>
  )
}

export function Pie() {
  return (
    <footer className="border-t border-linea">
      <div className="mx-auto flex max-w-2xl flex-wrap gap-x-6 gap-y-2 px-4 py-5 text-[0.95rem] text-marron">
        <Link to="/privacidad" className="underline">
          Privacidad
        </Link>
        <Link to="/galeria" className="underline">
          Galería
        </Link>
      </div>
    </footer>
  )
}
