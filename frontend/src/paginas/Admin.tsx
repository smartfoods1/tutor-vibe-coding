import { useState } from 'react'
import { useConfig } from '../componentes/Configuracion.tsx'
import { Cargando, MensajeError, mensajeDe } from '../componentes/Estados.tsx'
import Pagina from '../componentes/Pagina.tsx'
import VistaDatos from '../componentes/VistaDatos.tsx'
import { api, type LinkPorAprobar } from '../lib/api.ts'
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
