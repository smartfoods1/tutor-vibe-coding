import { Link } from 'react-router-dom'
import { Cargando, MensajeError, mensajeDe } from '../componentes/Estados.tsx'
import Pagina from '../componentes/Pagina.tsx'
import TextoMd from '../componentes/TextoMd.tsx'
import { ErrorApi, api, type PasosKit } from '../lib/api.ts'
import { useCarga } from '../lib/useCarga.ts'

const NOMBRE_HERRAMIENTA = { codex: 'Codex', claude: 'Claude' } as const
const NOMBRE_SISTEMA = { mac: 'Mac', windows: 'Windows', otro: 'tu computadora' } as const

function Encabezado({ pasos }: { pasos?: PasosKit }) {
  return (
    <>
      <p className="etiqueta">Módulos 4 a 7 · en tu computadora</p>
      <h1 className="mt-1 text-[2rem] font-bold">Cómo seguir en tu computadora</h1>
      {pasos && (
        <p className="mt-2 text-marron">
          Para {NOMBRE_HERRAMIENTA[pasos.herramienta]} en {NOMBRE_SISTEMA[pasos.sistema]}.
        </p>
      )}
    </>
  )
}

/**
 * Los pasos para abrir el kit en la herramienta elegida y empezar la lección 4. Es el mismo texto que
 * el LEEME.txt que viaja dentro del kit (sale del mismo archivo): acá se lee sin tener que buscarlo.
 */
export default function Seguir() {
  const { datos: pasos, error, cargando, recargar } = useCarga(() => api.pasosDelKit())

  if (cargando) {
    return (
      <Pagina titulo="Cómo seguir en tu computadora" navegacion="privada">
        <Encabezado />
        <Cargando />
      </Pagina>
    )
  }

  if (!pasos) {
    // 409: todavía falta elegir la herramienta o una computadora Mac o Windows.
    const faltaElegir = error instanceof ErrorApi && error.status === 409
    return (
      <Pagina titulo="Cómo seguir en tu computadora" navegacion="privada">
        <Encabezado />
        <div className="mt-6">
          {faltaElegir ? (
            <div className="aviso">
              <p>{mensajeDe(error)}</p>
              <Link to="/modulo/3" className="boton mt-4 w-full">
                Elegir mi herramienta y mi computadora
              </Link>
            </div>
          ) : (
            <MensajeError mensaje={mensajeDe(error)} alReintentar={() => void recargar()} />
          )}
        </div>
      </Pagina>
    )
  }

  return (
    <Pagina titulo="Cómo seguir en tu computadora" navegacion="privada">
      <Encabezado pasos={pasos} />
      <article className="tarjeta mt-6">
        <TextoMd texto={pasos.texto_md} />
      </article>
      {/* El LEEME manda "volver a la web para cerrar el módulo 3": el camino tiene que estar a la vista. */}
      <p className="mt-6">
        Si todavía te falta cerrar el módulo 3, o querés bajar el kit de nuevo o cambiar tu elección, está todo en el
        módulo 3.
      </p>
      <div className="mt-4 flex flex-col gap-3 sm:flex-row">
        <Link to="/modulo/3" className="boton sm:flex-1">
          Volver al módulo 3
        </Link>
        <Link to="/inicio" className="boton boton-sec sm:flex-1">
          Volver al inicio
        </Link>
      </div>
    </Pagina>
  )
}
