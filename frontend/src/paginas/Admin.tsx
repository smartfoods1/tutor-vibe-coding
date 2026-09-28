import { useState } from 'react'
import { useConfig } from '../componentes/Configuracion.tsx'
import { Cargando, MensajeError, mensajeDe } from '../componentes/Estados.tsx'
import Pagina from '../componentes/Pagina.tsx'
import VistaDatos from '../componentes/VistaDatos.tsx'
import { ErrorApi, api, type LinkPorAprobar, type PedidoAcceso } from '../lib/api.ts'
import { useCarga } from '../lib/useCarga.ts'
import { esLinkSeguro } from '../lib/validar.ts'

export default function Admin() {
  const yo = useCarga(() => api.yo())

  return (
    <Pagina titulo="Administrar" navegacion="privada">
      <h1 className="text-[2rem] font-bold">Administrar el curso</h1>
      {yo.cargando ? (
        <Cargando />
      ) : !yo.datos ? (
        <div className="mt-6">
          <MensajeError mensaje={mensajeDe(yo.error)} alReintentar={() => void yo.recargar()} />
        </div>
      ) : !yo.datos.es_admin ? (
        <p className="aviso mt-6">Esta sección es solo para quien administra el curso.</p>
      ) : (
        <>
          <PedidosDeAcceso />
          <GaleriaPorAprobar />
          <ListaNovedades />
          <Reporte />
        </>
      )}
    </Pagina>
  )
}

/** El CSV de quienes aceptaron las novedades. Solo si la instalación tiene newsletter (NEWSLETTER_NOMBRE). */
function ListaNovedades() {
  const { newsletter } = useConfig()
  const [bajando, setBajando] = useState(false)
  const [falla, setFalla] = useState<string | null>(null)

  if (!newsletter) return null

  async function bajarCsv() {
    setFalla(null)
    setBajando(true)
    try {
      await api.descargarNovedades()
    } catch (e) {
      setFalla(mensajeDe(e))
    } finally {
      setBajando(false)
    }
  }

  return (
    <section aria-labelledby="novedades" className="tarjeta mt-6">
      <h2 id="novedades" className="text-[1.3rem] font-bold">
        Lista de novedades ({newsletter})
      </h2>
      <p className="mt-2">
        Solo quienes aceptaron recibir las novedades. Es un CSV con una columna, email, para importar a mano en{' '}
        {newsletter}.
      </p>
      {falla && (
        <div className="mt-3">
          <MensajeError mensaje={falla} />
        </div>
      )}
      <button type="button" className="boton mt-4 w-full sm:w-auto" onClick={() => void bajarCsv()} disabled={bajando}>
        {bajando ? 'Preparando…' : `Bajar la lista de novedades (${newsletter})`}
      </button>
    </section>
  )
}

function Reporte() {
  const { datos, error, cargando, recargar } = useCarga(() => api.reporte())

  return (
    <section aria-labelledby="reporte" className="mt-8">
      <div className="flex items-center justify-between gap-4">
        <h2 id="reporte" className="text-[1.3rem] font-bold">
          Reporte
        </h2>
        <button type="button" className="boton boton-sec boton-chico" onClick={() => void recargar()}>
          Actualizar
        </button>
      </div>
      {cargando ? (
        <Cargando />
      ) : !datos ? (
        <div className="mt-4">
          <MensajeError mensaje={mensajeDe(error)} alReintentar={() => void recargar()} />
        </div>
      ) : (
        <div className="tarjeta mt-4">
          <VistaDatos datos={datos} />
        </div>
      )}
    </section>
  )
}

function fecha(iso: string): string {
  const momento = new Date(iso)
  if (Number.isNaN(momento.getTime())) return ''
  return momento.toLocaleDateString('es-AR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    timeZone: 'America/Argentina/Buenos_Aires',
  })
}

function fechaYHora(iso: string): string {
  const momento = new Date(iso)
  if (Number.isNaN(momento.getTime())) return ''
  return momento.toLocaleString('es-AR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'America/Argentina/Buenos_Aires',
  })
}

function cantidadDePedidos(n: number): string {
  if (n === 0) return 'No hay pedidos pendientes.'
  return n === 1 ? '1 pedido pendiente.' : `${n} pedidos pendientes.`
}

/**
 * Las cuentas que esperan aprobación (APROBACION_MANUAL). Aprobar le manda la bienvenida; rechazar
 * borra la cuenta con sus datos. Sin aprobación manual la sección aparece solo si quedaron pedidos.
 */
function PedidosDeAcceso() {
  const { aprobacionManual } = useConfig()
  const { datos, error, cargando, recargar, poner } = useCarga(() => api.pedidosDeAcceso())
  const [ocupado, setOcupado] = useState<number | null>(null)
  const [aRechazar, setARechazar] = useState<number | null>(null)
  const [falla, setFalla] = useState<string | null>(null)
  const pedidos = Array.isArray(datos) ? datos : []

  if (!aprobacionManual && pedidos.length === 0) return null

  async function resolver(pedido: PedidoAcceso, accion: 'aprobar' | 'rechazar') {
    setFalla(null)
    setOcupado(pedido.id)
    try {
      if (accion === 'aprobar') await api.aprobarPedido(pedido.id)
      else await api.rechazarPedido(pedido.id)
      setARechazar(null)
      poner(pedidos.filter((p) => p.id !== pedido.id))
      void recargar()
    } catch (e) {
      setFalla(mensajeDe(e))
      // 404 o 409: ya lo resolvió otra pestaña (o se borró); la lista que se ve quedó vieja.
      if (e instanceof ErrorApi && (e.status === 404 || e.status === 409)) {
        setARechazar(null)
        void recargar()
      }
    } finally {
      setOcupado(null)
    }
  }

  return (
    <section aria-labelledby="pedidos-admin" className="tarjeta mt-6">
      <div className="flex items-center justify-between gap-4">
        <h2 id="pedidos-admin" className="text-[1.3rem] font-bold">
          Pedidos de acceso
        </h2>
        <button type="button" className="boton boton-sec boton-chico" onClick={() => void recargar()}>
          Actualizar
        </button>
      </div>
      <p className="mt-2">
        Cada inscripción nueva espera acá. Al aprobarla le llega el mail de bienvenida; al rechazarla se borran sus
        datos.
      </p>
      {falla && (
        <div className="mt-3">
          <MensajeError mensaje={falla} />
        </div>
      )}
      {cargando ? (
        <Cargando />
      ) : error && !datos ? (
        <div className="mt-4">
          <MensajeError mensaje={mensajeDe(error)} alReintentar={() => void recargar()} />
        </div>
      ) : (
        <>
          <p className="mt-3 font-semibold">{cantidadDePedidos(pedidos.length)}</p>
          {pedidos.length > 0 && (
            <ul aria-label="Pedidos de acceso" className="mt-3 divide-y divide-linea border-y border-linea">
              {pedidos.map((pedido) => (
                <li key={pedido.id} className="space-y-3 py-3">
                  <div>
                    <p className="font-semibold break-all">{pedido.email}</p>
                    <p className="text-marron">
                      {[fechaYHora(pedido.creado), pedido.fuente ? `Fuente: ${pedido.fuente}` : 'Sin fuente']
                        .filter(Boolean)
                        .join(' · ')}
                    </p>
                  </div>
                  {aRechazar === pedido.id ? (
                    <div role="group" aria-label="Confirmar el rechazo" className="aviso">
                      <p>Se borran sus datos. ¿Seguro?</p>
                      <div className="mt-3 flex flex-wrap gap-3">
                        <button
                          type="button"
                          className="boton boton-sec boton-chico border-oxido text-oxido"
                          disabled={ocupado !== null}
                          onClick={() => void resolver(pedido, 'rechazar')}
                        >
                          {ocupado === pedido.id ? 'Rechazando…' : 'Sí, rechazar'}
                        </button>
                        <button
                          type="button"
                          className="boton boton-sec boton-chico"
                          disabled={ocupado === pedido.id}
                          onClick={() => setARechazar(null)}
                        >
                          Cancelar
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-wrap gap-3">
                      <button
                        type="button"
                        className="boton boton-chico"
                        aria-label={`Aprobar a ${pedido.email}`}
                        disabled={ocupado !== null}
                        onClick={() => void resolver(pedido, 'aprobar')}
                      >
                        {ocupado === pedido.id ? 'Aprobando…' : 'Aprobar'}
                      </button>
                      <button
                        type="button"
                        className="boton boton-sec boton-chico"
                        aria-label={`Rechazar a ${pedido.email}`}
                        disabled={ocupado !== null}
                        onClick={() => setARechazar(pedido.id)}
                      >
                        Rechazar
                      </button>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </section>
  )
}

/** Los links que pidieron estar en la galería: se ven recién cuando se aprueban. */
function GaleriaPorAprobar() {
  const { datos, error, cargando, recargar, poner } = useCarga(() => api.linksPorAprobar())
  const [ocupado, setOcupado] = useState<number | null>(null)
  const [falla, setFalla] = useState<string | null>(null)
  const links = Array.isArray(datos) ? datos : []
  const pendientes = links.filter((l) => !l.aprobado).length

  async function cambiar(link: LinkPorAprobar, aprobado: boolean) {
    setFalla(null)
    setOcupado(link.id)
    try {
      await api.aprobarLink(link.id, aprobado)
      poner(links.map((l) => (l.id === link.id ? { ...l, aprobado } : l)))
    } catch (e) {
      setFalla(mensajeDe(e))
    } finally {
      setOcupado(null)
    }
  }

  return (
    <section aria-labelledby="galeria-admin" className="tarjeta mt-6">
      <div className="flex items-center justify-between gap-4">
        <h2 id="galeria-admin" className="text-[1.3rem] font-bold">
          Galería por aprobar
        </h2>
        <button type="button" className="boton boton-sec boton-chico" onClick={() => void recargar()}>
          Actualizar
        </button>
      </div>
      <p className="mt-2">
        Links que sus autores quieren mostrar. La galería pública muestra solo los aprobados. Abrí cada uno antes de
        aprobarlo.
      </p>
      {falla && (
        <div className="mt-3">
          <MensajeError mensaje={falla} />
        </div>
      )}
      {cargando ? (
        <Cargando />
      ) : error && !datos ? (
        <div className="mt-4">
          <MensajeError mensaje={mensajeDe(error)} alReintentar={() => void recargar()} />
        </div>
      ) : links.length === 0 ? (
        <p className="mt-3 text-marron">No hay links para revisar.</p>
      ) : (
        <>
          <p className="mt-3 font-semibold">
            {pendientes === 0 ? 'No hay links pendientes.' : pendientes === 1 ? '1 pendiente.' : `${pendientes} pendientes.`}
          </p>
          <ul aria-label="Galería por aprobar" className="mt-3 divide-y divide-linea border-y border-linea">
            {links.map((link) => (
              <li key={link.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                <div className="min-w-0 flex-1">
                  {esLinkSeguro(link.url) ? (
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer nofollow ugc"
                      className="enlace font-semibold break-words"
                    >
                      {link.titulo?.trim() || link.url}
                    </a>
                  ) : (
                    <p className="font-semibold break-words">{link.titulo?.trim() || link.url}</p>
                  )}
                  <p className="break-all text-marron">{link.url}</p>
                  <p className="text-marron">
                    {link.aprobado ? 'Aprobado' : 'Pendiente'}
                    {fecha(link.creado) && ` · ${fecha(link.creado)}`}
                  </p>
                </div>
                {link.aprobado ? (
                  <button
                    type="button"
                    className="boton boton-sec boton-chico"
                    disabled={ocupado === link.id}
                    onClick={() => void cambiar(link, false)}
                  >
                    Sacar
                  </button>
                ) : (
                  <button
                    type="button"
                    className="boton boton-chico"
                    disabled={ocupado === link.id || !esLinkSeguro(link.url)}
                    onClick={() => void cambiar(link, true)}
                  >
                    Aprobar
                  </button>
                )}
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  )
}
