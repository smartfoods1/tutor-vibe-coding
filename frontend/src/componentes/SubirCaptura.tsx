import { useRef, useState } from 'react'
import { achicarImagen } from '../lib/captura.ts'
import { mensajeDe } from './Estados.tsx'

interface Props {
  alElegir: (imagen: Blob) => void
  deshabilitado?: boolean
}

function IconoImagen() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <circle cx="9" cy="10" r="2" />
      <path d="m21 16-5-5-9 9" strokeLinejoin="round" />
    </svg>
  )
}

/** Elige una captura (o una foto de la pantalla) y la achica antes de mandarla. */
export default function SubirCaptura({ alElegir, deshabilitado = false }: Props) {
  const entrada = useRef<HTMLInputElement>(null)
  const [preparando, setPreparando] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function elegir(archivo: File | undefined) {
    if (!archivo) return
    setError(null)
    setPreparando(true)
    try {
      alElegir(await achicarImagen(archivo))
    } catch (e) {
      setError(mensajeDe(e))
    } finally {
      setPreparando(false)
      if (entrada.current) entrada.current.value = ''
    }
  }

  return (
    <div className="contents">
      <input
        ref={entrada}
        type="file"
        accept="image/*"
        className="sr-only"
        tabIndex={-1}
        aria-hidden="true"
        onChange={(e) => void elegir(e.target.files?.[0])}
      />
      <button
        type="button"
        className="boton boton-sec"
        onClick={() => entrada.current?.click()}
        disabled={deshabilitado || preparando}
      >
        <IconoImagen />
        {preparando ? 'Preparando…' : 'Captura'}
      </button>
      {error && (
        <p role="alert" className="basis-full text-oxido">
          {error}
        </p>
      )}
    </div>
  )
}
