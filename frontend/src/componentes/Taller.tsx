import { useState, type FormEvent } from 'react'
import { api, type Herramienta, type Sistema, type Yo } from '../lib/api.ts'
import { MensajeError, mensajeDe } from './Estados.tsx'

const HERRAMIENTAS: { valor: Herramienta; nombre: string; detalle: string }[] = [
  { valor: 'codex', nombre: 'Codex, en la app de ChatGPT', detalle: 'Si usás ChatGPT, con o sin pago, o no usás ninguna.' },
  { valor: 'claude', nombre: 'Claude Code, en la app de Claude', detalle: 'Si tenés Claude Pro (se paga).' },
]

const SISTEMAS: { valor: Sistema; nombre: string }[] = [
  { valor: 'mac', nombre: 'Mac' },
  { valor: 'windows', nombre: 'Windows' },
  { valor: 'otro', nombre: 'Otra (Linux, tablet o solo celular)' },
]

const NOMBRE_CORTO: Record<Herramienta, string> = { codex: 'Codex', claude: 'Claude' }

const FALTA_COMPU =
  'Para seguir con el curso necesitás una computadora Mac o Windows. Tu avance queda guardado: cuando la tengas, entrá desde ahí con tu mail y seguís desde acá.'

/** Primer texto legible de la respuesta de PUT /taller (con "otro" trae qué hace falta). */
function textoDe(respuesta: unknown): string | null {
  if (!respuesta || typeof respuesta !== 'object') return null
  for (const clave of ['mensaje', 'detalle', 'falta', 'texto']) {
    const valor = (respuesta as Record<string, unknown>)[clave]
    if (typeof valor === 'string' && valor.trim()) return valor
  }
  return null
}

interface Props {
  yo: Yo
  alCambiar: () => void
}

/** Módulo 3: elegir herramienta y sistema y bajar el kit personalizado. */
export default function Taller({ yo, alCambiar }: Props) {
  const tallerHerramienta = yo.taller.herramienta
  const tallerSistema = yo.taller.sistema
  const [herramienta, setHerramienta] = useState<Herramienta | null>(tallerHerramienta)
  const [sistema, setSistema] = useState<Sistema | null>(tallerSistema)
  const [guardado, setGuardado] = useState<{ herramienta: Herramienta; sistema: Sistema } | null>(
    tallerHerramienta && tallerSistema ? { herramienta: tallerHerramienta, sistema: tallerSistema } : null,
  )
  const [nota, setNota] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [ocupado, setOcupado] = useState(false)
  const [kit, setKit] = useState<{ nombre?: string; error?: string } | null>(null)
  const [bajando, setBajando] = useState(false)

  // Si la elección cambia afuera (el tutor la registra en el chat), el formulario se pone al día.
  // Si lo que llega es lo mismo que acaba de guardar este formulario, se deja todo como está.
  const [visto, setVisto] = useState({ herramienta: tallerHerramienta, sistema: tallerSistema })
  if (visto.herramienta !== tallerHerramienta || visto.sistema !== tallerSistema) {
    setVisto({ herramienta: tallerHerramienta, sistema: tallerSistema })
    const propio = guardado?.herramienta === tallerHerramienta && guardado?.sistema === tallerSistema
    if (!propio) {
      setHerramienta(tallerHerramienta)
      setSistema(tallerSistema)
      setGuardado(tallerHerramienta && tallerSistema ? { herramienta: tallerHerramienta, sistema: tallerSistema } : null)
      setNota(null)
      setKit(null)
      setError(null)
    }
  }

  async function guardar(evento: FormEvent) {
    evento.preventDefault()
    if (!herramienta || !sistema) {
      setError('Elegí una herramienta y una computadora.')
      return
    }
    setError(null)
    setOcupado(true)
    try {
      const respuesta = await api.elegirTaller(herramienta, sistema)
      setGuardado({ herramienta, sistema })
      setNota(sistema === 'otro' ? textoDe(respuesta) : null)
      setKit(null)
      alCambiar()
    } catch (e) {
      setError(mensajeDe(e))
    } finally {
      setOcupado(false)
    }
  }

  async function bajarKit() {
    setBajando(true)
    setKit(null)
    try {
      const nombre = await api.descargarKit()
      setKit({ nombre })
      alCambiar()
    } catch (e) {
      setKit({ error: mensajeDe(e) })
    } finally {
      setBajando(false)
    }
  }

  const puedeBajar = guardado !== null && guardado.sistema !== 'otro'
  const faltaCompu = guardado?.sistema === 'otro'
  const nombreHerramienta = guardado ? NOMBRE_CORTO[guardado.herramienta] : ''

  return (
    <section id="kit" aria-labelledby="taller" className="tarjeta mt-8 scroll-mt-4">
      <p className="etiqueta">Tu taller</p>
      <h2 id="taller" className="mt-1 text-[1.5rem] font-bold">
        Tu herramienta y tu kit
      </h2>
      <p className="mt-2">
        Si no sabés cuál elegir, preguntale al tutor: te recomienda una según lo que ya tenés, con su costo real y la
        fecha en que lo verificamos.
      </p>

      <form onSubmit={guardar} className="mt-5 space-y-6">
        <fieldset className="space-y-3">
          <legend className="font-semibold">¿Qué herramienta vas a usar?</legend>
          {HERRAMIENTAS.map((opcion) => (
            <label key={opcion.valor} className="flex gap-3">
              <input
                type="radio"
                name="herramienta"
                value={opcion.valor}
                checked={herramienta === opcion.valor}
                onChange={() => setHerramienta(opcion.valor)}
              />
              <span>
                <span className="block">{opcion.nombre}</span>
                <span className="block text-marron">{opcion.detalle}</span>
              </span>
            </label>
          ))}
        </fieldset>

        <fieldset className="space-y-3">
          <legend className="font-semibold">¿Qué computadora vas a usar?</legend>
          {SISTEMAS.map((opcion) => (
            <label key={opcion.valor} className="flex gap-3">
              <input
                type="radio"
                name="sistema"
                value={opcion.valor}
                checked={sistema === opcion.valor}
                onChange={() => setSistema(opcion.valor)}
              />
              <span>{opcion.nombre}</span>
            </label>
          ))}
        </fieldset>

        {error && <MensajeError mensaje={error} />}
        <button type="submit" className={`boton w-full ${puedeBajar ? 'boton-sec' : ''}`} disabled={ocupado}>
          {ocupado ? 'Guardando…' : 'Guardar mi elección'}
        </button>
      </form>

      {faltaCompu && (
        <div role="status" className="aviso mt-5">
          <p>{nota ?? FALTA_COMPU}</p>
        </div>
      )}

      {puedeBajar && (
        <div className="mt-8 border-t border-linea pt-6">
          <h3 className="text-[1.25rem] font-bold">Tu kit</h3>
          <p className="mt-2">
            Es una carpeta con tu idea adentro y las lecciones de los módulos 4 a 7. La abrís en {nombreHerramienta} y
            ahí sigue el curso.
          </p>
          <button type="button" className="boton mt-4 w-full" onClick={() => void bajarKit()} disabled={bajando}>
            {bajando ? 'Armando tu kit…' : 'Bajar mi kit'}
          </button>
          {kit?.error && (
            <div className="mt-4">
              <MensajeError mensaje={kit.error} />
            </div>
          )}
          {kit?.nombre && (
            <div role="status" className="aviso aviso-logro mt-4 space-y-2">
              <p className="font-semibold">Listo, bajaste {kit.nombre}.</p>
              <p>
                Descomprimilo (en Windows: clic derecho y "Extraer todo") y guardá la carpeta en un lugar fijo, que no
                sea Descargas ni el escritorio.
              </p>
              <p>Adentro hay un archivo LEEME.txt con los pasos para abrirla en {nombreHerramienta}.</p>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
