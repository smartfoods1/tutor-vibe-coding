import { Link, useNavigate } from 'react-router-dom'
import { Cargando, MensajeError, mensajeDe } from '../componentes/Estados.tsx'
import Pagina from '../componentes/Pagina.tsx'
import { api, type Yo } from '../lib/api.ts'
import { RESUMEN_MODULOS, TITULOS_MODULOS } from '../lib/marca.ts'
import { useCarga } from '../lib/useCarga.ts'

const NOMBRE_HERRAMIENTA = { codex: 'Codex', claude: 'Claude' } as const

function estadoDe(yo: Yo, modulo: number): 'terminado' | 'actual' | 'pendiente' {
  if (modulo < yo.modulo_actual || yo.avance.some((a) => a.modulo === modulo)) return 'terminado'
  if (modulo === yo.modulo_actual) return 'actual'
  return 'pendiente'
}

export default function Inicio() {
  const navigate = useNavigate()
  const { datos: yo, error, cargando, recargar } = useCarga(() => api.yo())

  async function salir() {
    await api.salir().catch(() => null)
    navigate('/', { replace: true })
  }

  if (cargando) {
    return (
      <Pagina titulo="Tu recorrido" navegacion="privada">
        <Cargando />
      </Pagina>
    )
  }
  if (!yo) {
    return (
      <Pagina titulo="Tu recorrido" navegacion="privada">
        <MensajeError mensaje={mensajeDe(error)} alReintentar={() => void recargar()} />
      </Pagina>
    )
  }

  const actual = yo.modulo_actual
  const enLaWeb = actual <= 3
  const herramienta = yo.taller.herramienta ? NOMBRE_HERRAMIENTA[yo.taller.herramienta] : 'tu herramienta'

  return (
    <Pagina titulo="Tu recorrido" navegacion="privada">
      <h1 className="text-[2rem] font-bold">Tu recorrido</h1>

      <section className="tarjeta mt-6 border-2 border-tinta" aria-labelledby="ahora">
        {enLaWeb ? (
          <>
            <p className="etiqueta text-oxido">Módulo {actual} · estás acá</p>
            <h2 id="ahora" className="mt-2 text-[1.5rem] font-bold">
              {TITULOS_MODULOS[actual]}
            </h2>
            <p className="mt-2">{RESUMEN_MODULOS[actual]}</p>
            {actual === 3 && <p className="mt-2 text-marron">Este módulo conviene hacerlo desde la computadora.</p>}
            <Link to={`/modulo/${actual}`} className="boton mt-5 w-full">
              {actual === 1 && yo.avance.length === 0 ? 'Empezar el módulo 1' : `Seguir con el módulo ${actual}`}
            </Link>
          </>
        ) : (
          <>
            <p className="etiqueta text-oxido">Módulos 4 a 7 · en {herramienta}</p>
            <h2 id="ahora" className="mt-2 text-[1.5rem] font-bold">
              {actual >= 7 ? 'Tu página está publicada' : 'Construí tu página con el kit'}
            </h2>
            <p className="mt-2">
              {actual >= 7
                ? 'Registraste tu link. Si la cambiás, publicala de nuevo en el mismo link.'
                : `Abrí la carpeta de tu kit en ${herramienta} y escribí "sigamos" (o "empecemos" la primera vez). El tutor sabe dónde quedaste.`}
            </p>
            <Link to="/mostrar" className="boton mt-5 w-full">
              {actual >= 7 ? 'Registrar otro link' : 'Ya publiqué: registrar mi link'}
            </Link>
            <p className="mt-4">
              ¿Perdiste la carpeta?{' '}
              <Link to="/modulo/3" className="enlace">
                Volvé a bajar el kit
              </Link>
            </p>
          </>
        )}
      </section>

      <section className="mt-10" aria-labelledby="en-la-web">
        <h2 id="en-la-web" className="text-[1.3rem] font-bold">
          En la web, con el tutor
        </h2>
        <ol className="mt-3 divide-y divide-linea border-y border-linea">
          {[1, 2, 3].map((modulo) => {
            const estado = estadoDe(yo, modulo)
            const contenido = (
              <>
                <span className="etiqueta block">Módulo {modulo}</span>
                <span className="block font-semibold">{TITULOS_MODULOS[modulo]}</span>
              </>
            )
            return (
              <li key={modulo} className="flex items-center justify-between gap-4 py-3">
                {estado === 'pendiente' ? (
                  <div className="text-marron">{contenido}</div>
                ) : (
                  <Link to={`/modulo/${modulo}`} className="no-underline">
                    {contenido}
                  </Link>
                )}
                <span className={estado === 'actual' ? 'font-semibold text-oxido' : 'text-marron'}>
                  {estado === 'terminado' ? 'Terminado' : estado === 'actual' ? 'Estás acá' : 'Todavía no'}
                </span>
              </li>
            )
          })}
        </ol>
      </section>

      <section className="mt-8" aria-labelledby="en-la-compu">
        <h2 id="en-la-compu" className="text-[1.3rem] font-bold">
          En tu computadora, con el kit
        </h2>
        <p className="mt-1 text-marron">El kit es una carpeta con tu idea adentro. La bajás al final del módulo 3.</p>
        <ol className="mt-3 divide-y divide-linea border-y border-linea">
          {[4, 5, 6, 7].map((modulo) => (
            <li key={modulo} className="py-3">
              <span className="etiqueta block">Módulo {modulo}</span>
              <span className="block font-semibold">{TITULOS_MODULOS[modulo]}</span>
            </li>
          ))}
        </ol>
      </section>

      <nav className="mt-10" aria-label="Accesos">
        <ul className="grid gap-3 sm:grid-cols-2">
          <li>
            <Link to="/mi-idea" className="boton boton-sec w-full">
              Mi idea
            </Link>
          </li>
          {!enLaWeb && (
            <li>
              <Link to="/mostrar" className="boton boton-sec w-full">
                Mostrar lo que hiciste
              </Link>
            </li>
          )}
          <li>
            <Link to="/mis-datos" className="boton boton-sec w-full">
              Mis datos
            </Link>
          </li>
          {yo.es_admin && (
            <li>
              <Link to="/admin" className="boton boton-sec w-full">
                Administrar el curso
              </Link>
            </li>
          )}
        </ul>
      </nav>

      <p className="mt-8 text-marron">
        Entraste como <span className="break-all">{yo.email}</span>.{' '}
        <button type="button" className="enlace text-tinta" onClick={() => void salir()}>
          Salir
        </button>
      </p>
    </Pagina>
  )
}
