import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ErrorApi, api, type Idea } from '../lib/api.ts'
import { useCarga } from '../lib/useCarga.ts'
import { Cargando, MensajeError, mensajeDe } from './Estados.tsx'
import TextoMd from './TextoMd.tsx'

/** Lo que le llega al tutor cuando la persona toca cada botón: la guía del módulo 2 los nombra igual. */
export const RESPUESTA_ESTA_BIEN = 'Está bien así'
export const RESPUESTA_QUIERO_CAMBIAR = 'Quiero cambiar algo'

interface Props {
  /** Se muestra en gris hasta que el tutor termina de escribir. */
  deshabilitado: boolean
  alElegir: (texto: string) => void
}

/** GET /api/idea da 404 si todavía no hay idea. */
async function cargarIdea(): Promise<Idea | null> {
  try {
    return await api.idea()
  } catch (e) {
    if (e instanceof ErrorApi && e.status === 404) return null
    throw e
  }
}

/** La idea, leída dentro del chat. Se monta recién la primera vez que se abre el desplegable. */
function IdeaLeida() {
  const { datos: idea, error, cargando, recargar } = useCarga(cargarIdea)
  if (cargando) return <Cargando texto="Trayendo tu idea" />
  if (error && !idea) return <MensajeError mensaje={mensajeDe(error)} alReintentar={() => void recargar()} />
  if (!idea) return <p className="py-3 text-marron">Todavía no hay una idea guardada.</p>
  return (
    <article className="tarjeta mt-3">
      <TextoMd texto={idea.texto_md} bajarTitulos />
      {idea.que_sigue_md && (
        <div className="mt-4 border-t border-linea pt-3">
          <p className="font-semibold">Qué sigue</p>
          <div className="mt-1">
            <TextoMd texto={idea.que_sigue_md} bajarTitulos />
          </div>
        </div>
      )}
    </article>
  )
}

/**
 * Lo que ve la persona cuando el tutor guarda su idea en el módulo 2: la puede leer ahí mismo y
 * decir, con un toque, si la representa o quiere cambiar algo. Los dos botones le hablan al tutor.
 */
export default function IdeaGuardada({ deshabilitado, alElegir }: Props) {
  const [abierta, setAbierta] = useState(false)
  // Una vez pedida, la lectura queda montada (oculta al cerrar): al reabrir no vuelve a cargar.
  const [pedida, setPedida] = useState(false)
  const idLectura = 'idea-guardada-lectura'
  return (
    <div className="aviso aviso-logro">
      <p className="font-semibold">Tu idea quedó guardada.</p>
      <button
        type="button"
        className="enlace mt-2"
        aria-expanded={abierta}
        aria-controls={idLectura}
        onClick={() => {
          setAbierta((v) => !v)
          setPedida(true)
        }}
      >
        {abierta ? 'Ocultar mi idea' : 'Leer mi idea acá'}
      </button>
      <div id={idLectura} hidden={!abierta}>
        {pedida && <IdeaLeida />}
      </div>
      <p className="mt-3">¿Te representa? Tocá una opción o escribile al tutor.</p>
      <div className="mt-2 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          className="boton sm:flex-1"
          disabled={deshabilitado}
          onClick={() => alElegir(RESPUESTA_ESTA_BIEN)}
        >
          {RESPUESTA_ESTA_BIEN}
        </button>
        <button
          type="button"
          className="boton boton-sec sm:flex-1"
          disabled={deshabilitado}
          onClick={() => alElegir(RESPUESTA_QUIERO_CAMBIAR)}
        >
          {RESPUESTA_QUIERO_CAMBIAR}
        </button>
      </div>
      <Link to="/mi-idea" className="enlace mt-3 inline-block">
        Editarla o bajarla en Mi idea
      </Link>
    </div>
  )
}
