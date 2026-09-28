import { useEffect, useRef, useState } from 'react'
import { alcanceDeTope, api, type Alcance } from '../lib/api.ts'
import { mensajeDe } from './Estados.tsx'

const MAX_SEGUNDOS = 180
const TIPOS = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus']

function tipoSoportado(): string | undefined {
  if (typeof MediaRecorder === 'undefined' || typeof MediaRecorder.isTypeSupported !== 'function') return undefined
  return TIPOS.find((tipo) => MediaRecorder.isTypeSupported(tipo))
}

export function microfonoDisponible(): boolean {
  return typeof MediaRecorder !== 'undefined' && typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia
}

interface Props {
  alTexto: (texto: string) => void
  alTope?: (alcance: Alcance) => void
  deshabilitado?: boolean
}

function IconoMicrofono() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="9" y="3" width="6" height="11" rx="3" />
      <path d="M5 11a7 7 0 0 0 14 0M12 18v3" strokeLinecap="round" />
    </svg>
  )
}

/** Dicta con el micrófono: graba, manda a transcribir y deja el texto en la caja para revisarlo. */
export default function Microfono({ alTexto, alTope, deshabilitado = false }: Props) {
  const [estado, setEstado] = useState<'quieto' | 'grabando' | 'transcribiendo'>('quieto')
  const [segundos, setSegundos] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const grabador = useRef<MediaRecorder | null>(null)
  const flujo = useRef<MediaStream | null>(null)
  const reloj = useRef<number | null>(null)

  const liberar = () => {
    if (reloj.current !== null) window.clearInterval(reloj.current)
    reloj.current = null
    flujo.current?.getTracks().forEach((pista) => pista.stop())
    flujo.current = null
  }

  useEffect(
    () => () => {
      if (grabador.current && grabador.current.state !== 'inactive') {
        grabador.current.onstop = null
        grabador.current.stop()
      }
      liberar()
    },
    [],
  )

  if (!microfonoDisponible()) return null

  async function transcribir(audio: Blob) {
    setEstado('transcribiendo')
    try {
      const texto = (await api.transcribir(audio)).trim()
      if (texto) alTexto(texto)
      else setError('No se entendió el audio. Probá de nuevo, más cerca del micrófono, o escribí.')
    } catch (e) {
      const alcance = alcanceDeTope(e)
      if (alcance) alTope?.(alcance)
      else setError(mensajeDe(e))
    } finally {
      setEstado('quieto')
    }
  }

  async function empezar() {
    setError(null)
    let stream: MediaStream
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {
      setError('No pudimos usar el micrófono. Revisá que el navegador tenga permiso, o escribí tu respuesta.')
      return
    }
    flujo.current = stream
    const tipo = tipoSoportado()
    const partes: Blob[] = []
    let rec: MediaRecorder
    try {
      rec = new MediaRecorder(stream, tipo ? { mimeType: tipo } : undefined)
    } catch {
      liberar()
      setError('Tu navegador no deja grabar audio. Escribí tu respuesta.')
      return
    }
    rec.ondataavailable = (evento) => {
      if (evento.data.size > 0) partes.push(evento.data)
    }
    rec.onstop = () => {
      liberar()
      const audio = new Blob(partes, { type: rec.mimeType || tipo || 'audio/webm' })
      if (audio.size === 0) {
        setEstado('quieto')
        setError('No se grabó nada. Probá de nuevo.')
        return
      }
      void transcribir(audio)
    }
    grabador.current = rec
    rec.start()
    setSegundos(0)
    setEstado('grabando')
    let transcurrido = 0
    reloj.current = window.setInterval(() => {
      transcurrido += 1
      setSegundos(transcurrido)
      if (transcurrido >= MAX_SEGUNDOS) terminar()
    }, 1000)
  }

  function terminar() {
    if (grabador.current && grabador.current.state !== 'inactive') grabador.current.stop()
  }

  const minutos = `${Math.floor(segundos / 60)}:${String(segundos % 60).padStart(2, '0')}`

  return (
    <div className="contents">
      {estado === 'grabando' ? (
        <button type="button" className="boton boton-sec border-oxido text-oxido" onClick={terminar}>
          <span aria-hidden="true" className="inline-block h-3 w-3 rounded-full bg-oxido motion-safe:animate-pulse" />
          Terminar ({minutos})
        </button>
      ) : (
        <button
          type="button"
          className="boton boton-sec"
          onClick={() => void empezar()}
          disabled={deshabilitado || estado === 'transcribiendo'}
        >
          <IconoMicrofono />
          {estado === 'transcribiendo' ? 'Pasando a texto…' : 'Hablar'}
        </button>
      )}
      {(estado === 'grabando' || error) && (
        <p role={error ? 'alert' : 'status'} className={`basis-full ${error ? 'text-oxido' : 'text-marron'}`}>
          {error ?? 'Grabando. Cuando termines, tocá Terminar. Después revisá el texto antes de enviarlo.'}
        </p>
      )}
    </div>
  )
}
