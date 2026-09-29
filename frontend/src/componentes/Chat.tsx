import { useCallback, useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react'
import { Link } from 'react-router-dom'
import {
  ErrorApi,
  alcanceDeTope,
  api,
  type Alcance,
  type EventoTurno,
  type Herramienta,
  type Mensaje,
  type PedidoTurno,
  type Sistema,
} from '../lib/api.ts'
import { useConfig } from './Configuracion.tsx'
import Escuchar from './Escuchar.tsx'
import { MensajeError, mensajeDe } from './Estados.tsx'
import IdeaGuardada from './IdeaGuardada.tsx'
import Microfono from './Microfono.tsx'
import SubirCaptura from './SubirCaptura.tsx'
import TextoMd from './TextoMd.tsx'

const MAX_TEXTO = 4000

const HERRAMIENTAS: Record<string, string> = {
  guardar_idea: 'Guardando tu idea',
  marcar_avance: 'Anotando tu avance',
  consultar_machete: 'Buscando el dato actualizado',
}

interface Burbuja {
  id: number
  rol: 'tutor' | 'alumno'
  texto: string
  captura?: string
  completa: boolean
}

interface Falla {
  mensaje: string
  reintentable: boolean
  /** Falló al abrir la sesión (y no un turno). */
  alAbrir?: boolean
}

interface Props {
  modulo: number
  /** Muestra el botón para subir capturas (módulo 3). */
  conCaptura?: boolean
  alTope: (alcance: Alcance) => void
  alAvance?: (moduloActual: number) => void
  /** El tutor registró la herramienta y la computadora (registrar_taller, módulo 3). */
  alTaller?: (taller: { herramienta: Herramienta | null; sistema: Sistema | null }) => void
  /**
   * Versión de la idea ya guardada al abrir el módulo 2 sin terminarlo. Al retomar la charla, el cuadro
   * de la idea vuelve a mostrarse (el mensaje del tutor sigue mandando a tocar sus botones).
   */
  ideaAlAbrir?: number | null
}

interface UltimoTurno {
  sesion: number
  pedido: PedidoTurno
  /** El servidor recibió el turno (respondió 200): el mensaje ya quedó guardado. */
  llego: boolean
}

let proximoId = 1
const nuevoId = () => proximoId++

const aBurbujas = (mensajes: Mensaje[] | undefined): Burbuja[] =>
  (mensajes ?? [])
    .filter((m) => m.texto)
    .map((m) => ({ id: nuevoId(), rol: m.rol, texto: m.texto, completa: true }))

export default function Chat({ modulo, conCaptura = false, alTope, alAvance, alTaller, ideaAlAbrir = null }: Props) {
  // En modo demo no hay voz (ni dictado ni Escuchar): el backend no tiene claves para eso.
  const conVoz = !useConfig().modoDemo
  const [sesionId, setSesionId] = useState<number | null>(null)
  const [burbujas, setBurbujas] = useState<Burbuja[]>([])
  const [estado, setEstado] = useState<'abriendo' | 'listo' | 'pensando' | 'escribiendo'>('abriendo')
  const [herramienta, setHerramienta] = useState<string | null>(null)
  const [falla, setFalla] = useState<Falla | null>(null)
  const [ideaGuardada, setIdeaGuardada] = useState<number | null>(null)
  const [avance, setAvance] = useState<{ completado: number; actual: number } | null>(null)
  const [borrador, setBorrador] = useState('')
  const [captura, setCaptura] = useState<{ imagen: Blob; url: string } | null>(null)

  const iniciado = useRef(false)
  // Hasta que la persona escribe (o retoma una charla), no se mueve la página: arriba está el audio.
  const seguir = useRef(false)
  const ultimoTurno = useRef<UltimoTurno | null>(null)
  const urls = useRef<string[]>([])
  const fin = useRef<HTMLDivElement>(null)
  const callbacks = useRef({ alTope, alAvance, alTaller })
  callbacks.current = { alTope, alAvance, alTaller }
  const ideaInicial = useRef(ideaAlAbrir)
  ideaInicial.current = ideaAlAbrir

  useEffect(() => {
    const creadas = urls.current
    return () => creadas.forEach((url) => URL.revokeObjectURL(url))
  }, [])

  const bajar = useCallback((comportamiento: ScrollBehavior) => {
    const destino = fin.current
    if (destino && typeof destino.scrollIntoView === 'function') {
      destino.scrollIntoView({ behavior: comportamiento, block: 'end' })
    }
  }, [])

  const mandar = useCallback(
    async (sesion: number, pedido: PedidoTurno) => {
      setFalla(null)
      setEstado('pensando')
      let tutorId: number | null = null
      let cerrado = false
      // Lo que el tutor escribe después de usar una herramienta va en un párrafo aparte (como al
      // recargar, que el servidor une los bloques de texto con una línea en blanco).
      let separar = false

      const alEvento = (evento: EventoTurno) => {
        switch (evento.tipo) {
          case 'pensando':
            setEstado('pensando')
            break
          case 'texto': {
            if (!evento.delta) break
            setEstado('escribiendo')
            setHerramienta(null)
            if (tutorId === null) {
              const id = nuevoId()
              tutorId = id
              setBurbujas((previas) => [...previas, { id, rol: 'tutor', texto: evento.delta, completa: false }])
            } else {
              const id = tutorId
              const delta = separar ? `\n\n${evento.delta}` : evento.delta
              setBurbujas((previas) => previas.map((b) => (b.id === id ? { ...b, texto: b.texto + delta } : b)))
            }
            separar = false
            break
          }
          case 'herramienta':
            setHerramienta(evento.estado === 'inicio' ? (HERRAMIENTAS[evento.nombre] ?? 'Un momento') : null)
            if (evento.estado === 'fin') separar = true
            break
          case 'idea':
            setIdeaGuardada(evento.version)
            break
          case 'avance':
            setAvance({ completado: evento.modulo_completado, actual: evento.modulo_actual })
            callbacks.current.alAvance?.(evento.modulo_actual)
            break
          case 'taller':
            callbacks.current.alTaller?.({ herramienta: evento.herramienta, sistema: evento.sistema })
            break
          case 'fin':
            cerrado = true
            break
          case 'tope':
            cerrado = true
            callbacks.current.alTope(evento.alcance)
            break
          case 'error':
            cerrado = true
            setFalla({ mensaje: evento.mensaje, reintentable: evento.reintentable })
            break
        }
      }

      let llego = false
      try {
        await api.turno(sesion, pedido, alEvento)
        // Respondió 200: el mensaje quedó guardado, aunque la respuesta se haya cortado.
        llego = true
        if (!cerrado) setFalla({ mensaje: 'Se cortó la respuesta. Probá de nuevo.', reintentable: true })
      } catch (e) {
        const reintentable = !(e instanceof ErrorApi) || e.status === 0 || e.status >= 500 || e.status === 429
        setFalla({ mensaje: mensajeDe(e), reintentable })
      } finally {
        ultimoTurno.current = { sesion, pedido, llego }
        const id = tutorId
        if (id !== null) setBurbujas((previas) => previas.map((b) => (b.id === id ? { ...b, completa: true } : b)))
        setHerramienta(null)
        setEstado('listo')
      }
    },
    [],
  )

  /**
   * Después de una falla con el turno ya guardado: trae la conversación como quedó en el servidor
   * (sin lo que llegó a medias) y, si el último mensaje de la persona sigue sin respuesta, pide que
   * el tutor siga desde ahí con un turno vacío. Así el mensaje no se manda dos veces.
   */
  const seguirDesdeElServidor = useCallback(
    async (sesion: number) => {
      setFalla(null)
      setEstado('pensando')
      try {
        const { mensajes, pendiente } = await api.sesion(sesion)
        setBurbujas(aBurbujas(mensajes))
        if (pendiente) await mandar(sesion, { texto: '' })
        else setEstado('listo')
      } catch (e) {
        setEstado('listo')
        setFalla({ mensaje: mensajeDe(e), reintentable: true })
      }
    },
    [mandar],
  )

  const abrir = useCallback(async () => {
    setFalla(null)
    setEstado('abriendo')
    try {
      const sesion = await api.abrirSesion(modulo)
      setSesionId(sesion.id)
      if (sesion.retomada) {
        const { mensajes, pendiente } = await api.sesion(sesion.id)
        const visibles = aBurbujas(mensajes)
        if (visibles.length > 0) {
          seguir.current = visibles.length > 2
          setBurbujas(visibles)
          // Si el tutor ya guardó la idea y la última palabra fue suya, la persona sigue en el cuadro de la idea.
          if (modulo === 2 && ideaInicial.current !== null && !pendiente && visibles[visibles.length - 1].rol === 'tutor') {
            setIdeaGuardada(ideaInicial.current)
          }
          // Si el último mensaje de la persona quedó sin respuesta (se cortó), se la pide ahora.
          if (pendiente) await mandar(sesion.id, { texto: '' })
          else setEstado('listo')
          return
        }
      }
      await mandar(sesion.id, { texto: '' })
    } catch (e) {
      const alcance = alcanceDeTope(e)
      if (alcance) {
        callbacks.current.alTope(alcance)
        return
      }
      setEstado('listo')
      setFalla({ mensaje: mensajeDe(e), reintentable: true, alAbrir: true })
    }
  }, [modulo, mandar])

  useEffect(() => {
    if (iniciado.current) return
    iniciado.current = true
    void abrir()
  }, [abrir])

  // Un mensaje nuevo se muestra; mientras el tutor escribe, se lo sigue solo si la persona está
  // abajo de todo (si subió a releer, no se la mueve).
  useEffect(() => {
    if (seguir.current && burbujas.length > 0) bajar('smooth')
  }, [burbujas.length, bajar])

  useEffect(() => {
    if (seguir.current && estado === 'pensando') bajar('smooth')
  }, [estado, bajar])

  // El cuadro de la idea es alto y llega después del texto: se baja hasta él para que sus botones no
  // queden detrás de la barra de escribir (el "sigo solo si estoy cerca" de abajo no alcanza).
  useEffect(() => {
    if (seguir.current && ideaGuardada !== null) bajar('smooth')
  }, [ideaGuardada, bajar])

  useEffect(() => {
    const destino = fin.current
    if (!seguir.current || !destino) return
    // Cerca del final del chat (no de la página, que tiene el pie abajo).
    if (destino.getBoundingClientRect().top - window.innerHeight < 320) bajar('auto')
  }, [burbujas, bajar])

  function reintentar() {
    const ultimo = ultimoTurno.current
    if (falla?.alAbrir || !ultimo) {
      void abrir()
      return
    }
    // Si el turno llegó al servidor, el mensaje ya está guardado: se sigue desde ahí. Si nunca
    // llegó (sin conexión, o un estado que no es 200), se manda de nuevo tal cual.
    if (ultimo.llego) void seguirDesdeElServidor(ultimo.sesion)
    else void mandar(ultimo.sesion, ultimo.pedido)
  }

  function enviar(evento?: FormEvent) {
    evento?.preventDefault()
    const texto = borrador.trim()
    if ((!texto && !captura) || sesionId === null || estado !== 'listo') return
    seguir.current = true
    setBurbujas((previas) => [
      ...previas,
      { id: nuevoId(), rol: 'alumno', texto, captura: captura?.url, completa: true },
    ])
    setBorrador('')
    const imagen = captura?.imagen ?? null
    setCaptura(null)
    setIdeaGuardada(null)
    void mandar(sesionId, { texto: texto || undefined, imagen })
  }

  /** Un botón de respuesta rápida (los de la idea guardada): le llega al tutor como si lo hubiera escrito. */
  function responder(texto: string) {
    if (sesionId === null || estado !== 'listo') return
    seguir.current = true
    setBurbujas((previas) => [...previas, { id: nuevoId(), rol: 'alumno', texto, completa: true }])
    setIdeaGuardada(null)
    void mandar(sesionId, { texto })
  }

  function alTeclear(evento: KeyboardEvent<HTMLTextAreaElement>) {
    if (evento.key === 'Enter' && (evento.metaKey || evento.ctrlKey)) enviar()
  }

  function elegirCaptura(imagen: Blob) {
    const url = URL.createObjectURL(imagen)
    urls.current.push(url)
    setCaptura({ imagen, url })
  }

  const ocupado = estado !== 'listo' || sesionId === null
  const siguiente = avance && avance.actual > modulo && avance.actual <= 3 ? avance.actual : null
  // El módulo 3 se termina con el tutor, pero al 4 se pasa bajando el kit (más abajo en la página).
  const faltaKit = avance !== null && avance.completado === 3 && avance.actual <= 3

  return (
    <section aria-label="Conversación con el tutor" className="mt-6">
      <ol className="space-y-5">
        {burbujas.map((b) =>
          b.rol === 'tutor' ? (
            <li key={b.id} className="max-w-[95%]">
              <p className="etiqueta">Tutor</p>
              <div className="mt-1 rounded-lg rounded-tl-none border border-linea bg-hoja px-4 py-3">
                <TextoMd texto={b.texto} bajarTitulos />
              </div>
              {conVoz && b.completa && <Escuchar texto={b.texto} alTope={alTope} />}
            </li>
          ) : (
            <li key={b.id} className="ml-auto max-w-[88%]">
              <p className="etiqueta text-right">Vos</p>
              <div className="mt-1 rounded-lg rounded-tr-none bg-alumno px-4 py-3">
                {b.captura && (
                  <img src={b.captura} alt="Tu captura" className="mb-2 max-h-48 rounded border border-linea" />
                )}
                {b.texto && <p className="whitespace-pre-wrap break-words">{b.texto}</p>}
              </div>
            </li>
          ),
        )}
      </ol>

      <div aria-live="polite" className="mt-4 space-y-4">
        {(estado === 'abriendo' || estado === 'pensando') && (
          <p role="status" className="text-marron">
            <span className="puntos">{herramienta ?? 'El tutor está pensando'}</span>
          </p>
        )}
        {estado === 'escribiendo' && herramienta && (
          <p role="status" className="text-marron">
            <span className="puntos">{herramienta}</span>
          </p>
        )}
        {ideaGuardada !== null &&
          (modulo === 2 ? (
            <IdeaGuardada key={ideaGuardada} deshabilitado={ocupado} alElegir={responder} />
          ) : (
            <div className="aviso aviso-logro">
              <p>Tu idea quedó guardada. Podés leerla, cambiarla y bajarla cuando quieras.</p>
              <Link to="/mi-idea" className="enlace">
                Ver mi idea
              </Link>
            </div>
          ))}
        {avance && (
          <div className="aviso aviso-logro">
            <p className="font-semibold">Terminaste el módulo {avance.completado}.</p>
            {faltaKit ? (
              <>
                <p className="mt-2">Te falta un paso: bajar tu kit, la carpeta con la que seguís el curso.</p>
                <a href="#kit" className="boton mt-3 w-full">
                  Bajar tu kit
                </a>
              </>
            ) : siguiente ? (
              <Link to={`/modulo/${siguiente}`} className="boton mt-3 w-full">
                Seguir con el módulo {siguiente}
              </Link>
            ) : (
              <Link to="/inicio" className="boton mt-3 w-full">
                Volver al inicio
              </Link>
            )}
          </div>
        )}
        {falla && (
          <MensajeError mensaje={falla.mensaje} alReintentar={falla.reintentable ? reintentar : undefined} />
        )}
      </div>

      {/* Al final de la charla y fuera de la barra fija (en el celular ocuparía un tercio de la pantalla).
          Al terminar el módulo, el aviso de avance ya trae el camino: no se repite. */}
      {avance === null && (
        <p className="mt-6 text-[0.9rem] leading-snug text-marron">
          Podés salir cuando quieras: tu conversación queda guardada.{' '}
          <Link to="/inicio" className="enlace">
            Volver al inicio
          </Link>
        </p>
      )}

      <form
        onSubmit={enviar}
        className="sticky bottom-0 mt-6 -mx-4 border-t border-linea bg-papel px-4 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))]"
      >
        {captura && (
          <div className="mb-3 flex items-center gap-3">
            <img src={captura.url} alt="Captura lista para mandar" className="h-16 rounded border border-linea" />
            <div>
              <p>Captura lista. No la guardamos: solo la lee el tutor.</p>
              <button type="button" className="enlace" onClick={() => setCaptura(null)}>
                Quitar
              </button>
            </div>
          </div>
        )}
        <label htmlFor={`mensaje-${modulo}`} className="sr-only">
          Tu mensaje
        </label>
        <textarea
          id={`mensaje-${modulo}`}
          className="campo min-h-[4.5rem]"
          rows={2}
          maxLength={MAX_TEXTO}
          placeholder={conVoz ? 'Escribí acá, o tocá Hablar para dictar' : 'Escribí acá'}
          value={borrador}
          onChange={(e) => setBorrador(e.target.value)}
          onKeyDown={alTeclear}
        />
        {borrador.length > MAX_TEXTO - 400 && (
          <p className="mt-1 text-marron">
            {borrador.length} de {MAX_TEXTO} caracteres
          </p>
        )}
        <div className="mt-3 flex flex-wrap gap-3">
          {conVoz && (
            <Microfono
              alTexto={(dictado) => setBorrador((previo) => (previo.trim() ? `${previo.trim()} ${dictado}` : dictado))}
              alTope={alTope}
            />
          )}
          {conCaptura && <SubirCaptura alElegir={elegirCaptura} deshabilitado={ocupado} />}
          <button type="submit" className="boton min-w-[8rem] flex-1" disabled={ocupado || (!borrador.trim() && !captura)}>
            Enviar
          </button>
        </div>
      </form>
      {/* Al final de todo: al bajar hasta acá, la caja de escribir no tapa el último mensaje. */}
      <div ref={fin} />
    </section>
  )
}
