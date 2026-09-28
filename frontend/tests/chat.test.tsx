import { fireEvent, render, screen, waitFor } from '@testing-library/react'
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
    expect(screen.getByRole('link', { name: /ver mi idea/i })).toHaveAttribute('href', '/mi-idea')
    expect(screen.getByText(/terminaste el módulo 2/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /seguir con el módulo 3/i })).toHaveAttribute('href', '/modulo/3')
    expect(alAvance).toHaveBeenCalledWith(3)
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
