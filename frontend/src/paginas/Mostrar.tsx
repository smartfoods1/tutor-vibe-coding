import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useConfig } from '../componentes/Configuracion.tsx'
import { Cargando, MensajeError, mensajeDe } from '../componentes/Estados.tsx'
import Pagina from '../componentes/Pagina.tsx'
import { api } from '../lib/api.ts'
import { textoUsoContenido } from '../lib/marca.ts'
import { useCarga } from '../lib/useCarga.ts'
import { normalizarLink } from '../lib/validar.ts'

/** El link se registra recién con el kit bajado (módulo 4 en adelante): antes no hay página que mostrar. */
const MODULO_MINIMO = 4

export default function Mostrar() {
  const { autorNombre } = useConfig()
  // Si la sesión venció, lleva a entrar antes de que la persona escriba nada.
  const yo = useCarga(() => api.yo())
  const [link, setLink] = useState('')
  const [titulo, setTitulo] = useState('')
  const [galeria, setGaleria] = useState(false)
  const [contenido, setContenido] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)
  const [listo, setListo] = useState<{ mail: boolean } | null>(null)

  async function registrar(evento: FormEvent) {
    evento.preventDefault()
    const resultado = normalizarLink(link)
    if ('error' in resultado) {
      setError(resultado.error)
      return
    }
    setError(null)
    setEnviando(true)
    try {
      const respuesta = await api.registrarLink({
        url: resultado.url,
        titulo: titulo.trim() || null,
        mostrar_galeria: galeria,
        uso_contenido: contenido,
      })
      setListo({ mail: respuesta?.mail === true })
    } catch (e) {
      setError(mensajeDe(e))
    } finally {
      setEnviando(false)
    }
  }

  if (listo) {
    return (
      <Pagina titulo="Mostrar lo que hiciste" navegacion="privada">
        <h1 className="text-[2rem] font-bold">Listo</h1>
        <div role="status" className="aviso aviso-logro mt-6">
          <p className="font-semibold">Tu link quedó registrado.</p>
          {listo.mail && (
            <p className="mt-2">
              Te mandamos un mail con tu link, para que lo tengas a mano y se lo puedas mandar a alguien.
            </p>
          )}
          {galeria && <p className="mt-2">Aparece en la galería cuando lo aprobemos.</p>}
        </div>
        <p className="mt-4">
          Podés cambiar qué hacemos con tu link, o borrarlo, en{' '}
          <Link to="/mis-datos" className="enlace">
            Mis datos
          </Link>
          .
        </p>
        <Link to="/inicio" className="boton mt-6 w-full">
          Volver al inicio
        </Link>
        <p className="mt-4">
          <Link to="/galeria" className="enlace">
            Ver la galería
          </Link>
        </p>
      </Pagina>
    )
  }

  if (yo.cargando || !yo.datos) {
    return (
      <Pagina titulo="Mostrar lo que hiciste" navegacion="privada">
        <h1 className="text-[2rem] font-bold">Mostrar lo que hiciste</h1>
        {yo.cargando ? (
          <Cargando />
        ) : (
          <div className="mt-6">
            <MensajeError mensaje={mensajeDe(yo.error)} alReintentar={() => void yo.recargar()} />
          </div>
        )}
      </Pagina>
    )
  }

  if (yo.datos.modulo_actual < MODULO_MINIMO) {
    const actual = yo.datos.modulo_actual
    return (
      <Pagina titulo="Mostrar lo que hiciste" navegacion="privada">
        <h1 className="text-[2rem] font-bold">Mostrar lo que hiciste</h1>
        <div className="aviso mt-6">
          <p>
            Primero tenés que bajar tu kit, al final del módulo 3. Con el kit construís y publicás tu página; cuando
            tengas el link, lo registrás acá.
          </p>
          <Link to={`/modulo/${actual}`} className="boton mt-4 w-full">
            Ir al módulo {actual}
          </Link>
        </div>
      </Pagina>
    )
  }

  return (
    <Pagina titulo="Mostrar lo que hiciste" navegacion="privada">
      <h1 className="text-[2rem] font-bold">Mostrar lo que hiciste</h1>
      <p className="mt-4">
        Cuando tengas tu página publicada, registrá el link acá. Nos sirve para saber que el curso funciona.
      </p>

      <form onSubmit={registrar} noValidate className="mt-6 space-y-6">
        <div>
          <label htmlFor="link" className="block font-semibold">
            El link de tu página
          </label>
          <p className="text-marron">Copialo tal cual desde la barra del navegador.</p>
          <input
            id="link"
            type="text"
            inputMode="url"
            autoCapitalize="none"
            autoCorrect="off"
            spellCheck={false}
            maxLength={500}
            className="campo mt-2"
            value={link}
            onChange={(e) => setLink(e.target.value)}
          />
        </div>

        <div>
          <label htmlFor="titulo-link" className="block font-semibold">
            Un nombre para tu página <span className="font-normal text-marron">(si querés)</span>
          </label>
          <input
            id="titulo-link"
            type="text"
            maxLength={120}
            className="campo mt-2"
            value={titulo}
            onChange={(e) => setTitulo(e.target.value)}
          />
        </div>

        <fieldset className="space-y-4">
          <legend className="font-semibold">¿Qué podemos hacer con tu link?</legend>
          <p className="text-marron">
            Las dos vienen sin marcar. Si las dejás así, el link queda registrado igual y no se muestra en ningún lado.
          </p>
          <label className="flex gap-3">
            <input type="checkbox" checked={galeria} onChange={(e) => setGaleria(e.target.checked)} />
            <span>
              Se puede mostrar en la galería del curso, a la vista de cualquiera. Aparece recién cuando lo aprobamos.
            </span>
          </label>
          <label className="flex gap-3">
            <input type="checkbox" checked={contenido} onChange={(e) => setContenido(e.target.checked)} />
            <span>{textoUsoContenido(autorNombre)}</span>
          </label>
        </fieldset>

        {error && <MensajeError mensaje={error} />}
        <button type="submit" className="boton w-full" disabled={enviando}>
          {enviando ? 'Registrando…' : 'Registrar mi link'}
        </button>
      </form>
    </Pagina>
  )
}
