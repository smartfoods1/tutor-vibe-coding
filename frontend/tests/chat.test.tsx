import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import Chat from '../src/componentes/Chat.tsx'
import { flujoCortado, json, llamadasA, simularFetch, sse } from './ayudas.ts'

afterEach(() => vi.unstubAllGlobals())

function abrir(props: Partial<React.ComponentProps<typeof Chat>> = {}) {
  const alTope = vi.fn()
  const alAvance = vi.fn()
  render(
    <MemoryRouter>
      <Chat modulo={1} alTope={alTope} alAvance={alAvance} {...props} />
    </MemoryRouter>,
  )
  return { alTope, alAvance }
}

/** Una respuesta SSE que se va escribiendo a mano: sirve para probar qué pasa "en el medio" de un turno. */
function respuestaControlada() {
  const codificador = new TextEncoder()
  let control!: ReadableStreamDefaultController<Uint8Array>
  const respuesta = new Response(
    new ReadableStream<Uint8Array>({
      start(c) {
        control = c
      },
    }),
    { status: 200, headers: { 'Content-Type': 'text/event-stream' } },
  )
  return {
    respuesta,
    evento: (tipo: string, datos: unknown) =>
      control.enqueue(codificador.encode(`event: ${tipo}\ndata: ${JSON.stringify(datos)}\n\n`)),
    cerrar: () => control.close(),
  }
}

describe('Chat', () => {
  it('en una sesión nueva manda un turno vacío y muestra el saludo que va llegando', async () => {
    const espia = simularFetch({
      'POST /api/modulos/1/sesion': json({ id: 5, retomada: false }),
      'POST /api/sesiones/5/turno': () =>
        sse([
          ['pensando', {}],
          ['texto', { delta: 'Hola, soy el tutor ' }],
          ['texto', { delta: 'del curso.' }],
          ['fin', { stop_reason: 'end_turn' }],
        ]),
    })
    abrir()
    expect(await screen.findByText('Hola, soy el tutor del curso.')).toBeInTheDocument()
    const [turno] = llamadasA(espia, 'POST /api/sesiones/5/turno')
    expect((turno[1]?.body as FormData).get('texto')).toBe('')
  })

  it('si la sesión se retoma muestra los mensajes guardados sin pedir otro saludo', async () => {
    const espia = simularFetch({
      'POST /api/modulos/1/sesion': json({ id: 8, retomada: true }),
      'GET /api/sesiones/8': json({
        id: 8,
        modulo: 1,
        mensajes: [
          { rol: 'tutor', texto: '¿Qué te trajo hasta acá?' },
          { rol: 'alumno', texto: 'Quiero hacer una página para mi taller.' },
        ],
      }),
    })
    abrir()
    expect(await screen.findByText('¿Qué te trajo hasta acá?')).toBeInTheDocument()
    expect(screen.getByText('Quiero hacer una página para mi taller.')).toBeInTheDocument()
    expect(llamadasA(espia, 'POST /api/sesiones/8/turno')).toHaveLength(0)
  })

  it('manda lo que escribe la persona y muestra la respuesta', async () => {
    const espia = simularFetch({
      'POST /api/modulos/1/sesion': json({ id: 8, retomada: true }),
      'GET /api/sesiones/8': json({ id: 8, modulo: 1, mensajes: [{ rol: 'tutor', texto: 'Hola.' }] }),
      'POST /api/sesiones/8/turno': () =>
        sse([
          ['texto', { delta: 'Qué lindo.' }],
          ['fin', { stop_reason: 'end_turn' }],
        ]),
    })
    abrir()
    await screen.findByText('Hola.')
    fireEvent.change(screen.getByLabelText(/tu mensaje/i), { target: { value: 'Una agenda de sueños' } })
    fireEvent.click(screen.getByRole('button', { name: /^enviar$/i }))
    expect(await screen.findByText('Una agenda de sueños')).toBeInTheDocument()
    expect(await screen.findByText('Qué lindo.')).toBeInTheDocument()
    const [turno] = llamadasA(espia, 'POST /api/sesiones/8/turno')
    expect((turno[1]?.body as FormData).get('texto')).toBe('Una agenda de sueños')
    expect(screen.getByLabelText(/tu mensaje/i)).toHaveValue('')
  })

  it('si el error llega por el stream, Reintentar sigue desde el mensaje guardado (texto vacío)', async () => {
    let vez = 0
    const espia = simularFetch({
      'POST /api/modulos/1/sesion': json({ id: 5, retomada: true }),
      'GET /api/sesiones/5': () =>
        json({
          id: 5,
          modulo: 1,
          mensajes: [
            { rol: 'tutor', texto: 'Hola.' },
            ...(vez > 0 ? [{ rol: 'alumno', texto: 'Una agenda de sueños' }] : []),
          ],
          pendiente: vez > 0,
        }),
      'POST /api/sesiones/5/turno': () => {
        vez += 1
        if (vez === 1) {
          return sse([
            ['texto', { delta: 'Me quedé a mitad' }],
            ['error', { mensaje: 'El tutor no respondió.', reintentable: true }],
          ])
        }
        return sse([
          ['texto', { delta: 'Ahora sí.' }],
          ['fin', { stop_reason: 'end_turn' }],
        ])
      },
    })
    abrir()
    await screen.findByText('Hola.')
    fireEvent.change(screen.getByLabelText(/tu mensaje/i), { target: { value: 'Una agenda de sueños' } })
    fireEvent.click(screen.getByRole('button', { name: /^enviar$/i }))
    expect(await screen.findByText('El tutor no respondió.')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /reintentar/i }))
    expect(await screen.findByText('Ahora sí.')).toBeInTheDocument()
    const turnos = llamadasA(espia, 'POST /api/sesiones/5/turno')
    expect(turnos).toHaveLength(2)
    expect((turnos[1][1]?.body as FormData).get('texto')).toBe('')
    // El mensaje de la persona no se duplica y lo que quedó a mitad (sin guardar) no queda a la vista.
    expect(screen.getAllByText('Una agenda de sueños')).toHaveLength(1)
    expect(screen.queryByText('Me quedé a mitad')).toBeNull()
    expect(screen.queryByText('El tutor no respondió.')).toBeNull()
  })

  it('si el stream se corta sin "fin" después de un 200, Reintentar manda texto vacío', async () => {
    let vez = 0
    const espia = simularFetch({
      'POST /api/modulos/1/sesion': json({ id: 5, retomada: true }),
      'GET /api/sesiones/5': () =>
        json({
          id: 5,
          modulo: 1,
          mensajes: [{ rol: 'tutor', texto: 'Hola.' }, ...(vez > 0 ? [{ rol: 'alumno', texto: 'Hola, tutor' }] : [])],
          pendiente: vez > 0,
        }),
      'POST /api/sesiones/5/turno': () => {
        vez += 1
        if (vez === 1) return sse([['texto', { delta: 'Primero' }]])
        return sse([
          ['texto', { delta: 'Sigo desde acá.' }],
          ['fin', { stop_reason: 'end_turn' }],
        ])
      },
    })
    abrir()
    await screen.findByText('Hola.')
    fireEvent.change(screen.getByLabelText(/tu mensaje/i), { target: { value: 'Hola, tutor' } })
    fireEvent.click(screen.getByRole('button', { name: /^enviar$/i }))
    expect(await screen.findByText(/se cortó la respuesta/i)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /reintentar/i }))
    expect(await screen.findByText('Sigo desde acá.')).toBeInTheDocument()
    const turnos = llamadasA(espia, 'POST /api/sesiones/5/turno')
    expect(turnos).toHaveLength(2)
    expect((turnos[1][1]?.body as FormData).get('texto')).toBe('')
  })

  it('si la conexión se cae a mitad del stream, también sigue desde el mensaje guardado', async () => {
    let vez = 0
    const espia = simularFetch({
      'POST /api/modulos/1/sesion': json({ id: 5, retomada: true }),
      'GET /api/sesiones/5': () =>
        json({
          id: 5,
          modulo: 1,
          mensajes: [{ rol: 'tutor', texto: 'Hola.' }, ...(vez > 0 ? [{ rol: 'alumno', texto: 'Hola, tutor' }] : [])],
          pendiente: vez > 0,
        }),
      'POST /api/sesiones/5/turno': () => {
        vez += 1
        if (vez === 1) {
          const cuerpo = flujoCortado(['event: texto\ndata: {"delta":"Empie"}\n\n'])
          return new Response(cuerpo, { status: 200, headers: { 'Content-Type': 'text/event-stream' } })
        }
        return sse([
          ['texto', { delta: 'Ahora completo.' }],
          ['fin', { stop_reason: 'end_turn' }],
        ])
      },
    })
    abrir()
    await screen.findByText('Hola.')
    fireEvent.change(screen.getByLabelText(/tu mensaje/i), { target: { value: 'Hola, tutor' } })
    fireEvent.click(screen.getByRole('button', { name: /^enviar$/i }))
    expect(await screen.findByText(/se cortó la respuesta/i)).toBeInTheDocument()
    expect(screen.getByText('Empie')).toBeInTheDocument()
    expect(screen.queryByText(/network error/i)).toBeNull()
    fireEvent.click(screen.getByRole('button', { name: /reintentar/i }))
    expect(await screen.findByText('Ahora completo.')).toBeInTheDocument()
    expect((llamadasA(espia, 'POST /api/sesiones/5/turno')[1][1]?.body as FormData).get('texto')).toBe('')
  })

  it('si el pedido nunca llegó (sin conexión), Reintentar reenvía lo mismo', async () => {
    let vez = 0
    const espia = simularFetch({
      'POST /api/modulos/1/sesion': json({ id: 5, retomada: true }),
      'GET /api/sesiones/5': json({ id: 5, modulo: 1, mensajes: [{ rol: 'tutor', texto: 'Hola.' }] }),
      'POST /api/sesiones/5/turno': () => {
        vez += 1
        if (vez === 1) return Promise.reject(new TypeError('Failed to fetch'))
        return sse([
          ['texto', { delta: 'Te leí.' }],
          ['fin', { stop_reason: 'end_turn' }],
        ])
      },
    })
    abrir()
    await screen.findByText('Hola.')
    fireEvent.change(screen.getByLabelText(/tu mensaje/i), { target: { value: 'Mi idea es un mate' } })
    fireEvent.click(screen.getByRole('button', { name: /^enviar$/i }))
    expect(await screen.findByText(/no hay conexión/i)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /reintentar/i }))
    expect(await screen.findByText('Te leí.')).toBeInTheDocument()
    const turnos = llamadasA(espia, 'POST /api/sesiones/5/turno')
    expect(turnos).toHaveLength(2)
    expect((turnos[1][1]?.body as FormData).get('texto')).toBe('Mi idea es un mate')
    expect(screen.getAllByText('Mi idea es un mate')).toHaveLength(1)
  })

  it('si el servidor respondió con un error antes del stream, Reintentar reenvía lo mismo', async () => {
    let vez = 0
    const espia = simularFetch({
      'POST /api/modulos/1/sesion': json({ id: 5, retomada: true }),
      'GET /api/sesiones/5': json({ id: 5, modulo: 1, mensajes: [{ rol: 'tutor', texto: 'Hola.' }] }),
      'POST /api/sesiones/5/turno': () => {
        vez += 1
        if (vez === 1) return json({ detalle: 'Algo falló de nuestro lado.' }, 503)
        return sse([
          ['texto', { delta: 'Listo.' }],
          ['fin', { stop_reason: 'end_turn' }],
        ])
      },
    })
    abrir()
    await screen.findByText('Hola.')
    fireEvent.change(screen.getByLabelText(/tu mensaje/i), { target: { value: 'Otra vez' } })
    fireEvent.click(screen.getByRole('button', { name: /^enviar$/i }))
    expect(await screen.findByText('Algo falló de nuestro lado.')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /reintentar/i }))
    expect(await screen.findByText('Listo.')).toBeInTheDocument()
    expect((llamadasA(espia, 'POST /api/sesiones/5/turno')[1][1]?.body as FormData).get('texto')).toBe('Otra vez')
    expect(llamadasA(espia, 'GET /api/sesiones/5')).toHaveLength(1)
  })

  it('el texto que llega después de una herramienta va en un párrafo aparte', async () => {
    simularFetch({
      'POST /api/modulos/1/sesion': json({ id: 5, retomada: false }),
      'POST /api/sesiones/5/turno': () =>
        sse([
          ['texto', { delta: 'Lo marco como completo.' }],
          ['herramienta', { nombre: 'marcar_avance', estado: 'inicio', error: false }],
          ['herramienta', { nombre: 'marcar_avance', estado: 'fin', error: false }],
          ['avance', { modulo_completado: 1, modulo_actual: 2 }],
          ['texto', { delta: 'Listo, el módulo 1 ' }],
          ['texto', { delta: 'quedó completo.' }],
          ['fin', { stop_reason: 'end_turn' }],
        ]),
    })
    abrir()
    expect(await screen.findByText('Listo, el módulo 1 quedó completo.')).toBeInTheDocument()
    expect(screen.getByText('Lo marco como completo.')).toBeInTheDocument()
    expect(screen.queryByText(/completo\.Listo/)).toBeNull()
  })

  it('si la herramienta va antes de todo texto, el mensaje arranca sin separación y sigue de corrido', async () => {
    simularFetch({
      'POST /api/modulos/1/sesion': json({ id: 5, retomada: false }),
      'POST /api/sesiones/5/turno': () =>
        sse([
          ['herramienta', { nombre: 'consultar_machete', estado: 'inicio', error: false }],
          ['herramienta', { nombre: 'consultar_machete', estado: 'fin', error: false }],
          ['texto', { delta: 'Netlify sigue ' }],
          ['texto', { delta: 'siendo gratis.' }],
          ['fin', { stop_reason: 'end_turn' }],
        ]),
    })
    abrir()
    expect(await screen.findByText('Netlify sigue siendo gratis.')).toBeInTheDocument()
  })

  it('cuando el tutor registra el taller avisa para recargar los datos', async () => {
    simularFetch({
      'POST /api/modulos/3/sesion': json({ id: 5, retomada: false }),
      'POST /api/sesiones/5/turno': () =>
        sse([
          ['texto', { delta: 'Anotado: Codex en Mac.' }],
          ['taller', { herramienta: 'codex', sistema: 'mac' }],
          ['fin', { stop_reason: 'end_turn' }],
        ]),
    })
    const alTaller = vi.fn()
    abrir({ modulo: 3, alTaller })
    await screen.findByText('Anotado: Codex en Mac.')
    await waitFor(() => expect(alTaller).toHaveBeenCalledWith({ herramienta: 'codex', sistema: 'mac' }))
  })

  it('al terminar el módulo 3 sin el kit, el aviso lleva a la sección del kit', async () => {
    simularFetch({
      'POST /api/modulos/3/sesion': json({ id: 5, retomada: false }),
      'POST /api/sesiones/5/turno': () =>
        sse([
          ['texto', { delta: 'Ya quedó instalado.' }],
          ['avance', { modulo_completado: 3, modulo_actual: 3 }],
          ['fin', { stop_reason: 'end_turn' }],
        ]),
    })
    abrir({ modulo: 3 })
    expect(await screen.findByText(/terminaste el módulo 3/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /bajar tu kit/i })).toHaveAttribute('href', '#kit')
    expect(screen.queryByRole('link', { name: /volver al inicio/i })).toBeNull()
  })

  it('al terminar el módulo 3 con el kit ya bajado, el aviso lleva a cómo seguir en la computadora', async () => {
    simularFetch({
      'POST /api/modulos/3/sesion': json({ id: 5, retomada: false }),
      'POST /api/sesiones/5/turno': () =>
        sse([
          ['texto', { delta: 'Ya quedó instalado.' }],
          ['avance', { modulo_completado: 3, modulo_actual: 4 }],
          ['fin', { stop_reason: 'end_turn' }],
        ]),
    })
    abrir({ modulo: 3 })
    expect(await screen.findByText(/terminaste el módulo 3/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /cómo seguir en tu computadora/i })).toHaveAttribute('href', '/seguir')
  })

  it('al terminar el módulo 3 sin el kit no manda todavía a los pasos: primero hay que bajarlo', async () => {
    simularFetch({
      'POST /api/modulos/3/sesion': json({ id: 5, retomada: false }),
      'POST /api/sesiones/5/turno': () =>
        sse([
          ['texto', { delta: 'Ya quedó instalado.' }],
          ['avance', { modulo_completado: 3, modulo_actual: 3 }],
          ['fin', { stop_reason: 'end_turn' }],
        ]),
    })
    abrir({ modulo: 3 })
    expect(await screen.findByRole('link', { name: /bajar tu kit/i })).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /cómo seguir en tu computadora/i })).toBeNull()
  })

  it('avisa cuando se guarda la idea y cuando termina el módulo', async () => {
    simularFetch({
      'POST /api/modulos/2/sesion': json({ id: 5, retomada: false }),
      'POST /api/sesiones/5/turno': () =>
        sse([
          ['texto', { delta: 'Listo, la guardé.' }],
          ['idea', { version: 3 }],
          ['avance', { modulo_completado: 2, modulo_actual: 3 }],
          ['fin', { stop_reason: 'end_turn' }],
        ]),
    })
    const { alAvance } = abrir({ modulo: 2 })
    expect(await screen.findByText(/tu idea quedó guardada/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /editarla o bajarla en mi idea/i })).toHaveAttribute('href', '/mi-idea')
    expect(screen.getByText(/terminaste el módulo 2/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /seguir con el módulo 3/i })).toHaveAttribute('href', '/modulo/3')
    expect(alAvance).toHaveBeenCalledWith(3)
  })

  describe('al guardarse la idea en el módulo 2', () => {
    const IDEA = {
      version: 3,
      texto_md: '# Recetas de la abuela\n\n## Qué es\n\nUna página con cinco recetas.',
      que_sigue_md: '- Un buscador de recetas',
      autor: 'tutor',
      creado: '2026-09-29T12:00:00Z',
    }

    /** El primer turno guarda la idea; los que siguen son solo texto. */
    function conIdeaGuardada(extra: Record<string, () => Response> = {}) {
      let turno = 0
      return simularFetch({
        'POST /api/modulos/2/sesion': json({ id: 5, retomada: false }),
        'POST /api/sesiones/5/turno': () => {
          turno += 1
          return turno === 1
            ? sse([
                ['texto', { delta: 'Listo, la guardé.' }],
                ['idea', { version: 3 }],
                ['fin', { stop_reason: 'end_turn' }],
              ])
            : sse([
                ['texto', { delta: 'Perfecto, seguimos.' }],
                ['fin', { stop_reason: 'end_turn' }],
              ])
        },
        'GET /api/idea': json(IDEA),
        ...extra,
      })
    }

    it('ofrece leerla ahí mismo, dos botones para seguir y el enlace para editarla o bajarla', async () => {
      conIdeaGuardada()
      abrir({ modulo: 2 })
      expect(await screen.findByText(/tu idea quedó guardada/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /leer mi idea acá/i })).toHaveAttribute('aria-expanded', 'false')
      expect(screen.getByRole('button', { name: 'Está bien así' })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Quiero cambiar algo' })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /editarla o bajarla en mi idea/i })).toHaveAttribute('href', '/mi-idea')
    })

    it('trae la idea recién al abrir el desplegable y la muestra dentro del chat, con lo que sigue', async () => {
      const espia = conIdeaGuardada()
      abrir({ modulo: 2 })
      const leer = await screen.findByRole('button', { name: /leer mi idea acá/i })
      expect(llamadasA(espia, 'GET /api/idea')).toHaveLength(0)
      fireEvent.click(leer)
      expect(await screen.findByText(/una página con cinco recetas/i)).toBeInTheDocument()
      expect(screen.getByText(/un buscador de recetas/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /ocultar mi idea/i })).toHaveAttribute('aria-expanded', 'true')
      // Al cerrar y abrir de nuevo no la pide otra vez.
      fireEvent.click(screen.getByRole('button', { name: /ocultar mi idea/i }))
      expect(screen.getByText(/una página con cinco recetas/i)).not.toBeVisible()
      fireEvent.click(screen.getByRole('button', { name: /leer mi idea acá/i }))
      expect(screen.getByText(/una página con cinco recetas/i)).toBeVisible()
      expect(llamadasA(espia, 'GET /api/idea')).toHaveLength(1)
    })

    it('si no se puede traer la idea, lo dice y deja reintentar sin perder los botones', async () => {
      let intentos = 0
      conIdeaGuardada({
        'GET /api/idea': () => {
          intentos += 1
          return intentos === 1 ? json({ detalle: 'Falló' }, 500) : json(IDEA)
        },
      })
      abrir({ modulo: 2 })
      fireEvent.click(await screen.findByRole('button', { name: /leer mi idea acá/i }))
      const alerta = await screen.findByRole('alert')
      expect(alerta).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Está bien así' })).toBeEnabled()
      fireEvent.click(screen.getByRole('button', { name: /reintentar/i }))
      expect(await screen.findByText(/una página con cinco recetas/i)).toBeInTheDocument()
    })

    it('"Está bien así" le manda ese mensaje al tutor, lo muestra como de la persona y guarda el aviso', async () => {
      const espia = conIdeaGuardada()
      abrir({ modulo: 2 })
      fireEvent.click(await screen.findByRole('button', { name: 'Está bien así' }))
      expect(await screen.findByText('Está bien así')).toBeInTheDocument()
      await waitFor(() => expect(llamadasA(espia, 'POST /api/sesiones/5/turno')).toHaveLength(2))
      const turnos = llamadasA(espia, 'POST /api/sesiones/5/turno')
      expect((turnos[1][1]?.body as FormData).get('texto')).toBe('Está bien así')
      expect(await screen.findByText('Perfecto, seguimos.')).toBeInTheDocument()
      // Ya contestó: el bloque con los botones se va (si el tutor guarda otra versión, vuelve solo).
      await waitFor(() => expect(screen.queryByRole('button', { name: 'Quiero cambiar algo' })).toBeNull())
    })

    it('"Quiero cambiar algo" le manda ese mensaje al tutor', async () => {
      const espia = conIdeaGuardada()
      abrir({ modulo: 2 })
      fireEvent.click(await screen.findByRole('button', { name: 'Quiero cambiar algo' }))
      expect(await screen.findByText('Quiero cambiar algo')).toBeInTheDocument()
      await waitFor(() => expect(llamadasA(espia, 'POST /api/sesiones/5/turno')).toHaveLength(2))
      const turnos = llamadasA(espia, 'POST /api/sesiones/5/turno')
      expect((turnos[1][1]?.body as FormData).get('texto')).toBe('Quiero cambiar algo')
    })

    it('los botones quedan deshabilitados mientras el tutor sigue escribiendo y no mandan nada', async () => {
      const turno = respuestaControlada()
      const espia = simularFetch({
        'POST /api/modulos/2/sesion': json({ id: 5, retomada: false }),
        'POST /api/sesiones/5/turno': () => turno.respuesta,
      })
      abrir({ modulo: 2 })
      await waitFor(() => expect(llamadasA(espia, 'POST /api/sesiones/5/turno')).toHaveLength(1))
      await act(async () => {
        turno.evento('texto', { delta: 'Listo, la guardé.' })
        turno.evento('idea', { version: 3 })
      })
      // El cuadro ya está, pero el tutor todavía escribe.
      const boton = await screen.findByRole('button', { name: 'Está bien así' })
      expect(boton).toBeDisabled()
      expect(screen.getByRole('button', { name: 'Quiero cambiar algo' })).toBeDisabled()
      fireEvent.click(boton)
      expect(llamadasA(espia, 'POST /api/sesiones/5/turno')).toHaveLength(1)
      await act(async () => {
        turno.evento('fin', { stop_reason: 'end_turn' })
        turno.cerrar()
      })
      await waitFor(() => expect(screen.getByRole('button', { name: 'Está bien así' })).toBeEnabled())
      expect(screen.getByRole('button', { name: 'Quiero cambiar algo' })).toBeEnabled()
    })

    it('si el tutor guarda otra versión después de un cambio, los botones vuelven', async () => {
      let turno = 0
      simularFetch({
        'POST /api/modulos/2/sesion': json({ id: 5, retomada: false }),
        'POST /api/sesiones/5/turno': () => {
          turno += 1
          return sse([
            ['texto', { delta: turno === 1 ? 'Listo, la guardé.' : 'Cambiada y guardada.' }],
            ['idea', { version: turno === 1 ? 3 : 4 }],
            ['fin', { stop_reason: 'end_turn' }],
          ])
        },
      })
      abrir({ modulo: 2 })
      fireEvent.click(await screen.findByRole('button', { name: 'Quiero cambiar algo' }))
      expect(await screen.findByText('Cambiada y guardada.')).toBeInTheDocument()
      expect(await screen.findByRole('button', { name: 'Está bien así' })).toBeEnabled()
    })

    it('en el módulo 3 sigue el aviso de siempre, sin botones de respuesta', async () => {
      simularFetch({
        'POST /api/modulos/3/sesion': json({ id: 5, retomada: false }),
        'POST /api/sesiones/5/turno': () =>
          sse([
            ['texto', { delta: 'Actualicé tu idea.' }],
            ['idea', { version: 4 }],
            ['fin', { stop_reason: 'end_turn' }],
          ]),
      })
      abrir({ modulo: 3 })
      expect(await screen.findByText(/tu idea quedó guardada/i)).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /ver mi idea/i })).toHaveAttribute('href', '/mi-idea')
      expect(screen.queryByRole('button', { name: 'Está bien así' })).toBeNull()
      expect(screen.queryByRole('button', { name: /leer mi idea acá/i })).toBeNull()
    })
  })

  describe('al volver a un módulo 2 con la idea ya guardada', () => {
    function retomada(opciones: { pendiente?: boolean; ultimoRol?: 'tutor' | 'alumno' } = {}) {
      const { pendiente = false, ultimoRol = 'tutor' } = opciones
      return simularFetch({
        'POST /api/modulos/2/sesion': json({ id: 5, retomada: true }),
        'GET /api/sesiones/5': json({
          id: 5,
          modulo: 2,
          mensajes: [
            { rol: 'alumno', texto: 'Un buscador de becas' },
            { rol: 'tutor', texto: 'Listo, la guardé. Tocá "Está bien así" si te representa.' },
            ...(ultimoRol === 'alumno' ? [{ rol: 'alumno', texto: 'Leí la idea' }] : []),
          ],
          pendiente,
        }),
        'POST /api/sesiones/5/turno': () =>
          sse([
            ['texto', { delta: 'Seguimos.' }],
            ['fin', { stop_reason: 'end_turn' }],
          ]),
      })
    }

    it('vuelve el cuadro con el desplegable y los botones (recargar no deja a la persona sin salida)', async () => {
      retomada()
      abrir({ modulo: 2, ideaAlAbrir: 3 })
      expect(await screen.findByText(/tu idea quedó guardada/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /leer mi idea acá/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Está bien así' })).toBeEnabled()
      expect(screen.getByRole('button', { name: 'Quiero cambiar algo' })).toBeEnabled()
    })

    it('no aparece si todavía no hay idea guardada', async () => {
      retomada()
      abrir({ modulo: 2, ideaAlAbrir: null })
      expect(await screen.findByText(/listo, la guardé/i)).toBeInTheDocument()
      expect(screen.queryByRole('button', { name: 'Está bien así' })).toBeNull()
    })

    it('no aparece si el último mensaje de la persona quedó sin respuesta', async () => {
      const espia = retomada({ pendiente: true, ultimoRol: 'alumno' })
      abrir({ modulo: 2, ideaAlAbrir: 3 })
      expect(await screen.findByText('Seguimos.')).toBeInTheDocument()
      expect(llamadasA(espia, 'POST /api/sesiones/5/turno')).toHaveLength(1)
      expect(screen.queryByRole('button', { name: 'Está bien así' })).toBeNull()
    })

    it('en otro módulo no aparece aunque haya idea guardada', async () => {
      simularFetch({
        'POST /api/modulos/3/sesion': json({ id: 5, retomada: true }),
        'GET /api/sesiones/5': json({ id: 5, modulo: 3, mensajes: [{ rol: 'tutor', texto: 'Seguimos con la instalación.' }] }),
      })
      abrir({ modulo: 3, ideaAlAbrir: 3 })
      expect(await screen.findByText('Seguimos con la instalación.')).toBeInTheDocument()
      expect(screen.queryByText(/tu idea quedó guardada/i)).toBeNull()
    })
  })

  it('cuando aparece el cuadro de la idea, baja hasta él para que los botones no queden atrás de la barra', async () => {
    const original = Element.prototype.scrollIntoView
    const rectOriginal = Element.prototype.getBoundingClientRect
    const bajar = vi.fn()
    Element.prototype.scrollIntoView = bajar
    // El final del chat queda lejos (el cuadro es alto): el "sigo solo si estoy cerca" no alcanza.
    Element.prototype.getBoundingClientRect = () => ({ top: 5000, bottom: 5000, left: 0, right: 0, width: 0, height: 0, x: 0, y: 5000, toJSON: () => ({}) })
    try {
      const turno = respuestaControlada()
      simularFetch({
        'POST /api/modulos/2/sesion': json({ id: 5, retomada: true }),
        'GET /api/sesiones/5': json({
          id: 5,
          modulo: 2,
          mensajes: [
            { rol: 'tutor', texto: 'Primera pregunta.' },
            { rol: 'alumno', texto: 'Mi respuesta.' },
            { rol: 'tutor', texto: 'Segunda pregunta.' },
          ],
        }),
        'POST /api/sesiones/5/turno': () => turno.respuesta,
      })
      abrir({ modulo: 2 })
      await screen.findByText('Segunda pregunta.')
      fireEvent.change(screen.getByLabelText(/tu mensaje/i), { target: { value: 'La última respuesta' } })
      fireEvent.click(screen.getByRole('button', { name: /^enviar$/i }))
      await act(async () => turno.evento('texto', { delta: 'Listo, la guardé.' }))
      await screen.findByText('Listo, la guardé.')
      const antes = bajar.mock.calls.length
      // La herramienta tarda: el cuadro llega en otro pedazo, después del texto.
      await act(async () => turno.evento('idea', { version: 3 }))
      expect(await screen.findByText(/tu idea quedó guardada/i)).toBeInTheDocument()
      await waitFor(() => expect(bajar.mock.calls.length).toBeGreaterThan(antes))
      await act(async () => {
        turno.evento('fin', { stop_reason: 'end_turn' })
        turno.cerrar()
      })
    } finally {
      Element.prototype.scrollIntoView = original
      Element.prototype.getBoundingClientRect = rectOriginal
    }
  })

  describe('la salida del chat', () => {
    it.each([1, 2, 3])('en el módulo %i avisa que la charla queda guardada y ofrece volver al inicio', async (modulo) => {
      simularFetch({
        [`POST /api/modulos/${modulo}/sesion`]: json({ id: 5, retomada: false }),
        'POST /api/sesiones/5/turno': () =>
          sse([
            ['texto', { delta: 'Hola.' }],
            ['fin', { stop_reason: 'end_turn' }],
          ]),
      })
      abrir({ modulo })
      expect(await screen.findByText('Hola.')).toBeInTheDocument()
      expect(screen.getByText(/podés salir cuando quieras: tu conversación queda guardada/i)).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /^volver al inicio$/i })).toHaveAttribute('href', '/inicio')
    })

    it('se ve desde el primer momento, aunque el tutor todavía no haya contestado', () => {
      simularFetch({
        'POST /api/modulos/2/sesion': () => new Promise<Response>(() => {}),
      })
      abrir({ modulo: 2 })
      expect(screen.getByRole('link', { name: /^volver al inicio$/i })).toHaveAttribute('href', '/inicio')
    })

    it('al terminar el módulo no se repite: el aviso de avance ya trae su propio camino', async () => {
      simularFetch({
        'POST /api/modulos/2/sesion': json({ id: 5, retomada: false }),
        'POST /api/sesiones/5/turno': () =>
          sse([
            ['texto', { delta: 'Cerramos.' }],
            ['avance', { modulo_completado: 2, modulo_actual: 3 }],
            ['fin', { stop_reason: 'end_turn' }],
          ]),
      })
      abrir({ modulo: 2 })
      expect(await screen.findByText(/terminaste el módulo 2/i)).toBeInTheDocument()
      expect(screen.queryByText(/podés salir cuando quieras/i)).toBeNull()
      expect(screen.queryByRole('link', { name: /^volver al inicio$/i })).toBeNull()
    })
  })

  it('al llegar al tope avisa para pasar a la guía escrita', async () => {
    simularFetch({
      'POST /api/modulos/1/sesion': json({ id: 5, retomada: false }),
      'POST /api/sesiones/5/turno': () => sse([['tope', { alcance: 'alumno', guia: '/api/modulos/1/guia' }]]),
    })
    const { alTope } = abrir()
    await waitFor(() => expect(alTope).toHaveBeenCalledWith('alumno'))
  })

  it('si al abrir la sesión ya hay tope, avisa sin mandar turnos', async () => {
    const espia = simularFetch({
      'POST /api/modulos/1/sesion': json({ detalle: 'tope', alcance: 'mes', guia: '/api/modulos/1/guia' }, 402),
    })
    const { alTope } = abrir()
    await waitFor(() => expect(alTope).toHaveBeenCalledWith('mes'))
    expect(espia.mock.calls.some(([url]) => String(url).includes('/turno'))).toBe(false)
  })
})
