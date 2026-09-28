import { Navigate, useLocation } from 'react-router-dom'
import { Cargando } from '../componentes/Estados.tsx'
import Pagina from '../componentes/Pagina.tsx'
import PedidoPendiente from '../componentes/PedidoPendiente.tsx'
import { api, cuentaPendiente } from '../lib/api.ts'
import { useCarga } from '../lib/useCarga.ts'

/** Lo que llega en el state de la navegación (desde Entrar, con el mail que se acaba de verificar). */
export interface EstadoPendiente {
  email?: string
}

/**
 * /pendiente: adonde lleva Entrar cuando la cuenta queda pendiente, y adonde lleva cualquier pedido
 * que responde el 403 de pendiente. Si la cuenta ya está aprobada, sigue al curso.
 */
export default function Pendiente() {
  const estado = (useLocation().state ?? {}) as EstadoPendiente
  const yo = useCarga(() => api.yo())

  if (yo.datos && !cuentaPendiente(yo.datos)) return <Navigate to="/inicio" replace />

  const email = yo.datos?.email ?? estado.email ?? null
  if (yo.cargando && !email) {
    return (
      <Pagina titulo="Tu pedido de acceso">
        <Cargando />
      </Pagina>
    )
  }
  return <PedidoPendiente email={email} />
}
