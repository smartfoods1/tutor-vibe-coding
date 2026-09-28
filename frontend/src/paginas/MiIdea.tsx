import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Cargando, MensajeError, mensajeDe } from '../componentes/Estados.tsx'
import Pagina from '../componentes/Pagina.tsx'
import TextoMd from '../componentes/TextoMd.tsx'
import { ErrorApi, api, type Idea } from '../lib/api.ts'
import { useCarga } from '../lib/useCarga.ts'

const MAX_IDEA = 6000
const MAX_QUE_SIGUE = 3000

/** Solo si no carga la plantilla del curso (GET /api/idea/plantilla): los mismos títulos, sin ayudas. */
const PLANTILLA_MINIMA = `# El nombre de tu idea

## Qué es

## Para quién

## Qué siento cuando la imagino funcionando y por qué me importa

## La versión más chica que ya valdría la pena

## El molde

## Lo que la máquina no puede adivinar

## Sé que funciona si
`

async function cargarPlantilla(): Promise<string> {
  try {
    const { texto_md } = await api.plantillaIdea()
    return typeof texto_md === 'string' && texto_md.trim() ? texto_md : PLANTILLA_MINIMA
  } catch {
    return PLANTILLA_MINIMA
  }
}

function fecha(iso: string): string {
  const momento = new Date(iso)
  if (Number.isNaN(momento.getTime())) return ''
  return momento.toLocaleDateString('es-AR', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'America/Argentina/Buenos_Aires' })
}

/** GET /api/idea da 404 si todavía no hay idea: eso no es un error para mostrar. */
async function cargarIdea(): Promise<Idea | null> {
  try {
    return await api.idea()
  } catch (e) {
    if (e instanceof ErrorApi && e.status === 404) return null
    throw e
  }
}

export default function MiIdea() {
  const { datos: idea, error, cargando, recargar, poner } = useCarga(cargarIdea)
  const [editando, setEditando] = useState(false)
  const [texto, setTexto] = useState('')
  const [queSigue, setQueSigue] = useState('')
  const [guardando, setGuardando] = useState(false)
  const [falla, setFalla] = useState<string | null>(null)
  const [aviso, setAviso] = useState<string | null>(null)
  const [bajando, setBajando] = useState(false)
  const [preparando, setPreparando] = useState(false)

  function editar(base: Idea) {
    setTexto(base.texto_md)
    setQueSigue(base.que_sigue_md ?? '')
    setFalla(null)
    setAviso(null)
    setEditando(true)
  }

  async function escribirDeCero() {
    setPreparando(true)
    const plantilla = await cargarPlantilla()
    setPreparando(false)
    setTexto(plantilla)
    setQueSigue('')
    setFalla(null)
    setAviso(null)
    setEditando(true)
  }

  async function guardar(evento: FormEvent) {
    evento.preventDefault()
    if (!texto.trim()) {
      setFalla('Tu idea no puede quedar vacía.')
      return
    }
    setGuardando(true)
    setFalla(null)
    try {
      const { version } = await api.guardarIdea(texto, queSigue)
      poner({
        version,
        texto_md: texto,
        que_sigue_md: queSigue || null,
        autor: 'alumno',
        creado: new Date().toISOString(),
      })
      setEditando(false)
      setAviso('Guardamos tu idea. Las versiones anteriores quedan guardadas también.')
      void recargar()
    } catch (e) {
      setFalla(mensajeDe(e))
    } finally {
      setGuardando(false)
    }
  }

  async function bajar() {
    setBajando(true)
    setFalla(null)
    try {
      await api.descargarIdea()
    } catch (e) {
      setFalla(mensajeDe(e))
    } finally {
      setBajando(false)
    }
  }

  let contenido
  if (cargando) {
    contenido = <Cargando />
  } else if (error && !idea) {
    contenido = <MensajeError mensaje={mensajeDe(error)} alReintentar={() => void recargar()} />
  } else if (editando) {
    contenido = (
      <form onSubmit={guardar} className="mt-6 space-y-6">
        <div>
          <label htmlFor="idea-texto" className="block font-semibold">
            Tu idea
          </label>
          <p className="text-marron">Podés usar # para el título y ** para resaltar, o escribir sin nada.</p>
          <textarea
            id="idea-texto"
            className="campo mt-2 min-h-[18rem]"
            maxLength={MAX_IDEA}
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
          />
          <p className="mt-1 text-marron">
            {texto.length} de {MAX_IDEA} caracteres
          </p>
        </div>
        <div>
          <label htmlFor="idea-que-sigue" className="block font-semibold">
            Qué sigue
          </label>
          <p className="text-marron">Lo que querés sumar más adelante, para que no se pierda.</p>
          <textarea
            id="idea-que-sigue"
            className="campo mt-2 min-h-[8rem]"
            maxLength={MAX_QUE_SIGUE}
            value={queSigue}
            onChange={(e) => setQueSigue(e.target.value)}
          />
        </div>
        {falla && <MensajeError mensaje={falla} />}
        <div className="flex flex-col gap-3 sm:flex-row">
          <button type="submit" className="boton flex-1" disabled={guardando}>
            {guardando ? 'Guardando…' : 'Guardar'}
          </button>
          <button type="button" className="boton boton-sec" onClick={() => setEditando(false)} disabled={guardando}>
            Cancelar
          </button>
        </div>
      </form>
    )
  } else if (!idea) {
    contenido = (
      <div className="mt-6 space-y-4">
        <p>Todavía no hay una idea guardada. La armás con el tutor en el módulo 2.</p>
        <Link to="/modulo/2" className="boton w-full">
          Ir al módulo 2
        </Link>
        <button type="button" className="enlace" onClick={() => void escribirDeCero()} disabled={preparando}>
          {preparando ? 'Preparando la plantilla…' : 'Prefiero escribirla por mi cuenta'}
        </button>
      </div>
    )
  } else {
    contenido = (
      <>
        <p className="mt-2 text-marron">
          Versión {idea.version}
          {fecha(idea.creado) && ` · ${fecha(idea.creado)}`}
        </p>
        {aviso && (
          <div role="status" className="aviso aviso-logro mt-4">
            <p>{aviso}</p>
          </div>
        )}
        <article className="tarjeta mt-6">
          <TextoMd texto={idea.texto_md} bajarTitulos />
          {idea.que_sigue_md && (
            <div className="mt-6 border-t border-linea pt-4">
              <h2 className="text-[1.25rem] font-bold">Qué sigue</h2>
              <div className="mt-2">
                <TextoMd texto={idea.que_sigue_md} bajarTitulos />
              </div>
            </div>
          )}
        </article>
        {falla && (
          <div className="mt-4">
            <MensajeError mensaje={falla} />
          </div>
        )}
        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <button type="button" className="boton flex-1" onClick={() => void bajar()} disabled={bajando}>
            {bajando ? 'Bajando…' : 'Bajar mi idea (mi-idea.md)'}
          </button>
          <button type="button" className="boton boton-sec" onClick={() => editar(idea)}>
            Editar
          </button>
        </div>
      </>
    )
  }

  return (
    <Pagina titulo="Mi idea" navegacion="privada">
      <p className="etiqueta">Mi idea en una página</p>
      <h1 className="mt-1 text-[2rem] font-bold">Mi idea</h1>
      {contenido}
    </Pagina>
  )
}
