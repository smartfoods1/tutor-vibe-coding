import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Cargando, MensajeError, mensajeDe } from '../componentes/Estados.tsx'
import Pagina from '../componentes/Pagina.tsx'
import { api } from '../lib/api.ts'

/** Baja de los mails del curso desde el link del mail (sin sesión). */
export default function Baja() {
  const [parametros] = useSearchParams()
  const token = parametros.get('t') ?? ''
  const [estado, setEstado] = useState<'mandando' | 'listo' | 'error'>(token ? 'mandando' : 'error')
  const [error, setError] = useState<string | null>(token ? null : 'Al link le falta una parte. Abrilo de nuevo desde el mail.')
  const hecho = useRef(false)

  useEffect(() => {
    if (!token || hecho.current) return
    hecho.current = true
    api
      .baja(token)
      .then(() => setEstado('listo'))
      .catch((e: unknown) => {
        setError(mensajeDe(e))
        setEstado('error')
      })
  }, [token])

  return (
    <Pagina titulo="Baja de los mails" navegacion="publica">
      <h1 className="text-[2rem] font-bold">Baja de los mails</h1>
      {estado === 'mandando' && <Cargando texto="Dándote de baja" />}
      {estado === 'listo' && (
        <div role="status" className="aviso mt-6">
          <p>Listo. No te vamos a mandar más mails del curso.</p>
          <p className="mt-2">
            Los códigos para entrar te siguen llegando cuando los pidas. Si cambiás de idea, podés volver a recibirlos
            desde{' '}
            <Link to="/mis-datos" className="enlace">
              Mis datos
            </Link>
            .
          </p>
        </div>
      )}
      {estado === 'error' && error && (
        <div className="mt-6">
          <MensajeError mensaje={error} />
        </div>
      )}
    </Pagina>
  )
}
