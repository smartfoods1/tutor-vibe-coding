import { useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useConfig } from '../componentes/Configuracion.tsx'
import { MensajeError, mensajeDe } from '../componentes/Estados.tsx'
import Pagina from '../componentes/Pagina.tsx'
import Turnstile from '../componentes/Turnstile.tsx'
import { ErrorApi, api, type Consentimientos } from '../lib/api.ts'
import { MENSAJE_MAIL, emailValido, normalizarEmail } from '../lib/validar.ts'

/** Lo que llega en el state de la navegación: de la portada (al anotarse) o de una página privada. */
export interface EstadoEntrar {
  email?: string
  enviado?: boolean
  /** Los permisos que marcó en la portada: se reenvían si pide otro código. */
  consentimientos?: Consentimientos
  fuente?: string | null
  desde?: string
}

export default function Entrar() {
  const { turnstileSiteKey } = useConfig()
  const navigate = useNavigate()
  const estado = (useLocation().state ?? {}) as EstadoEntrar

  const [paso, setPaso] = useState<'mail' | 'codigo'>(estado.enviado && estado.email ? 'codigo' : 'mail')
  const [email, setEmail] = useState(estado.email ?? '')
  const [codigo, setCodigo] = useState('')
  const [token, setToken] = useState<string | null>(null)
  const [reinicio, setReinicio] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [sinInscripcion, setSinInscripcion] = useState(false)
  const [ocupado, setOcupado] = useState(false)

  async function pedirCodigo(evento: FormEvent) {
    evento.preventDefault()
    const limpio = normalizarEmail(email)
    if (!emailValido(limpio)) return setError(MENSAJE_MAIL)
    if (turnstileSiteKey && !token) {
      return setError('Esperá un segundo a que termine la verificación de seguridad y probá de nuevo.')
    }
    setError(null)
    setSinInscripcion(false)
    setOcupado(true)
    try {
      await api.pedirCodigo({
        email: limpio,
        consentimientos: estado.consentimientos,
        fuente: estado.fuente,
        turnstile: token,
      })
      setEmail(limpio)
      setCodigo('')
      setPaso('codigo')
    } catch (e) {
      setError(mensajeDe(e))
      // Sin los permisos de la portada, un 422 es porque el mail todavía no se anotó.
      setSinInscripcion(e instanceof ErrorApi && e.status === 422 && !estado.consentimientos)
      if (turnstileSiteKey) setReinicio((n) => n + 1)
    } finally {
      setOcupado(false)
    }
  }

  async function verificar(evento: FormEvent) {
    evento.preventDefault()
    const numeros = codigo.replace(/\D/g, '')
    if (numeros.length !== 6) return setError('El código tiene 6 números. Copialo tal cual del mail.')
    setError(null)
    setOcupado(true)
    try {
      const { nuevo } = await api.verificar(email, numeros)
      const destino = nuevo ? '/modulo/1' : estado.desde && estado.desde !== '/entrar' ? estado.desde : '/inicio'
      navigate(destino, { replace: true })
    } catch (e) {
      setError(mensajeDe(e))
      setOcupado(false)
    }
  }

  if (paso === 'codigo') {
    return (
      <Pagina titulo="Revisá tu mail">
        <p className="etiqueta">Paso 2 de 2</p>
        <h1 className="mt-2 text-[2rem] font-bold">Revisá tu mail</h1>
        <p className="mt-4">
          Te mandamos un código de 6 números a <strong className="break-all">{email}</strong>. Vence en 10 minutos.
        </p>
        <form onSubmit={verificar} noValidate className="mt-6 space-y-5">
          <div>
            <label htmlFor="codigo" className="block font-semibold">
              Código de 6 números
            </label>
            <input
              id="codigo"
              inputMode="numeric"
              autoComplete="one-time-code"
              pattern="[0-9 ]*"
              maxLength={12}
              className="campo mt-2 font-mono text-[1.4rem] tracking-[0.3em]"
              value={codigo}
              onChange={(e) => setCodigo(e.target.value)}
              autoFocus
            />
          </div>
          {error && <MensajeError mensaje={error} />}
          <button type="submit" className="boton w-full" disabled={ocupado}>
            {ocupado ? 'Entrando…' : 'Entrar'}
          </button>
        </form>
        <div className="aviso mt-8">
          <p>¿No llegó? Fijate en la carpeta de spam o de promociones. Puede tardar un par de minutos.</p>
          <button
            type="button"
            className="enlace mt-2 text-left"
            onClick={() => {
              setError(null)
              setPaso('mail')
            }}
          >
            Pedir otro código o cambiar el mail
          </button>
        </div>
      </Pagina>
    )
  }

  return (
    <Pagina titulo="Entrar">
      <h1 className="text-[2rem] font-bold">Entrar</h1>
      <p className="mt-4">
        Escribí el mail con el que te anotaste. Te mandamos un código para entrar, sin contraseña.
      </p>
      <form onSubmit={pedirCodigo} noValidate className="mt-6 space-y-5">
        <div>
          <label htmlFor="email-entrar" className="block font-semibold">
            Tu mail
          </label>
          <input
            id="email-entrar"
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
        </div>
        {turnstileSiteKey && <Turnstile siteKey={turnstileSiteKey} alToken={setToken} reinicio={reinicio} />}
        {error && (
          <MensajeError mensaje={error}>
            {sinInscripcion && (
              <p className="mt-2 text-tinta">
                Si es tu primera vez,{' '}
                <Link to="/" className="enlace">
                  anotate acá
                </Link>
                .
              </p>
            )}
          </MensajeError>
        )}
        <button type="submit" className="boton w-full" disabled={ocupado}>
          {ocupado ? 'Mandando…' : 'Mandame el código'}
        </button>
      </form>
      <p className="mt-8">
        ¿Todavía no te anotaste?{' '}
        <Link to="/" className="enlace">
          Anotate acá
        </Link>
      </p>
    </Pagina>
  )
}
