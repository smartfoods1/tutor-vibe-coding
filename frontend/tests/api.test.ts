import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  ErrorApi,
  alNoAutorizado,
  api,
  leerSSE,
  pedir,
  type EventoSSE,
  type EventoTurno,
} from '../src/lib/api.ts'
import { cuerpoJson, flujo, flujoBytes, flujoCortado, json, llamadasA, simularFetch } from './ayudas.ts'

afterEach(() => {
  vi.unstubAllGlobals()
  alNoAutorizado(null)
})

async function juntar(pedazos: string[]): Promise<EventoSSE[]> {
  const eventos: EventoSSE[] = []
  await leerSSE(flujo(pedazos), (e) => eventos.push(e))
  return eventos
}

describe('leerSSE', () => {
  it('arma los eventos aunque lleguen partidos en cualquier lugar', async () => {
    const eventos = await juntar([
      'event: pens',
      'ando\ndata: {}\n',
      '\nevent: texto\nda',
      'ta: {"delta":"Hola"}\n\n',
    ])
    expect(eventos).toEqual([
      { evento: 'pensando', datos: '{}' },
      { evento: 'texto', datos: '{"delta":"Hola"}' },
    ])
  })

  it('acepta CRLF, junta varias líneas de datos e ignora comentarios', async () => {
    const eventos = await juntar([': ping\r\n\r\nevent: texto\r\ndata: uno\r\ndata: dos\r\n\r\n'])
    expect(eventos).toEqual([{ evento: 'texto', datos: 'uno\ndos' }])
  })

  it('sin nombre de evento usa "message" y entrega lo que quedó al final', async () => {
    const eventos = await juntar(['data: suelto\n\nevent: fin\ndata: {"stop_reason":"end_turn"}'])
    expect(eventos).toEqual([
      { evento: 'message', datos: 'suelto' },
      { evento: 'fin', datos: '{"stop_reason":"end_turn"}' },
    ])
  })

  it('no rompe los acentos partidos entre dos pedazos', async () => {
    const bytes = new TextEncoder().encode('event: texto\ndata: {"delta":"acción"}\n\n')
    const corte = bytes.indexOf(0xc3) + 1
    const eventos: EventoSSE[] = []
    await leerSSE(flujoBytes([bytes.slice(0, corte), bytes.slice(corte)]), (e) => eventos.push(e))
    expect(JSON.parse(eventos[0].datos)).toEqual({ delta: 'acción' })
  })
})

describe('pedir', () => {
  it('manda la cookie del mismo sitio y devuelve el JSON', async () => {
    const espia = simularFetch({ 'GET /api/yo': json({ email: 'a@ejemplo.com' }) })
    const datos = await pedir<{ email: string }>('/api/yo')
    expect(datos.email).toBe('a@ejemplo.com')
    expect(espia.mock.calls[0][1]?.credentials).toBe('same-origin')
  })

  it('manda el cuerpo como JSON', async () => {
    const espia = simularFetch({ 'PUT /api/idea': json({ version: 2 }) })
    await pedir('/api/idea', { metodo: 'PUT', cuerpo: { texto_md: 'hola' } })
    const [, init] = espia.mock.calls[0]
    expect(cuerpoJson(init)).toEqual({ texto_md: 'hola' })
    expect(new Headers(init?.headers).get('Content-Type')).toBe('application/json')
  })

  it('un error trae el campo detalle para mostrar', async () => {
    simularFetch({ 'GET /api/kit': json({ detalle: 'Primero elegí tu herramienta.' }, 409) })
    const error = await pedir('/api/kit').catch((e: unknown) => e)
    expect(error).toBeInstanceOf(ErrorApi)
    expect((error as ErrorApi).status).toBe(409)
    expect((error as ErrorApi).message).toBe('Primero elegí tu herramienta.')
  })

  it('un error sin detalle muestra un mensaje general', async () => {
    simularFetch({ 'GET /api/yo': new Response('<html>', { status: 502 }) })
    const error = (await pedir('/api/yo').catch((e: unknown) => e)) as ErrorApi
    expect(error.message).toMatch(/probá de nuevo/i)
  })

  it('un 401 lleva a entrar, salvo en los pedidos públicos', async () => {
    const aEntrar = vi.fn()
    alNoAutorizado(aEntrar)
    simularFetch({ 'GET /api/yo': json({ detalle: 'Tu sesión venció.' }, 401) })
    await pedir('/api/yo').catch(() => null)
    expect(aEntrar).toHaveBeenCalledTimes(1)
    await pedir('/api/yo', { publico: true }).catch(() => null)
    expect(aEntrar).toHaveBeenCalledTimes(1)
  })

  it('sin conexión da un mensaje claro', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => Promise.reject(new TypeError('Failed to fetch'))))
    const error = (await pedir('/api/yo').catch((e: unknown) => e)) as ErrorApi
    expect(error.status).toBe(0)
    expect(error.message).toMatch(/conexión/i)
  })
})

describe('api', () => {
  it('pedirCodigo manda el mail, los consentimientos, la fuente y el token', async () => {
    const espia = simularFetch({ 'POST /api/auth/codigo': json({ ok: true }) })
    await api.pedirCodigo({
      email: 'persona@ejemplo.com',
      consentimientos: { mails_curso: true, transferencia: true, novedades: false },
      fuente: 'radio-local',
      turnstile: 'token',
    })
    expect(cuerpoJson(espia.mock.calls[0][1])).toEqual({
      email: 'persona@ejemplo.com',
      consentimientos: { mails_curso: true, transferencia: true, novedades: false },
      fuente: 'radio-local',
      turnstile: 'token',
    })
  })

  it('cambiarConsentimientos manda novedades con ese nombre', async () => {
    const espia = simularFetch({ 'PUT /api/consentimientos': json({ ok: true }) })
    await api.cambiarConsentimientos({ novedades: true })
    expect(cuerpoJson(llamadasA(espia, 'PUT /api/consentimientos')[0][1])).toEqual({ novedades: true })
  })

  it('la lista de novedades se baja de /api/admin/novedades.csv', async () => {
    const espia = simularFetch({
      'GET /api/admin/novedades.csv': new Response('email\n', { headers: { 'Content-Type': 'text/csv' } }),
    })
    vi.stubGlobal('URL', Object.assign(URL, { createObjectURL: vi.fn(() => 'blob:x'), revokeObjectURL: vi.fn() }))
    const clic = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined)
    try {
      expect(await api.descargarNovedades()).toBe('novedades.csv')
      expect(llamadasA(espia, 'GET /api/admin/novedades.csv')).toHaveLength(1)
    } finally {
      clic.mockRestore()
    }
  })

  it('verificar no manda a entrar cuando el código está mal', async () => {
    const aEntrar = vi.fn()
    alNoAutorizado(aEntrar)
    simularFetch({ 'POST /api/auth/verificar': json({ detalle: 'El código no es válido.' }, 401) })
    const error = (await api.verificar('a@ejemplo.com', '123456').catch((e: unknown) => e)) as ErrorApi
    expect(error.message).toBe('El código no es válido.')
    expect(aEntrar).not.toHaveBeenCalled()
  })

  it('los links propios se cambian con PATCH y se borran con DELETE', async () => {
    const espia = simularFetch({
      'GET /api/links': json([]),
      'PATCH /api/links/7': json({ id: 7, mostrar_galeria: true }),
      'DELETE /api/links/7': json({ ok: true }),
    })
    await api.misLinks()
    await api.cambiarLink(7, { mostrar_galeria: true })
    await api.borrarLink(7)
    expect(llamadasA(espia, 'GET /api/links')).toHaveLength(1)
    expect(cuerpoJson(llamadasA(espia, 'PATCH /api/links/7')[0][1])).toEqual({ mostrar_galeria: true })
    expect(llamadasA(espia, 'DELETE /api/links/7')).toHaveLength(1)
  })

  it('la galería por aprobar usa las rutas de admin', async () => {
    const espia = simularFetch({
      'GET /api/admin/links': json([]),
      'PUT /api/admin/links/3': json({ ok: true }),
    })
    await api.linksPorAprobar()
    await api.aprobarLink(3, true)
    expect(llamadasA(espia, 'GET /api/admin/links')).toHaveLength(1)
    expect(cuerpoJson(llamadasA(espia, 'PUT /api/admin/links/3')[0][1])).toEqual({ aprobado: true })
  })

  it('la plantilla de la idea viene del servidor', async () => {
    simularFetch({ 'GET /api/idea/plantilla': json({ texto_md: '# Mi idea' }) })
    expect(await api.plantillaIdea()).toEqual({ texto_md: '# Mi idea' })
  })

  it('baja manda el token en la query', async () => {
    const espia = simularFetch({ 'POST /api/baja': json({ ok: true }) })
    await api.baja('a.b+c/d')
    expect(String(espia.mock.calls[0][0])).toBe('/api/baja?t=a.b%2Bc%2Fd')
  })
})

describe('turno', () => {
  it('manda el texto y la imagen como multipart y reparte los eventos', async () => {
    const cuerpo = [
      'event: pensando\ndata: {}\n\n',
      'event: texto\ndata: {"delta":"Hola, "}\n\n',
      'event: texto\ndata: {"delta":"¿cómo va?"}\n\n',
      'event: herramienta\ndata: {"nombre":"guardar_idea","estado":"inicio","error":false}\n\n',
      'event: idea\ndata: {"version":4}\n\n',
      'event: avance\ndata: {"modulo_completado":2,"modulo_actual":3}\n\n',
      'event: taller\ndata: {"herramienta":"claude","sistema":"windows"}\n\n',
      'event: fin\ndata: {"stop_reason":"end_turn"}\n\n',
    ]
    const espia = simularFetch({
      'POST /api/sesiones/42/turno': () =>
        new Response(flujo(cuerpo), { headers: { 'Content-Type': 'text/event-stream' } }),
    })
    const imagen = new Blob(['x'], { type: 'image/jpeg' })
    const eventos: EventoTurno[] = []
    await api.turno(42, { texto: 'mirá', imagen }, (e) => eventos.push(e))

    const [url, init] = espia.mock.calls[0]
    expect(url).toBe('/api/sesiones/42/turno')
    expect(init?.credentials).toBe('same-origin')
    const datos = init?.body as FormData
    expect(datos).toBeInstanceOf(FormData)
    expect(datos.get('texto')).toBe('mirá')
    expect(datos.get('imagen')).toBeInstanceOf(Blob)

    expect(eventos).toEqual([
      { tipo: 'pensando' },
      { tipo: 'texto', delta: 'Hola, ' },
      { tipo: 'texto', delta: '¿cómo va?' },
      { tipo: 'herramienta', nombre: 'guardar_idea', estado: 'inicio', error: false },
      { tipo: 'idea', version: 4 },
      { tipo: 'avance', modulo_completado: 2, modulo_actual: 3 },
      { tipo: 'taller', herramienta: 'claude', sistema: 'windows' },
      { tipo: 'fin', stop_reason: 'end_turn' },
    ])
  })

  it('si la conexión se corta a mitad del stream, entrega lo que llegó y termina sin levantar error', async () => {
    simularFetch({
      'POST /api/sesiones/4/turno': () =>
        new Response(flujoCortado(['event: texto\ndata: {"delta":"Hola"}\n\n']), {
          headers: { 'Content-Type': 'text/event-stream' },
        }),
    })
    const eventos: EventoTurno[] = []
    await api.turno(4, { texto: 'x' }, (e) => eventos.push(e))
    expect(eventos).toEqual([{ tipo: 'texto', delta: 'Hola' }])
  })

  it('el turno vacío para que el tutor salude manda solo el texto vacío', async () => {
    const espia = simularFetch({
      'POST /api/sesiones/7/turno': () => new Response(flujo(['event: fin\ndata: {}\n\n'])),
    })
    await api.turno(7, { texto: '' }, () => undefined)
    const datos = espia.mock.calls[0][1]?.body as FormData
    expect(datos.get('texto')).toBe('')
    expect(datos.get('imagen')).toBeNull()
  })

  it('un 402 se convierte en el evento tope', async () => {
    simularFetch({
      'POST /api/sesiones/9/turno': json({ detalle: 'tope', alcance: 'mes', guia: '/api/modulos/2/guia' }, 402),
    })
    const eventos: EventoTurno[] = []
    await api.turno(9, { texto: 'hola' }, (e) => eventos.push(e))
    expect(eventos).toEqual([{ tipo: 'tope', alcance: 'mes', guia: '/api/modulos/2/guia' }])
  })

  it('otro error se levanta con su detalle', async () => {
    simularFetch({ 'POST /api/sesiones/9/turno': json({ detalle: 'La sesión no es tuya.' }, 404) })
    await expect(api.turno(9, { texto: 'hola' }, () => undefined)).rejects.toThrow('La sesión no es tuya.')
  })

  it('ignora eventos desconocidos o con datos rotos', async () => {
    simularFetch({
      'POST /api/sesiones/3/turno': () =>
        new Response(flujo(['event: raro\ndata: {}\n\nevent: texto\ndata: no-es-json\n\nevent: fin\ndata: {}\n\n'])),
    })
    const eventos: EventoTurno[] = []
    await api.turno(3, { texto: 'x' }, (e) => eventos.push(e))
    expect(eventos).toEqual([{ tipo: 'fin', stop_reason: '' }])
  })
})

describe('descargas', () => {
  it('baja el archivo con el nombre que manda el servidor', async () => {
    simularFetch({
      'GET /api/kit': new Response('zip', {
        headers: {
          'Content-Type': 'application/zip',
          'Content-Disposition': 'attachment; filename="mi-proyecto-suenos.zip"',
        },
      }),
    })
    const crear = vi.fn(() => 'blob:x')
    vi.stubGlobal('URL', Object.assign(URL, { createObjectURL: crear, revokeObjectURL: vi.fn() }))
    const clic = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined)
    const nombre = await api.descargarKit()
    expect(nombre).toBe('mi-proyecto-suenos.zip')
    expect(crear).toHaveBeenCalledTimes(1)
    expect(clic).toHaveBeenCalledTimes(1)
    clic.mockRestore()
  })

  it('si falta algo muestra el detalle y no baja nada', async () => {
    const espia = simularFetch({ 'GET /api/kit': json({ detalle: 'Falta guardar tu idea.' }, 409) })
    await expect(api.descargarKit()).rejects.toThrow('Falta guardar tu idea.')
    expect(llamadasA(espia, 'GET /api/kit')).toHaveLength(1)
  })
})
