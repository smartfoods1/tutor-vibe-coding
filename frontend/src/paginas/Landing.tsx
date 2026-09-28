import { useEffect, useMemo, useState, type FormEvent, type ReactNode } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useConfig } from '../componentes/Configuracion.tsx'
import { Cargando, MensajeError, mensajeDe } from '../componentes/Estados.tsx'
import { Pie } from '../componentes/Pagina.tsx'
import TextoMd from '../componentes/TextoMd.tsx'
import Turnstile from '../componentes/Turnstile.tsx'
import { api, type Consentimientos } from '../lib/api.ts'
import { fuenteDeLaVisita } from '../lib/fuente.ts'
import type { EstadoEntrar } from './Entrar.tsx'
import { NOMBRE_CURSO } from '../lib/marca.ts'
import { useCarga } from '../lib/useCarga.ts'
import {
  MENSAJE_MAIL,
  MENSAJE_MAILS_CURSO,
  MENSAJE_TRANSFERENCIA,
  emailValido,
  normalizarEmail,
} from '../lib/validar.ts'

interface Casilla {
  tipo: keyof Consentimientos
  obligatoria: boolean
}

const OBLIGATORIAS: Casilla[] = [
  { tipo: 'mails_curso', obligatoria: true },
  { tipo: 'transferencia', obligatoria: true },
]

/** La de novedades es opcional y aparece solo si la instalación tiene newsletter (NEWSLETTER_NOMBRE). */
const NOVEDADES: Casilla = { tipo: 'novedades', obligatoria: false }

export default function Landing() {
  const { turnstileSiteKey, newsletter, cargada } = useConfig()
  const casillas = newsletter ? [...OBLIGATORIAS, NOVEDADES] : OBLIGATORIAS
  const navigate = useNavigate()
  const { search } = useLocation()
  const fuente = useMemo(() => fuenteDeLaVisita(search), [search])
  const legales = useCarga(() => api.textosLegales())
  const sesion = useCarga(() => api.yo({ publico: true }))

  const [email, setEmail] = useState('')
  const [marcadas, setMarcadas] = useState<Consentimientos>({
    mails_curso: false,
    transferencia: false,
    novedades: false,
  })
  const [token, setToken] = useState<string | null>(null)
  const [reinicio, setReinicio] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  useEffect(() => {
    document.title = `${NOMBRE_CURSO}: de lo que imaginás a algo que existe`
  }, [])

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    const limpio = normalizarEmail(email)
    if (!emailValido(limpio)) return setError(MENSAJE_MAIL)
    if (!marcadas.mails_curso) return setError(MENSAJE_MAILS_CURSO)
    if (!marcadas.transferencia) return setError(MENSAJE_TRANSFERENCIA)
    if (turnstileSiteKey && !token) {
      return setError('Esperá un segundo a que termine la verificación de seguridad y probá de nuevo.')
    }
    setError(null)
    setEnviando(true)
    // Sin newsletter no hay casilla de novedades: el permiso va siempre en false.
    const consentimientos: Consentimientos = { ...marcadas, novedades: newsletter ? marcadas.novedades : false }
    try {
      await api.pedirCodigo({ email: limpio, consentimientos, fuente, turnstile: token })
      // Entrar los reenvía si la persona pide otro código (el alta se hace con el código nuevo).
      const estado: EstadoEntrar = { email: limpio, enviado: true, consentimientos, fuente }
      navigate('/entrar', { state: estado })
    } catch (e) {
      setError(mensajeDe(e))
      if (turnstileSiteKey) setReinicio((n) => n + 1)
      setEnviando(false)
    }
  }

  const textos = legales.datos?.textos ?? {}
  // Cada casilla muestra el texto legal vigente, nunca uno inventado: si falta alguno, no se inscribe.
  const faltanTextos = legales.datos !== null && casillas.some(({ tipo }) => !textos[tipo]?.trim())

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="bg-oro text-tinta">
        <div className="mx-auto max-w-2xl px-4 pt-6 pb-10">
          <div className="flex items-center justify-between gap-4">
            <p className="font-semibold">{NOMBRE_CURSO}</p>
            <Link to="/entrar" className="enlace">
              Entrar
            </Link>
          </div>
          <div className="regla mt-4" aria-hidden="true" />
          <p className="etiqueta mt-8">Curso gratis · para gente que nunca programó</p>
          <h1 className="mt-3 text-[2.4rem] leading-[1.1] font-bold sm:text-[3rem]">
            De lo que imaginás a algo que <em className="text-oxido">existe</em>
          </h1>
          <p className="mt-5 text-[1.15rem]">
            Terminás con tu idea publicada como una página, con un link para compartir. No hace falta saber
            programar: vos decís qué querés, la máquina lo escribe y vos mirás el resultado.
          </p>
        </div>
      </header>

      <main className="mx-auto w-full max-w-2xl flex-1 px-4 pt-8 pb-12">
        <section aria-labelledby="como-es">
          <h2 id="como-es" className="text-[1.5rem] font-bold">
            Cómo es
          </h2>
          <ol className="mt-4 space-y-4">
            <Paso etiqueta="Módulos 1 y 2" titulo="Desde el celular">
              Conversás con un tutor, por texto o por voz, sobre cómo se piensa esto y sobre tu idea. Termina en
              una página que cuenta tu idea.
            </Paso>
            <Paso etiqueta="Módulo 3" titulo="En la computadora, Mac o Windows">
              Instalás tu herramienta con el tutor al lado. Antes de instalar nada vas a ver cuánto cuesta cada
              camino, con la fecha en que lo verificamos.
            </Paso>
            <Paso etiqueta="Módulos 4 a 7" titulo="En tu herramienta">
              Construís tu página, aprendés a volver atrás si algo se rompe y la publicás.
            </Paso>
          </ol>
          <p className="mt-5 text-marron">Calculamos unas 5 horas, repartidas en varios días. Lo estamos midiendo.</p>
        </section>

        <section aria-labelledby="anotate" className="tarjeta mt-10">
          <h2 id="anotate" className="text-[1.5rem] font-bold">
            Anotate
          </h2>

          {sesion.datos && (
            <div className="aviso aviso-logro mt-4">
              <p>Ya estás adentro.</p>
              <Link to="/inicio" className="enlace">
                Seguir con el curso
              </Link>
            </div>
          )}

          {/* Se espera la config: de ella depende si va la casilla de novedades. */}
          {legales.cargando || !cargada ? (
            <Cargando />
          ) : (legales.error && !legales.datos) || faltanTextos ? (
            <div className="mt-4">
              <MensajeError
                mensaje={
                  faltanTextos
                    ? 'No pudimos cargar los textos de la inscripción. Probá de nuevo en un rato.'
                    : 'No pudimos cargar los textos de la inscripción. Revisá la conexión.'
                }
                alReintentar={() => void legales.recargar()}
              />
            </div>
          ) : (
            <form onSubmit={enviar} noValidate className="mt-5 space-y-5">
              <div>
                <label htmlFor="email" className="block font-semibold">
                  Tu mail
                </label>
                <input
                  id="email"
                  type="email"
                  inputMode="email"
                  autoComplete="email"
                  autoCapitalize="none"
                  spellCheck={false}
                  maxLength={320}
                  className="campo mt-2"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <p className="mt-2 text-marron">Te mandamos un código de 6 números. No hace falta contraseña.</p>
              </div>

              <fieldset className="space-y-4">
                <legend className="font-semibold">Tus permisos</legend>
                <p className="text-marron">
                  {newsletter
                    ? 'Las dos primeras casillas son obligatorias para hacer el curso.'
                    : 'Las dos casillas son obligatorias para hacer el curso.'}
                </p>
                {casillas.map(({ tipo, obligatoria }) => (
                  <label key={tipo} className="flex gap-3">
                    <input
                      type="checkbox"
                      checked={marcadas[tipo]}
                      onChange={(e) => setMarcadas((previas) => ({ ...previas, [tipo]: e.target.checked }))}
                    />
                    <span>
                      {textos[tipo]}{' '}
                      <span className="text-marron">{obligatoria ? '(obligatoria)' : '(opcional)'}</span>
                    </span>
                  </label>
                ))}
              </fieldset>

              {legales.datos?.texto_md && (
                <details className="rounded-lg border border-linea px-4 py-3">
                  <summary className="cursor-pointer font-semibold">Por qué te pedimos estos permisos</summary>
                  <div className="mt-3">
                    <TextoMd texto={legales.datos.texto_md} bajarTitulos />
                  </div>
                </details>
              )}

              {turnstileSiteKey && <Turnstile siteKey={turnstileSiteKey} alToken={setToken} reinicio={reinicio} />}

              {error && <MensajeError mensaje={error} />}

              <button type="submit" className="boton w-full" disabled={enviando}>
                {enviando ? 'Mandando el código…' : 'Quiero empezar'}
              </button>

              <p>
                <Link to="/privacidad" className="enlace">
                  Cómo cuidamos tus datos
                </Link>
              </p>
            </form>
          )}
        </section>

        <p className="mt-8">
          ¿Ya te anotaste?{' '}
          <Link to="/entrar" className="enlace">
            Entrá con tu mail
          </Link>
        </p>
        <p className="mt-2">
          <Link to="/galeria" className="enlace">
            Mirá páginas que hicieron otras personas del curso
          </Link>
        </p>
      </main>
      <Pie />
    </div>
  )
}

function Paso({ etiqueta, titulo, children }: { etiqueta: string; titulo: string; children: ReactNode }) {
  return (
    <li className="border-l-2 border-oro-hondo pl-4">
      <p className="etiqueta">{etiqueta}</p>
      <p className="mt-1 font-semibold">{titulo}</p>
      <p className="mt-1">{children}</p>
    </li>
  )
}
