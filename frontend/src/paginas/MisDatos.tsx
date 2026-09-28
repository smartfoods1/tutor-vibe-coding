import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useConfig } from '../componentes/Configuracion.tsx'
import { Cargando, MensajeError, mensajeDe } from '../componentes/Estados.tsx'
import Pagina from '../componentes/Pagina.tsx'
import { api, cuentaPendiente, type CambiosLink, type LinkPropio } from '../lib/api.ts'
import { textoUsoContenido } from '../lib/marca.ts'
import { useCarga } from '../lib/useCarga.ts'
import { esLinkSeguro } from '../lib/validar.ts'

type CambiosConsentimientos = { mails_curso?: boolean; novedades?: boolean }

const PALABRA = 'BORRAR'

export default function MisDatos() {
  const { newsletter } = useConfig()
  const { datos: yo, error, cargando, recargar, poner } = useCarga(() => api.yo())
  const [falla, setFalla] = useState<string | null>(null)
  const [cambiando, setCambiando] = useState(false)
  const [bajando, setBajando] = useState(false)
  const [confirmacion, setConfirmacion] = useState('')
  const [borrando, setBorrando] = useState(false)
  const [borrado, setBorrado] = useState(false)

  async function cambiar(cambios: CambiosConsentimientos) {
    if (!yo) return
    const anterior = yo
    setFalla(null)
    setCambiando(true)
    poner({ ...yo, consentimientos: { ...yo.consentimientos, ...cambios } })
    try {
      await api.cambiarConsentimientos(cambios)
    } catch (e) {
      poner(anterior)
      setFalla(mensajeDe(e))
    } finally {
      setCambiando(false)
    }
  }

  async function bajar() {
    setFalla(null)
    setBajando(true)
    try {
      await api.descargarMisDatos()
    } catch (e) {
      setFalla(mensajeDe(e))
    } finally {
      setBajando(false)
    }
  }

  async function borrar(evento: FormEvent) {
    evento.preventDefault()
    if (confirmacion !== PALABRA) return
    setFalla(null)
    setBorrando(true)
    try {
      await api.borrarMisDatos()
      setBorrado(true)
    } catch (e) {
      setFalla(mensajeDe(e))
      setBorrando(false)
    }
  }

  if (borrado) {
    return (
      <Pagina titulo="Mis datos">
        <h1 className="text-[2rem] font-bold">Listo</h1>
        <div role="status" className="aviso mt-6">
          <p>Borramos todos tus datos y cerramos tu sesión. No vas a recibir más mails del curso.</p>
        </div>
        <Link to="/" className="boton boton-sec mt-6 w-full">
          Ir al principio
        </Link>
      </Pagina>
    )
  }

  return (
    <Pagina titulo="Mis datos" navegacion="privada">
      <h1 className="text-[2rem] font-bold">Mis datos</h1>
      <p className="mt-4">
        Lo que guardamos es tuyo: lo podés ver, bajar y borrar.{' '}
        <Link to="/privacidad" className="enlace">
          Cómo cuidamos tus datos
        </Link>
      </p>

      {cargando ? (
        <Cargando />
      ) : !yo ? (
        <div className="mt-6">
          <MensajeError mensaje={mensajeDe(error)} alReintentar={() => void recargar()} />
        </div>
      ) : (
        <>
          {falla && (
            <div className="mt-6">
              <MensajeError mensaje={falla} />
            </div>
          )}

          <section aria-labelledby="mails" className="mt-8">
            <h2 id="mails" className="text-[1.3rem] font-bold">
              Mails
            </h2>
            {yo.consentimientos.mails_curso ? (
              <>
                <p className="mt-2">
                  Recibís los mails del curso (como mucho tres, además de los códigos para entrar). Cada uno trae un
                  link para darte de baja.
                </p>
                <button
                  type="button"
                  className="enlace mt-2"
                  onClick={() => void cambiar({ mails_curso: false })}
                  disabled={cambiando}
                >
                  Dejar de recibir los mails del curso
                </button>
              </>
            ) : (
              <>
                <p className="mt-2">No recibís los mails del curso. Los códigos para entrar te llegan igual.</p>
                <button
                  type="button"
                  className="boton boton-sec mt-3 w-full sm:w-auto"
                  onClick={() => void cambiar({ mails_curso: true })}
                  disabled={cambiando}
                >
                  Volver a recibir los mails del curso
                </button>
              </>
            )}
            {newsletter && (
              <CasillaNovedades
                marcada={yo.consentimientos.novedades === true}
                alCambiar={(novedades) => void cambiar({ novedades })}
              />
            )}
          </section>

          {/* Una cuenta pendiente no tiene links (ni puede pedirlos): solo ve, baja o borra sus datos. */}
          {!cuentaPendiente(yo) && <MisLinks />}

          <section aria-labelledby="bajar" className="mt-10">
            <h2 id="bajar" className="text-[1.3rem] font-bold">
              Bajar mis datos
            </h2>
            <p className="mt-2">
              Un archivo con todo lo que guardamos: tu mail, tus permisos, tu avance, tu idea, tus conversaciones con el
              tutor y tus links.
            </p>
            <button
              type="button"
              className="boton boton-sec mt-3 w-full sm:w-auto"
              onClick={() => void bajar()}
              disabled={bajando}
            >
              {bajando ? 'Preparando…' : 'Bajar mis datos'}
            </button>
          </section>

          <section aria-labelledby="borrar" className="mt-10 rounded-lg border-2 border-oxido p-4">
            <h2 id="borrar" className="text-[1.3rem] font-bold text-oxido">
              Borrar todo
            </h2>
            <p className="mt-2">
              Borramos tu cuenta, tu idea, tus conversaciones, tu avance y tus links, y dejamos de mandarte mails. No
              se puede deshacer. Si querés quedarte con tu idea, bajala antes.
            </p>
            <form onSubmit={borrar} className="mt-4 space-y-3">
              <label htmlFor="confirmar-borrado" className="block font-semibold">
                Para confirmar, escribí {PALABRA}
              </label>
              <input
                id="confirmar-borrado"
                className="campo"
                autoCapitalize="characters"
                autoComplete="off"
                spellCheck={false}
                value={confirmacion}
                onChange={(e) => setConfirmacion(e.target.value)}
              />
              <button
                type="submit"
                className="boton boton-sec w-full border-oxido text-oxido"
                disabled={confirmacion !== PALABRA || borrando}
              >
                {borrando ? 'Borrando…' : 'Borrar todos mis datos'}
              </button>
            </form>
          </section>
        </>
      )}
    </Pagina>
  )
}

/** La casilla de novedades, con el texto legal vigente (el mismo de la inscripción, nunca uno inventado). */
function CasillaNovedades({ marcada, alCambiar }: { marcada: boolean; alCambiar: (marcada: boolean) => void }) {
  const legales = useCarga(() => api.textosLegales())
  const texto = legales.datos?.textos?.novedades?.trim()

  if (legales.cargando) return <Cargando />
  if (!texto) {
    return (
      <div className="mt-5">
        <MensajeError
          mensaje="No pudimos cargar el permiso de las novedades. Probá de nuevo en un rato."
          alReintentar={() => void legales.recargar()}
        />
      </div>
    )
  }
  return (
    <label className="mt-5 flex gap-3">
      <input type="checkbox" checked={marcada} onChange={(e) => alCambiar(e.target.checked)} />
      <span>{texto}</span>
    </label>
  )
}

function nombreDe(link: LinkPropio): string {
  if (link.titulo?.trim()) return link.titulo.trim()
  try {
    return new URL(link.url).hostname
  } catch {
    return link.url
  }
}

/** Los links que registró: qué hacemos con cada uno (por PATCH) y borrarlo (por DELETE, con confirmación). */
function MisLinks() {
  const { autorNombre } = useConfig()
  const { datos, error, cargando, recargar, poner } = useCarga(() => api.misLinks())
  const [falla, setFalla] = useState<string | null>(null)
  const [ocupado, setOcupado] = useState<number | null>(null)
  const [aBorrar, setABorrar] = useState<number | null>(null)
  const links = Array.isArray(datos) ? datos : []

  async function cambiar(link: LinkPropio, cambios: CambiosLink) {
    setFalla(null)
    setOcupado(link.id)
    try {
      const nuevo = await api.cambiarLink(link.id, cambios)
      const actualizado = nuevo && typeof nuevo === 'object' ? { ...link, ...cambios, ...nuevo } : { ...link, ...cambios }
      poner(links.map((l) => (l.id === link.id ? actualizado : l)))
    } catch (e) {
      setFalla(mensajeDe(e))
    } finally {
      setOcupado(null)
    }
  }

  async function borrar(link: LinkPropio) {
    setFalla(null)
    setOcupado(link.id)
    try {
      await api.borrarLink(link.id)
      setABorrar(null)
      poner(links.filter((l) => l.id !== link.id))
    } catch (e) {
      setFalla(mensajeDe(e))
    } finally {
      setOcupado(null)
    }
  }

  return (
    <section aria-labelledby="links" className="mt-10">
      <h2 id="links" className="text-[1.3rem] font-bold">
        Tus links
      </h2>
      <p className="mt-2">
        Elegí qué podemos hacer con cada link. La galería muestra un link recién cuando lo aprueba el curso.
      </p>
      {falla && (
        <div className="mt-4">
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
        <p className="mt-3 text-marron">Todavía no registraste ningún link.</p>
      ) : (
        <ul aria-label="Tus links" className="mt-4 divide-y divide-linea border-y border-linea">
          {links.map((link) => (
            <li key={link.id} className="space-y-3 py-4">
              <div>
                <p className="font-semibold break-words">{nombreDe(link)}</p>
                {esLinkSeguro(link.url) ? (
                  <a
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="enlace break-all text-marron"
                  >
                    {link.url}
                  </a>
                ) : (
                  <p className="break-all text-marron">{link.url}</p>
                )}
              </div>
              <label className="flex gap-3">
                <input
                  type="checkbox"
                  checked={link.mostrar_galeria}
                  disabled={ocupado !== null}
                  onChange={(e) => void cambiar(link, { mostrar_galeria: e.target.checked })}
                />
                <span>Se puede mostrar en la galería del curso, a la vista de cualquiera.</span>
              </label>
              {link.mostrar_galeria && (
                <p className="pl-8 text-marron">
                  {link.aprobado ? 'Se ve en la galería.' : 'Espera que el curso lo apruebe para verse en la galería.'}
                </p>
              )}
              <label className="flex gap-3">
                <input
                  type="checkbox"
                  checked={link.uso_contenido}
                  disabled={ocupado !== null}
                  onChange={(e) => void cambiar(link, { uso_contenido: e.target.checked })}
                />
                <span>{textoUsoContenido(autorNombre)}</span>
              </label>
              {aBorrar === link.id ? (
                <div role="group" aria-label="Confirmar el borrado" className="aviso">
                  <p>¿Borrar este link? No se puede deshacer.</p>
                  <div className="mt-3 flex flex-wrap gap-3">
                    <button
                      type="button"
                      className="boton boton-sec boton-chico border-oxido text-oxido"
                      disabled={ocupado === link.id}
                      onClick={() => void borrar(link)}
                    >
                      {ocupado === link.id ? 'Borrando…' : 'Sí, borrarlo'}
                    </button>
                    <button
                      type="button"
                      className="boton boton-sec boton-chico"
                      disabled={ocupado === link.id}
                      onClick={() => setABorrar(null)}
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              ) : (
                <button type="button" className="enlace text-oxido" onClick={() => setABorrar(link.id)}>
                  Borrar este link
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
