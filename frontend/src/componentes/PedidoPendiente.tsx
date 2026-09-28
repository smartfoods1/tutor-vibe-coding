import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../lib/api.ts'
import Pagina from './Pagina.tsx'

/**
 * Lo que ve una cuenta que se anotó y espera que quien administra la apruebe (APROBACION_MANUAL).
 * Mientras tanto no usa el tutor: puede ver o borrar sus datos, o salir.
 */
export default function PedidoPendiente({ email }: { email: string | null }) {
  const navigate = useNavigate()
  const [saliendo, setSaliendo] = useState(false)

  async function salir() {
    setSaliendo(true)
    await api.salir().catch(() => null)
    navigate('/', { replace: true })
  }

  return (
    <Pagina titulo="Tu pedido de acceso">
      <p className="etiqueta">Pedido de acceso</p>
      <h1 className="mt-2 text-[2rem] font-bold">Tu pedido está en espera</h1>
      <div role="status" className="aviso mt-6">
        <p className="font-semibold">Recibimos tu pedido. Te avisamos por mail cuando tengas acceso.</p>
        {email && (
          <p className="mt-2">
            El mail te llega a <strong className="break-all">{email}</strong>. Si no lo ves, fijate en spam o en
            promociones.
          </p>
        )}
      </div>
      <p className="mt-6">
        Quien administra el curso aprueba cada inscripción a mano. Hasta que lo haga, tu cuenta no usa el tutor.
      </p>
      <p className="mt-4">
        Si cambiaste de idea, en{' '}
        <Link to="/mis-datos" className="enlace">
          Mis datos
        </Link>{' '}
        podés borrar todo lo que guardamos.
      </p>
      <button type="button" className="boton boton-sec mt-8 w-full" onClick={() => void salir()} disabled={saliendo}>
        {saliendo ? 'Saliendo…' : 'Salir'}
      </button>
    </Pagina>
  )
}
