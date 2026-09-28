/**
 * Cliente de la API de la puerta (specs/001-curso-vibe-coding/contracts/api.md).
 *
 * - Todos los pedidos van con credentials "same-origin" (la cookie de sesión es HttpOnly).
 * - Los errores salen como ErrorApi con el campo "detalle" del servidor, listo para mostrar.
 * - Un 401 en un pedido privado llama al manejador de alNoAutorizado (la app lleva a /entrar).
 */

const MENSAJE_GENERAL = 'Algo falló de nuestro lado. Probá de nuevo en un rato.'
const MENSAJE_SIN_CONEXION = 'No hay conexión. Revisá internet y probá de nuevo.'

export class ErrorApi extends Error {
  readonly status: number
  readonly datos: unknown

  constructor(status: number, detalle: string, datos: unknown = null) {
    super(detalle)
    this.name = 'ErrorApi'
    this.status = status
    this.datos = datos
  }
}

let manejador401: (() => void) | null = null

/** Registra qué hacer cuando la sesión venció (o null para sacarlo). */
export function alNoAutorizado(fn: (() => void) | null): void {
  manejador401 = fn
}

export interface Opciones {
  metodo?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  /** Objeto que se manda como JSON, o FormData tal cual. */
  cuerpo?: unknown
  /** Pedido público o de entrada: un 401 no lleva a /entrar. */
  publico?: boolean
  signal?: AbortSignal
  aceptar?: string
}

async function llamar(ruta: string, opciones: Opciones = {}): Promise<Response> {
  const cabeceras = new Headers({ Accept: opciones.aceptar ?? 'application/json' })
  let cuerpo: BodyInit | undefined
  if (opciones.cuerpo instanceof FormData) {
    cuerpo = opciones.cuerpo
  } else if (opciones.cuerpo !== undefined) {
    cabeceras.set('Content-Type', 'application/json')
    cuerpo = JSON.stringify(opciones.cuerpo)
  }
  let respuesta: Response
  try {
    respuesta = await fetch(ruta, {
      method: opciones.metodo ?? 'GET',
      credentials: 'same-origin',
      headers: cabeceras,
      body: cuerpo,
      signal: opciones.signal,
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw error
    throw new ErrorApi(0, MENSAJE_SIN_CONEXION)
  }
  if (respuesta.status === 401 && !opciones.publico) manejador401?.()
  return respuesta
}

async function leerCuerpo(respuesta: Response): Promise<unknown> {
  const texto = await respuesta.text().catch(() => '')
  if (!texto) return null
  try {
    return JSON.parse(texto)
  } catch {
    return texto
  }
}

async function comoError(respuesta: Response): Promise<ErrorApi> {
  const datos = await leerCuerpo(respuesta)
  const detalle =
    datos && typeof datos === 'object' && typeof (datos as { detalle?: unknown }).detalle === 'string'
      ? (datos as { detalle: string }).detalle
      : MENSAJE_GENERAL
  return new ErrorApi(respuesta.status, detalle, datos)
}

/** Pedido JSON. Devuelve el cuerpo ya leído o levanta ErrorApi. */
export async function pedir<T>(ruta: string, opciones: Opciones = {}): Promise<T> {
  const respuesta = await llamar(ruta, opciones)
  if (!respuesta.ok) throw await comoError(respuesta)
  return (await leerCuerpo(respuesta)) as T
}

function nombreDeArchivo(respuesta: Response, porDefecto: string): string {
  const disposicion = respuesta.headers.get('Content-Disposition') ?? ''
  const codificado = /filename\*\s*=\s*(?:UTF-8'')?([^;]+)/i.exec(disposicion)
  if (codificado) {
    try {
      return decodeURIComponent(codificado[1].trim().replace(/^"|"$/g, ''))
    } catch {
      /* sigue con filename= */
    }
  }
  const simple = /filename\s*=\s*"?([^";]+)"?/i.exec(disposicion)
  return simple ? simple[1].trim() : porDefecto
}

/** Baja un archivo de la API (con la sesión) y lo guarda en el dispositivo. Devuelve el nombre. */
export async function descargar(ruta: string, porDefecto: string): Promise<string> {
  const respuesta = await llamar(ruta, { aceptar: '*/*' })
  if (!respuesta.ok) throw await comoError(respuesta)
  const nombre = nombreDeArchivo(respuesta, porDefecto)
  const blob = await respuesta.blob()
  const url = URL.createObjectURL(blob)
  const enlace = document.createElement('a')
  enlace.href = url
  enlace.download = nombre
  enlace.rel = 'noopener'
  document.body.appendChild(enlace)
  enlace.click()
  enlace.remove()
  setTimeout(() => URL.revokeObjectURL(url), 60_000)
  return nombre
}

// ---------------------------------------------------------------------------
// Lector de SSE (EventSource no manda POST)
// ---------------------------------------------------------------------------

export interface EventoSSE {
  evento: string
  datos: string
}

/** Lee un text/event-stream y llama a alEvento por cada evento completo. */
export async function leerSSE(
  cuerpo: ReadableStream<Uint8Array>,
  alEvento: (evento: EventoSSE) => void,
): Promise<void> {
  const lector = cuerpo.getReader()
  const decodificador = new TextDecoder('utf-8')
  let resto = ''
  let evento = ''
  let datos: string[] = []

  const despachar = () => {
    if (datos.length > 0) alEvento({ evento: evento || 'message', datos: datos.join('\n') })
    evento = ''
    datos = []
  }

  const procesarLinea = (linea: string) => {
    if (linea === '') {
      despachar()
      return
    }
    if (linea.startsWith(':')) return
    const dosPuntos = linea.indexOf(':')
    const campo = dosPuntos === -1 ? linea : linea.slice(0, dosPuntos)
    let valor = dosPuntos === -1 ? '' : linea.slice(dosPuntos + 1)
    if (valor.startsWith(' ')) valor = valor.slice(1)
    if (campo === 'event') evento = valor
    else if (campo === 'data') datos.push(valor)
  }

  const procesar = (texto: string, final: boolean) => {
    resto += texto
    let inicio = 0
    for (let i = 0; i < resto.length; i++) {
      const caracter = resto[i]
      if (caracter !== '\n' && caracter !== '\r') continue
      // Un \r al final puede ser la mitad de un \r\n: se espera al próximo pedazo.
      if (caracter === '\r' && i === resto.length - 1 && !final) break
      procesarLinea(resto.slice(inicio, i))
      if (caracter === '\r' && resto[i + 1] === '\n') i++
      inicio = i + 1
    }
    resto = resto.slice(inicio)
  }

  try {
    for (;;) {
      const { done, value } = await lector.read()
      if (done) break
      procesar(decodificador.decode(value, { stream: true }), false)
    }
    procesar(decodificador.decode(), true)
    if (resto) procesarLinea(resto)
    resto = ''
    despachar()
  } finally {
    lector.releaseLock()
  }
}

// ---------------------------------------------------------------------------
// Tipos del contrato
// ---------------------------------------------------------------------------

export interface Config {
  turnstile_site_key: string | null
  aviso_prueba: boolean
  /** AUTOR_NOMBRE de la instalación, o null (textos genéricos). */
  autor_nombre?: string | null
  /** NEWSLETTER_NOMBRE de la instalación, o null (sin casilla de novedades). */
  newsletter?: string | null
  /** MODO_DEMO: el tutor sigue un guion fijo, sin IA ni voz. */
  modo_demo?: boolean
}

export interface Consentimientos {
  mails_curso: boolean
  transferencia: boolean
  /** Opcional: recibir las novedades del autor por el newsletter configurado. */
  novedades: boolean
}

export interface TextosLegales {
  version: string
  textos: Partial<Record<keyof Consentimientos, string>>
  texto_md: string
}

export interface Privacidad {
  version: string
  titulo: string
  texto_md: string
}

export interface Audio {
  modulo: number
  url: string
  transcripcion?: string | null
}

export interface Yo {
  email: string
  modulo_actual: number
  avance: { modulo: number; completado: string; via: string }[]
  idea: { version: number; actualizada: string } | null
  taller: { herramienta: Herramienta | null; sistema: Sistema | null }
  tope: { bloqueado: boolean; alcance: Alcance | null }
  consentimientos: { mails_curso: boolean; novedades: boolean }
  audios: Audio[]
  es_admin?: boolean
}

export type Alcance = 'alumno' | 'mes'
export type Herramienta = 'codex' | 'claude'
export type Sistema = 'mac' | 'windows' | 'otro'

export interface Guia {
  modulo: number
  titulo: string
  guia_md: string
  audio?: unknown
}

export interface Sesion {
  id: number
  retomada: boolean
}

export interface Mensaje {
  rol: 'tutor' | 'alumno'
  texto: string
}

export interface Idea {
  version: number
  texto_md: string
  que_sigue_md: string | null
  autor: string
  creado: string
}

export interface LinkGaleria {
  titulo: string | null
  url: string
}

export interface PedidoLink {
  url: string
  titulo: string | null
  mostrar_galeria: boolean
  uso_contenido: boolean
}

/** Un link propio (GET /links). La galería lo muestra solo con mostrar_galeria y aprobado. */
export interface LinkPropio {
  id: number
  url: string
  titulo: string | null
  mostrar_galeria: boolean
  uso_contenido: boolean
  aprobado: boolean
  creado: string
}

export type CambiosLink = Partial<Pick<LinkPropio, 'mostrar_galeria' | 'uso_contenido'>>

/** Un link que alguien pidió mostrar en la galería (GET /admin/links, pendientes primero). */
export interface LinkPorAprobar {
  id: number
  url: string
  titulo: string | null
  mostrar_galeria: boolean
  aprobado: boolean
  creado: string
}

export type EventoTurno =
  | { tipo: 'pensando' }
  | { tipo: 'texto'; delta: string }
  | { tipo: 'herramienta'; nombre: string; estado: 'inicio' | 'fin'; error: boolean }
  | { tipo: 'avance'; modulo_completado: number; modulo_actual: number }
  | { tipo: 'idea'; version: number }
  | { tipo: 'taller'; herramienta: Herramienta | null; sistema: Sistema | null }
  | { tipo: 'fin'; stop_reason: string }
  | { tipo: 'tope'; alcance: Alcance; guia: string }
  | { tipo: 'error'; mensaje: string; reintentable: boolean }

const texto = (v: unknown, porDefecto = ''): string => (typeof v === 'string' ? v : porDefecto)
const numero = (v: unknown): number => (typeof v === 'number' && Number.isFinite(v) ? v : 0)
const alcance = (v: unknown): Alcance => (v === 'mes' ? 'mes' : 'alumno')
const herramienta = (v: unknown): Herramienta | null => (v === 'codex' || v === 'claude' ? v : null)
const sistema = (v: unknown): Sistema | null => (v === 'mac' || v === 'windows' || v === 'otro' ? v : null)

/** Traduce un evento SSE del turno al tipo del contrato; null si no se entiende. */
export function aEventoTurno({ evento, datos }: EventoSSE): EventoTurno | null {
  let d: Record<string, unknown>
  try {
    const leido: unknown = JSON.parse(datos || '{}')
    d = leido && typeof leido === 'object' ? (leido as Record<string, unknown>) : {}
  } catch {
    return null
  }
  switch (evento) {
    case 'pensando':
      return { tipo: 'pensando' }
    case 'texto':
      return { tipo: 'texto', delta: texto(d.delta) }
    case 'herramienta':
      return {
        tipo: 'herramienta',
        nombre: texto(d.nombre),
        estado: d.estado === 'fin' ? 'fin' : 'inicio',
        error: d.error === true,
      }
    case 'avance':
      return { tipo: 'avance', modulo_completado: numero(d.modulo_completado), modulo_actual: numero(d.modulo_actual) }
    case 'idea':
      return { tipo: 'idea', version: numero(d.version) }
    case 'taller':
      return { tipo: 'taller', herramienta: herramienta(d.herramienta), sistema: sistema(d.sistema) }
    case 'fin':
      return { tipo: 'fin', stop_reason: texto(d.stop_reason) }
    case 'tope':
      return { tipo: 'tope', alcance: alcance(d.alcance), guia: texto(d.guia) }
    case 'error':
      return {
        tipo: 'error',
        mensaje: texto(d.mensaje, 'El tutor no pudo responder.'),
        reintentable: d.reintentable !== false,
      }
    default:
      return null
  }
}

export interface PedidoTurno {
  texto?: string
  imagen?: Blob | null
}

function extension(tipo: string): string {
  if (tipo === 'image/png') return 'png'
  if (tipo === 'image/webp') return 'webp'
  return 'jpg'
}

/**
 * Manda un turno al tutor y reparte los eventos a medida que llegan. Un 402 llega como evento tope.
 *
 * Si termina sin levantar error, el servidor recibió el turno (respondió 200) y el mensaje quedó
 * guardado, aunque el stream se haya cortado antes del evento "fin". Si levanta ErrorApi, el turno
 * no llegó: sin conexión (status 0) o con un estado que no es 200.
 */
async function turno(
  sesionId: number,
  pedido: PedidoTurno,
  alEvento: (evento: EventoTurno) => void,
  signal?: AbortSignal,
): Promise<void> {
  const datos = new FormData()
  if (pedido.texto !== undefined) datos.append('texto', pedido.texto)
  if (pedido.imagen) datos.append('imagen', pedido.imagen, `captura.${extension(pedido.imagen.type)}`)
  const respuesta = await llamar(`/api/sesiones/${sesionId}/turno`, {
    metodo: 'POST',
    cuerpo: datos,
    signal,
    aceptar: 'text/event-stream',
  })
  if (respuesta.status === 402) {
    const cuerpo = (await leerCuerpo(respuesta)) as Record<string, unknown> | null
    alEvento({ tipo: 'tope', alcance: alcance(cuerpo?.alcance), guia: texto(cuerpo?.guia) })
    return
  }
  if (!respuesta.ok) throw await comoError(respuesta)
  if (!respuesta.body) throw new ErrorApi(respuesta.status, MENSAJE_GENERAL)
  try {
    await leerSSE(respuesta.body, (crudo) => {
      const evento = aEventoTurno(crudo)
      if (evento) alEvento(evento)
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw error
    // Se cortó la conexión a mitad de la respuesta: el turno ya llegó. Quien llama lo nota porque
    // no vino el evento "fin".
  }
}

/** Error de tope (402) al abrir una sesión o usar la voz. */
export function alcanceDeTope(error: unknown): Alcance | null {
  if (!(error instanceof ErrorApi) || error.status !== 402) return null
  const datos = error.datos as { alcance?: unknown } | null
  return alcance(datos?.alcance)
}

async function transcribir(audio: Blob): Promise<string> {
  const datos = new FormData()
  const tipo = audio.type.split(';')[0]
  const ext = tipo.includes('mp4') || tipo.includes('m4a') ? 'm4a' : tipo.includes('ogg') ? 'ogg' : 'webm'
  datos.append('audio', audio, `voz.${ext}`)
  const respuesta = await pedir<{ texto: string }>('/api/voz/transcribir', { metodo: 'POST', cuerpo: datos })
  return respuesta.texto ?? ''
}

async function hablar(frase: string, signal?: AbortSignal): Promise<Blob> {
  const respuesta = await llamar('/api/voz/hablar', {
    metodo: 'POST',
    cuerpo: { texto: frase },
    signal,
    aceptar: 'audio/mpeg',
  })
  if (!respuesta.ok) throw await comoError(respuesta)
  return respuesta.blob()
}

export const api = {
  config: () => pedir<Config>('/api/config', { publico: true }),
  privacidad: () => pedir<Privacidad>('/api/legal/privacidad', { publico: true }),
  textosLegales: () => pedir<TextosLegales>('/api/legal/consentimientos', { publico: true }),

  pedirCodigo: (pedido: {
    email: string
    consentimientos?: Consentimientos
    fuente?: string | null
    turnstile?: string | null
  }) => {
    const cuerpo: Record<string, unknown> = { email: pedido.email }
    if (pedido.consentimientos) cuerpo.consentimientos = pedido.consentimientos
    if (pedido.fuente) cuerpo.fuente = pedido.fuente
    if (pedido.turnstile) cuerpo.turnstile = pedido.turnstile
    return pedir<{ ok: boolean }>('/api/auth/codigo', { metodo: 'POST', cuerpo, publico: true })
  },
  verificar: (email: string, codigo: string) =>
    pedir<{ ok: boolean; nuevo: boolean }>('/api/auth/verificar', {
      metodo: 'POST',
      cuerpo: { email, codigo },
      publico: true,
    }),
  salir: () => pedir<{ ok: boolean }>('/api/auth/salir', { metodo: 'POST', publico: true }),

  yo: (opciones: { publico?: boolean } = {}) => pedir<Yo>('/api/yo', opciones),
  guia: (modulo: number) => pedir<Guia>(`/api/modulos/${modulo}/guia`),
  abrirSesion: (modulo: number) => pedir<Sesion>(`/api/modulos/${modulo}/sesion`, { metodo: 'POST' }),
  sesion: (id: number) =>
    pedir<{ id: number; modulo: number; mensajes: Mensaje[]; pendiente?: boolean }>(`/api/sesiones/${id}`),
  turno,
  completar: (modulo: number) =>
    pedir<{ modulo_actual?: number }>(`/api/modulos/${modulo}/completar`, { metodo: 'POST' }),

  idea: () => pedir<Idea>('/api/idea'),
  plantillaIdea: () => pedir<{ texto_md: string }>('/api/idea/plantilla'),
  guardarIdea: (texto_md: string, que_sigue_md: string) =>
    pedir<{ version: number }>('/api/idea', { metodo: 'PUT', cuerpo: { texto_md, que_sigue_md } }),
  descargarIdea: () => descargar('/api/idea.md', 'mi-idea.md'),

  elegirTaller: (herramienta: Herramienta, sistema: Sistema) =>
    pedir<Record<string, unknown> | null>('/api/taller', { metodo: 'PUT', cuerpo: { herramienta, sistema } }),
  descargarKit: () => descargar('/api/kit', 'mi-proyecto.zip'),

  registrarLink: (pedido: PedidoLink) =>
    pedir<{ id: number; mail?: boolean }>('/api/links', { metodo: 'POST', cuerpo: pedido }),
  misLinks: () => pedir<LinkPropio[]>('/api/links'),
  cambiarLink: (id: number, cambios: CambiosLink) =>
    pedir<LinkPropio>(`/api/links/${id}`, { metodo: 'PATCH', cuerpo: cambios }),
  borrarLink: (id: number) => pedir<unknown>(`/api/links/${id}`, { metodo: 'DELETE' }),
  galeria: () => pedir<LinkGaleria[]>('/api/galeria', { publico: true }),

  cambiarConsentimientos: (cambios: Partial<Pick<Consentimientos, 'mails_curso' | 'novedades'>>) =>
    pedir<unknown>('/api/consentimientos', { metodo: 'PUT', cuerpo: cambios }),
  descargarMisDatos: () => descargar('/api/mis-datos', 'mis-datos.json'),
  borrarMisDatos: () => pedir<unknown>('/api/mis-datos', { metodo: 'DELETE', cuerpo: { confirmar: 'BORRAR' } }),
  baja: (token: string) =>
    pedir<unknown>(`/api/baja?t=${encodeURIComponent(token)}`, { metodo: 'POST', publico: true }),

  transcribir,
  hablar,

  reporte: () => pedir<Record<string, unknown>>('/api/admin/reporte'),
  linksPorAprobar: () => pedir<LinkPorAprobar[]>('/api/admin/links'),
  aprobarLink: (id: number, aprobado: boolean) =>
    pedir<unknown>(`/api/admin/links/${id}`, { metodo: 'PUT', cuerpo: { aprobado } }),
  /** CSV con una columna, email: quienes aceptaron las novedades (para importar en el newsletter). */
  descargarNovedades: () => descargar('/api/admin/novedades.csv', 'novedades.csv'),
}
