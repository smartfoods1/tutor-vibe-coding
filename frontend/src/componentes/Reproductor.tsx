import { useState } from 'react'
import type { Audio } from '../lib/api.ts'
import { useConfig } from './Configuracion.tsx'
import { Cargando } from './Estados.tsx'
import TextoMd from './TextoMd.tsx'

/** Solo acepta rutas del mismo sitio (/audios/...) para no cargar nada de afuera. */
function rutaLocal(url: string | null | undefined): string | null {
  if (!url || !url.startsWith('/') || url.startsWith('//')) return null
  return url
}

function sinFrontmatter(texto: string): string {
  return texto.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, '')
}

/** El audio del autor del curso para el módulo, con su transcripción. Se puede saltear. */
export default function Reproductor({ audio }: { audio: Audio }) {
  const { autorNombre } = useConfig()
  const [abierta, setAbierta] = useState(false)
  const [transcripcion, setTranscripcion] = useState<string | null>(null)
  const [error, setError] = useState(false)
  const url = rutaLocal(audio.url)
  const rutaTranscripcion = rutaLocal(audio.transcripcion)
  if (!url) return null

  async function alternar() {
    const abrir = !abierta
    setAbierta(abrir)
    if (!abrir || transcripcion !== null || !rutaTranscripcion) return
    setError(false)
    try {
      const respuesta = await fetch(rutaTranscripcion, { credentials: 'same-origin' })
      if (!respuesta.ok) throw new Error(String(respuesta.status))
      setTranscripcion(sinFrontmatter(await respuesta.text()))
    } catch {
      setError(true)
    }
  }

  return (
    <section aria-labelledby={`audio-${audio.modulo}`} className="tarjeta mt-6">
      <p className="etiqueta">{autorNombre ? `Audio de ${autorNombre}` : 'Audio del autor'}</p>
      <h2 id={`audio-${audio.modulo}`} className="mt-1 text-[1.25rem] font-bold">
        {autorNombre ? `Antes de empezar, escuchá a ${autorNombre}` : 'Antes de empezar, escuchá al autor del curso'}
      </h2>
      <p className="mt-1 text-marron">Dura unos minutos. Si preferís, podés saltearlo o leerlo.</p>
      <audio controls preload="metadata" src={url} className="mt-4 w-full">
        Tu navegador no puede reproducir este audio.
      </audio>
      {rutaTranscripcion && (
        <>
          <button
            type="button"
            className="enlace mt-3"
            aria-expanded={abierta}
            onClick={() => void alternar()}
          >
            {abierta ? 'Ocultar la transcripción' : 'Leer la transcripción'}
          </button>
          {abierta && (
            <div className="mt-3 border-t border-linea pt-3">
              {error ? (
                <p className="text-oxido">No pudimos cargar la transcripción. Probá de nuevo en un rato.</p>
              ) : transcripcion === null ? (
                <Cargando />
              ) : (
                <TextoMd texto={transcripcion} bajarTitulos />
              )}
            </div>
          )}
        </>
      )}
    </section>
  )
}
