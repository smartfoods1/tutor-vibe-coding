import { vi } from 'vitest'

export function json(datos: unknown, status = 200): Response {
  return new Response(JSON.stringify(datos), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

export function flujo(pedazos: string[]): ReadableStream<Uint8Array> {
  const codificador = new TextEncoder()
  return new ReadableStream({
    start(control) {
      for (const pedazo of pedazos) control.enqueue(codificador.encode(pedazo))
      control.close()
    },
  })
}

/** Un stream que entrega los pedazos y después se corta con un error de red (sin cerrar). */
export function flujoCortado(pedazos: string[]): ReadableStream<Uint8Array> {
  const codificador = new TextEncoder()
  const pendientes = [...pedazos]
  return new ReadableStream({
    pull(control) {
      const pedazo = pendientes.shift()
      if (pedazo === undefined) control.error(new TypeError('network error'))
      else control.enqueue(codificador.encode(pedazo))
    },
  })
}

export function flujoBytes(pedazos: Uint8Array[]): ReadableStream<Uint8Array> {
  return new ReadableStream({
    start(control) {
      for (const pedazo of pedazos) control.enqueue(pedazo)
      control.close()
    },
  })
}

export function sse(eventos: [string, unknown][]): Response {
  const texto = eventos.map(([evento, datos]) => `event: ${evento}\ndata: ${JSON.stringify(datos)}\n\n`)
  return new Response(flujo(texto), {
    status: 200,
    headers: { 'Content-Type': 'text/event-stream' },
  })
}

type Manejador = (init: RequestInit | undefined, url: string) => Response | Promise<Response>

/**
 * Reemplaza fetch por uno que contesta según "MÉTODO /ruta" (sin la query) o "/ruta".
 * Lo que no está en el mapa contesta 404.
 */
export function simularFetch(rutas: Record<string, Manejador | Response>) {
  const espia = vi.fn(async (entrada: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof entrada === 'string' ? entrada : entrada instanceof URL ? entrada.href : entrada.url
    const ruta = url.replace(/^https?:\/\/[^/]+/, '').split('?')[0]
    const metodo = (init?.method ?? 'GET').toUpperCase()
    const manejador = rutas[`${metodo} ${ruta}`] ?? rutas[ruta]
    if (manejador === undefined) return json({ detalle: 'no encontrado' }, 404)
    if (manejador instanceof Response) return manejador.clone()
    return manejador(init, url)
  })
  vi.stubGlobal('fetch', espia)
  return espia
}

export function llamadasA(espia: ReturnType<typeof simularFetch>, metodoYRuta: string) {
  const [metodo, ruta] = metodoYRuta.split(' ')
  return espia.mock.calls.filter(([entrada, init]) => {
    const url = String(entrada).replace(/^https?:\/\/[^/]+/, '').split('?')[0]
    return url === ruta && (init?.method ?? 'GET').toUpperCase() === metodo
  })
}

export function cuerpoJson(init: RequestInit | undefined): unknown {
  return JSON.parse(String(init?.body ?? 'null'))
}
