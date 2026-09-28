import { useEffect, useRef, useState } from 'react'
import { alcanceDeTope, api, type Alcance } from '../lib/api.ts'
import { frasesParaVoz } from '../lib/voz.ts'
import { mensajeDe } from './Estados.tsx'

type ContextoAudio = typeof AudioContext

function claseAudio(): ContextoAudio | undefined {
  const w = window as Window & { webkitAudioContext?: ContextoAudio }
  return window.AudioContext ?? w.webkitAudioContext
}

function IconoParlante() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M4 9v6h4l5 4V5L8 9H4Z" strokeLinejoin="round" />
      <path d="M16.5 8.5a5 5 0 0 1 0 7" strokeLinecap="round" />
    </svg>
  )
}

interface Props {
  texto: string
  alTope?: (alcance: Alcance) => void
}

/**
 * La voz del tutor viene apagada: este botón la pide de a una frase (hasta 600 caracteres) y la
 * reproduce con Web Audio, que queda habilitado por el toque aunque el audio llegue después.
 */
export default function Escuchar({ texto, alTope }: Props) {
  const [estado, setEstado] = useState<'quieto' | 'preparando' | 'sonando'>('quieto')
  const [error, setError] = useState<string | null>(null)
  const contexto = useRef<AudioContext | null>(null)
  const fuente = useRef<AudioBufferSourceNode | null>(null)
  const control = useRef<AbortController | null>(null)

  const parar = () => {
    control.current?.abort()
    control.current = null
    try {
      fuente.current?.stop()
    } catch {
      /* ya había terminado */
    }
    fuente.current = null
    setEstado('quieto')
  }

  useEffect(
    () => () => {
      control.current?.abort()
      try {
        fuente.current?.stop()
      } catch {
        /* nada */
      }
      void contexto.current?.close().catch(() => undefined)
    },
    [],
  )

  async function escuchar() {
    setError(null)
    const Clase = claseAudio()
    if (!Clase) {
      setError('Tu navegador no puede reproducir la voz.')
      return
    }
    const ctx = contexto.current ?? new Clase()
    contexto.current = ctx
    void ctx.resume().catch(() => undefined)

    const frases = frasesParaVoz(texto)
    if (frases.length === 0) return
    const propio = new AbortController()
    control.current = propio
    setEstado('preparando')

    const pedirFrase = (frase: string) => {
      const pedido = api.hablar(frase, propio.signal)
      pedido.catch(() => undefined)
      return pedido
    }

    try {
      let siguiente = pedirFrase(frases[0])
      for (let i = 0; i < frases.length; i++) {
        const audio = await siguiente
        if (i + 1 < frases.length) siguiente = pedirFrase(frases[i + 1])
        const buffer = await ctx.decodeAudioData(await audio.arrayBuffer())
        if (propio.signal.aborted) return
        setEstado('sonando')
        await new Promise<void>((listo) => {
          const nodo = ctx.createBufferSource()
          nodo.buffer = buffer
          nodo.connect(ctx.destination)
          nodo.onended = () => listo()
          fuente.current = nodo
          nodo.start()
        })
        if (propio.signal.aborted) return
      }
      setEstado('quieto')
    } catch (e) {
      if (propio.signal.aborted) return
      setEstado('quieto')
      const alcance = alcanceDeTope(e)
      if (alcance) alTope?.(alcance)
      else setError(e instanceof DOMException ? 'No se pudo reproducir la voz.' : mensajeDe(e))
    }
  }

  return (
    <div className="mt-2 flex flex-wrap items-center gap-3">
      {estado === 'quieto' ? (
        <button type="button" className="boton boton-sec boton-chico" onClick={() => void escuchar()}>
          <IconoParlante />
          Escuchar
        </button>
      ) : (
        <>
          <button type="button" className="boton boton-sec boton-chico" onClick={parar}>
            Parar
          </button>
          {estado === 'preparando' && (
            <span role="status" className="text-marron">
              <span className="puntos">Preparando la voz</span>
            </span>
          )}
        </>
      )}
      {error && (
        <span role="alert" className="text-oxido">
          {error}
        </span>
      )}
    </div>
  )
}
