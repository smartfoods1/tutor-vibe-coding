import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from '../src/App.tsx'
import { cuerpoJson, json, llamadasA, simularFetch, sse } from './ayudas.ts'

afterEach(() => vi.unstubAllGlobals())

const CONFIG = { 'GET /api/config': json({ turnstile_site_key: null, aviso_prueba: false }) }

/** La config completa del servidor: autor, newsletter y modo demo. */
function config(extra: Record<string, unknown> = {}) {
  return {
    'GET /api/config': json({
      turnstile_site_key: null,
      aviso_prueba: false,
      autor_nombre: null,
      newsletter: null,
      modo_demo: false,
      ...extra,
    }),
  }
}

const TEXTOS_LEGALES = {
  'GET /api/legal/consentimientos': json({
    version: '2026-09-28',
    textos: {
      mails_curso: 'Acepto recibir los mails del curso.',
      transferencia: 'Acepto que mis datos se procesen con proveedores en Estados Unidos.',
      novedades: 'Quiero recibir las novedades del curso por mail.',
    },
    texto_md: '',
  }),
}

const AUDIO_1 = { modulo: 1, url: '/audios/modulo-1.mp3', transcripcion: null }

/** Hace que el navegador de prueba parezca tener micrófono (jsdom no trae MediaRecorder). */
function conMicrofono() {
  vi.stubGlobal('MediaRecorder', Object.assign(function MediaRecorder() {}, { isTypeSupported: () => true }))
  Object.defineProperty(navigator, 'mediaDevices', {
    configurable: true,
    value: { getUserMedia: vi.fn() },
  })
}

function sinMicrofono() {
  Object.defineProperty(navigator, 'mediaDevices', { configurable: true, value: undefined })
}

const MODULOS_1_Y_2 = [
  { modulo: 1, completado: '2026-09-27T10:00:00+00:00', via: 'tutor' },
  { modulo: 2, completado: '2026-09-28T10:00:00+00:00', via: 'tutor' },
]

function yo(extra: Record<string, unknown> = {}) {
  return json({
    email: 'persona@ejemplo.com',
    modulo_actual: 2,
    avance: [{ modulo: 1, completado: '2026-09-28T10:00:00+00:00', via: 'tutor' }],
    idea: null,
    taller: { herramienta: null, sistema: null },
    tope: { bloqueado: false, alcance: null },
    consentimientos: { mails_curso: true, novedades: false },
    audios: [],
    ...extra,
  })
}

function abrir(ruta: string) {
  render(
    <MemoryRouter initialEntries={[ruta]}>
      <App />
    </MemoryRouter>,
  )
}

describe('Inicio', () => {
  it('muestra los módulos con su estado y destaca el actual', async () => {
    simularFetch({ ...CONFIG, 'GET /api/yo': yo() })
    abrir('/inicio')
    const actual = await screen.findByRole('link', { name: /seguir con el módulo 2/i })
    expect(actual).toHaveAttribute('href', '/modulo/2')
    expect(screen.getByText(/cómo piensa un vibe coder/i)).toBeInTheDocument()
    expect(screen.getAllByText(/terminado/i).length).toBeGreaterThan(0)
    expect(screen.getByText(/primera victoria/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /mi idea/i })).toHaveAttribute('href', '/mi-idea')
    // Mostrar lo que hiciste se abre recién con el kit bajado (módulo 4).
    expect(screen.queryByRole('link', { name: /mostrar lo que hiciste/i })).toBeNull()
    expect(screen.getByRole('link', { name: /mis datos/i })).toHaveAttribute('href', '/mis-datos')
    expect(screen.queryByRole('link', { name: /administrar/i })).toBeNull()
  })

  it('con el kit bajado muestra el acceso a Mostrar y cómo seguir en la herramienta', async () => {
    simularFetch({
      ...CONFIG,
      'GET /api/yo': yo({ modulo_actual: 4, taller: { herramienta: 'codex', sistema: 'mac' } }),
    })
    abrir('/inicio')
    expect(await screen.findByRole('link', { name: /mostrar lo que hiciste/i })).toHaveAttribute('href', '/mostrar')
    expect(screen.getByText(/escribí "sigamos" \(o "empecemos" la primera vez\)/i)).toBeInTheDocument()
  })

  it('a quien administra le muestra el acceso al reporte', async () => {
    simularFetch({ ...CONFIG, 'GET /api/yo': yo({ es_admin: true }) })
    abrir('/inicio')
    expect(await screen.findByRole('link', { name: /administrar/i })).toHaveAttribute('href', '/admin')
  })
})

describe('Modulo', () => {
  it('con el tope alcanzado muestra la guía escrita y "ya lo hice" marca el módulo', async () => {
    const espia = simularFetch({
      ...CONFIG,
      'GET /api/yo': yo({ modulo_actual: 1, avance: [], tope: { bloqueado: true, alcance: 'mes' } }),
      'GET /api/modulos/1/guia': json({ modulo: 1, titulo: 'Cómo piensa un vibe coder', guia_md: 'Primero, **respirá**.' }),
      'POST /api/modulos/1/completar': json({ modulo_actual: 2 }),
    })
    abrir('/modulo/1')
    expect(await screen.findByText(/llegó a su límite de uso este mes/i)).toBeInTheDocument()
    expect(await screen.findByText('respirá')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /ya lo hice/i }))
    expect(await screen.findByText(/terminaste el módulo 1/i)).toBeInTheDocument()
    expect(llamadasA(espia, 'POST /api/modulos/1/completar')).toHaveLength(1)
    expect(llamadasA(espia, 'POST /api/modulos/1/sesion')).toHaveLength(0)
  })

  it('en un módulo terminado no abre el chat (ni gasta el saludo) hasta que la persona lo pide', async () => {
    const espia = simularFetch({
      ...CONFIG,
      'GET /api/yo': yo({ modulo_actual: 3 }),
      'POST /api/modulos/1/sesion': json({ id: 4, retomada: true }),
      'GET /api/sesiones/4': json({ id: 4, modulo: 1, mensajes: [{ rol: 'tutor', texto: 'Hola de nuevo.' }] }),
    })
    abrir('/modulo/1')
    const volver = await screen.findByRole('button', { name: /volver a conversar con el tutor/i })
    expect(llamadasA(espia, 'POST /api/modulos/1/sesion')).toHaveLength(0)
    fireEvent.click(volver)
    expect(await screen.findByText('Hola de nuevo.')).toBeInTheDocument()
    expect(llamadasA(espia, 'POST /api/modulos/1/sesion')).toHaveLength(1)
  })

  it('el audio y la aclaración de la voz nombran al autor configurado', async () => {
    simularFetch({
      ...config({ autor_nombre: 'Ana' }),
      'GET /api/yo': yo({ modulo_actual: 1, avance: [], audios: [AUDIO_1] }),
      'POST /api/modulos/1/sesion': json({ id: 3, retomada: true }),
      'GET /api/sesiones/3': json({ id: 3, modulo: 1, mensajes: [{ rol: 'tutor', texto: 'Hola.' }] }),
    })
    abrir('/modulo/1')
    expect(await screen.findByText('Audio de Ana')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Antes de empezar, escuchá a Ana' })).toBeInTheDocument()
    expect(screen.getByText(/es una voz sintética, no la de Ana/i)).toBeInTheDocument()
    expect(await screen.findByText('Hola.')).toBeInTheDocument()
  })

  it('sin autor configurado, los textos del audio y de la voz son genéricos', async () => {
    simularFetch({
      ...config(),
      'GET /api/yo': yo({ modulo_actual: 1, avance: [], audios: [AUDIO_1] }),
      'POST /api/modulos/1/sesion': json({ id: 3, retomada: true }),
      'GET /api/sesiones/3': json({ id: 3, modulo: 1, mensajes: [{ rol: 'tutor', texto: 'Hola.' }] }),
    })
    abrir('/modulo/1')
    expect(await screen.findByText('Audio del autor')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Antes de empezar, escuchá al autor del curso' })).toBeInTheDocument()
    expect(screen.getByText(/es una voz sintética, no la del autor del curso/i)).toBeInTheDocument()
    await screen.findByText('Hola.')
  })

  it('con la voz disponible ofrece Hablar y Escuchar', async () => {
    conMicrofono()
    try {
      simularFetch({
        ...config(),
        'GET /api/yo': yo({ modulo_actual: 1, avance: [] }),
        'POST /api/modulos/1/sesion': json({ id: 3, retomada: true }),
        'GET /api/sesiones/3': json({ id: 3, modulo: 1, mensajes: [{ rol: 'tutor', texto: 'Hola.' }] }),
      })
      abrir('/modulo/1')
      await screen.findByText('Hola.')
      expect(screen.getByRole('button', { name: /escuchar/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /hablar/i })).toBeInTheDocument()
      expect(screen.queryByText(/modo demo/i)).toBeNull()
    } finally {
      sinMicrofono()
    }
  })

  it('en modo demo avisa que el tutor sigue un guion y no ofrece la voz', async () => {
    conMicrofono()
    try {
      simularFetch({
        ...config({ modo_demo: true }),
        'GET /api/yo': yo({ modulo_actual: 1, avance: [] }),
        'POST /api/modulos/1/sesion': json({ id: 3, retomada: true }),
        'GET /api/sesiones/3': json({ id: 3, modulo: 1, mensajes: [{ rol: 'tutor', texto: 'Hola.' }] }),
      })
      abrir('/modulo/1')
      expect(
        await screen.findByText('Modo demo: el tutor responde con un guion de ejemplo, sin IA'),
      ).toBeInTheDocument()
      await screen.findByText('Hola.')
      expect(screen.queryByRole('button', { name: /escuchar/i })).toBeNull()
      expect(screen.queryByRole('button', { name: /hablar/i })).toBeNull()
      expect(screen.queryByText(/voz sintética/i)).toBeNull()
      expect(screen.getByLabelText(/tu mensaje/i)).not.toHaveAttribute('placeholder', expect.stringMatching(/hablar/i))
    } finally {
      sinMicrofono()
    }
  })

  it('un módulo que todavía no se abrió lo explica', async () => {
    simularFetch({ ...CONFIG, 'GET /api/yo': yo({ modulo_actual: 1, avance: [] }) })
    abrir('/modulo/3')
    expect(await screen.findByText(/se abre cuando termines/i)).toBeInTheDocument()
  })

  it('en el módulo 3, bajar el kit a mitad del módulo no esconde el chat ni el "Ya lo hice"', async () => {
    let kitBajado = false
    const espia = simularFetch({
      ...CONFIG,
      'GET /api/yo': () =>
        yo({
          modulo_actual: kitBajado ? 4 : 3,
          avance: MODULOS_1_Y_2,
          idea: { version: 1, actualizada: '2026-09-28T10:00:00+00:00' },
          taller: { herramienta: 'codex', sistema: 'mac' },
        }),
      'POST /api/modulos/3/sesion': json({ id: 9, retomada: false }),
      'POST /api/sesiones/9/turno': () =>
        sse([
          ['texto', { delta: 'Vamos a instalar Codex.' }],
          ['fin', { stop_reason: 'end_turn' }],
        ]),
      'GET /api/kit': () => {
        kitBajado = true
        return new Response('zip', {
          headers: { 'Content-Type': 'application/zip', 'Content-Disposition': 'attachment; filename="mi-proyecto.zip"' },
        })
      },
      'GET /api/modulos/3/guia': json({ modulo: 3, titulo: 'Tu taller', guia_md: 'Pasos.' }),
    })
    vi.stubGlobal('URL', Object.assign(URL, { createObjectURL: vi.fn(() => 'blob:x'), revokeObjectURL: vi.fn() }))
    const clic = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined)
    try {
      abrir('/modulo/3')
      expect(await screen.findByText('Vamos a instalar Codex.')).toBeInTheDocument()
      fireEvent.click(screen.getByRole('button', { name: /bajar mi kit/i }))
      expect(await screen.findByText(/listo, bajaste mi-proyecto.zip/i)).toBeInTheDocument()
      await waitFor(() => expect(llamadasA(espia, 'GET /api/yo')).toHaveLength(2))
      await act(() => new Promise((listo) => setTimeout(listo, 30)))

      expect(screen.getByLabelText(/tu mensaje/i)).toBeInTheDocument()
      expect(screen.getByText('Vamos a instalar Codex.')).toBeInTheDocument()
      expect(screen.queryByText(/ya terminaste este módulo/i)).toBeNull()
      fireEvent.click(screen.getByRole('button', { name: /prefiero leer la guía escrita/i }))
      expect(await screen.findByRole('button', { name: /ya lo hice/i })).toBeInTheDocument()
    } finally {
      clic.mockRestore()
    }
  })

  it('el módulo 3 queda terminado por el avance, no por el módulo actual, y el aviso lleva al kit', async () => {
    const espia = simularFetch({
      ...CONFIG,
      'GET /api/yo': yo({
        modulo_actual: 3,
        avance: [...MODULOS_1_Y_2, { modulo: 3, completado: '2026-09-28T12:00:00+00:00', via: 'tutor' }],
        taller: { herramienta: 'claude', sistema: 'windows' },
      }),
    })
    abrir('/modulo/3')
    expect(await screen.findByText(/ya terminaste este módulo/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /volver a conversar con el tutor/i })).toBeInTheDocument()
    expect(llamadasA(espia, 'POST /api/modulos/3/sesion')).toHaveLength(0)
    expect(screen.getByRole('link', { name: /bajar tu kit/i })).toHaveAttribute('href', '#kit')
    expect(document.getElementById('kit')).not.toBeNull()
  })

  it('cuando el tutor registra el taller, la sección del kit se actualiza sola', async () => {
    let registrado = false
    simularFetch({
      ...CONFIG,
      'GET /api/yo': () =>
        yo({
          modulo_actual: 3,
          avance: MODULOS_1_Y_2,
          taller: registrado ? { herramienta: 'claude', sistema: 'mac' } : { herramienta: null, sistema: null },
        }),
      'POST /api/modulos/3/sesion': json({ id: 9, retomada: false }),
      'POST /api/sesiones/9/turno': () => {
        registrado = true
        return sse([
          ['texto', { delta: 'Anoto Claude en tu Mac.' }],
          ['taller', { herramienta: 'claude', sistema: 'mac' }],
          ['fin', { stop_reason: 'end_turn' }],
        ])
      },
    })
    abrir('/modulo/3')
    await screen.findByText('Anoto Claude en tu Mac.')
    expect(await screen.findByRole('button', { name: /bajar mi kit/i })).toBeInTheDocument()
    expect(screen.getByRole('radio', { name: /claude code/i })).toBeChecked()
    expect(screen.getByRole('radio', { name: /^mac$/i })).toBeChecked()
  })

  it('el taller explica qué herramienta conviene sin prometer que algo no se paga', async () => {
    simularFetch({
      ...CONFIG,
      'GET /api/yo': yo({ modulo_actual: 3, tope: { bloqueado: true, alcance: 'alumno' } }),
      'GET /api/modulos/3/guia': json({ modulo: 3, titulo: 'Tu taller', guia_md: 'Pasos.' }),
    })
    abrir('/modulo/3')
    expect(await screen.findByText('Si tenés Claude Pro (se paga).')).toBeInTheDocument()
    expect(screen.getByText('Si usás ChatGPT, con o sin pago, o no usás ninguna.')).toBeInTheDocument()
    expect(screen.queryByText(/gratis/i)).toBeNull()
  })

  it('al elegir otra computadora muestra lo que responde el servidor y no ofrece el kit', async () => {
    let elegido = false
    const espia = simularFetch({
      ...CONFIG,
      'GET /api/yo': () =>
        yo({
          modulo_actual: 3,
          tope: { bloqueado: true, alcance: 'alumno' },
          taller: elegido ? { herramienta: 'codex', sistema: 'otro' } : { herramienta: null, sistema: null },
        }),
      'GET /api/modulos/3/guia': json({ modulo: 3, titulo: 'Tu taller', guia_md: 'Pasos.' }),
      'PUT /api/taller': () => {
        elegido = true
        return json({ ok: true, mensaje: 'Para el kit hace falta una Mac o una Windows.' })
      },
    })
    abrir('/modulo/3')
    fireEvent.click(await screen.findByRole('radio', { name: /codex/i }))
    fireEvent.click(screen.getByRole('radio', { name: /otra/i }))
    fireEvent.click(screen.getByRole('button', { name: /guardar mi elección/i }))
    expect(await screen.findByText('Para el kit hace falta una Mac o una Windows.')).toBeInTheDocument()
    await waitFor(() => expect(llamadasA(espia, 'GET /api/yo')).toHaveLength(2))
    await act(() => new Promise((listo) => setTimeout(listo, 30)))
    expect(screen.getByText('Para el kit hace falta una Mac o una Windows.')).toBeInTheDocument()
    expect(screen.getByRole('radio', { name: /otra/i })).toBeChecked()
    expect(screen.queryByRole('button', { name: /bajar mi kit/i })).toBeNull()
  })

  it('el módulo 3 deja elegir herramienta y sistema y bajar el kit', async () => {
    const espia = simularFetch({
      ...CONFIG,
      'GET /api/yo': yo({ modulo_actual: 3, tope: { bloqueado: true, alcance: 'alumno' } }),
      'GET /api/modulos/3/guia': json({ modulo: 3, titulo: 'Tu taller', guia_md: 'Pasos.' }),
      'PUT /api/taller': json({ ok: true }),
      'GET /api/kit': json({ detalle: 'Falta guardar tu idea.' }, 409),
    })
    abrir('/modulo/3')
    fireEvent.click(await screen.findByRole('radio', { name: /codex/i }))
    fireEvent.click(screen.getByRole('radio', { name: /windows/i }))
    fireEvent.click(screen.getByRole('button', { name: /guardar mi elección/i }))
    await waitFor(() => expect(llamadasA(espia, 'PUT /api/taller')).toHaveLength(1))
    expect(cuerpoJson(llamadasA(espia, 'PUT /api/taller')[0][1])).toEqual({ herramienta: 'codex', sistema: 'windows' })
    fireEvent.click(await screen.findByRole('button', { name: /bajar mi kit/i }))
    expect(await screen.findByText('Falta guardar tu idea.')).toBeInTheDocument()
  })
})

describe('Mostrar', () => {
  it('antes de bajar el kit avisa que primero hay que bajarlo', async () => {
    const espia = simularFetch({ ...CONFIG, 'GET /api/yo': yo({ modulo_actual: 3 }) })
    abrir('/mostrar')
    expect(await screen.findByText(/primero tenés que bajar tu kit/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /ir al módulo 3/i })).toHaveAttribute('href', '/modulo/3')
    expect(screen.queryByLabelText(/el link de tu página/i)).toBeNull()
    expect(llamadasA(espia, 'POST /api/links')).toHaveLength(0)
  })

  it('si no le vamos a mandar mail, la confirmación no lo menciona', async () => {
    simularFetch({
      ...CONFIG,
      'GET /api/yo': yo({ modulo_actual: 5 }),
      'POST /api/links': json({ id: 8, mail: false }, 201),
    })
    abrir('/mostrar')
    fireEvent.change(await screen.findByLabelText(/el link de tu página/i), {
      target: { value: 'https://otra.netlify.app' },
    })
    fireEvent.click(screen.getByRole('button', { name: /registrar mi link/i }))
    const confirmacion = await screen.findByRole('status')
    expect(confirmacion).toHaveTextContent(/tu link quedó registrado/i)
    expect(confirmacion).not.toHaveTextContent(/mail/i)
  })

  it('la opción de uso como contenido nombra al autor, o al curso si no hay', async () => {
    simularFetch({ ...config({ autor_nombre: 'Ana' }), 'GET /api/yo': yo({ modulo_actual: 4 }) })
    const { unmount } = render(
      <MemoryRouter initialEntries={['/mostrar']}>
        <App />
      </MemoryRouter>,
    )
    expect(
      await screen.findByRole('checkbox', {
        name: 'Ana lo puede usar como contenido, por ejemplo para mostrarlo en sus redes.',
      }),
    ).toBeInTheDocument()
    unmount()

    simularFetch({ ...config(), 'GET /api/yo': yo({ modulo_actual: 4 }) })
    abrir('/mostrar')
    expect(
      await screen.findByRole('checkbox', {
        name: 'El curso lo puede usar como contenido, por ejemplo para mostrarlo en sus redes.',
      }),
    ).toBeInTheDocument()
  })

  it('las dos opciones vienen desmarcadas y exige https', async () => {
    const espia = simularFetch({
      ...CONFIG,
      'GET /api/yo': yo({ modulo_actual: 4 }),
      'POST /api/links': json({ id: 7, mail: true }, 201),
    })
    abrir('/mostrar')
    const galeria = await screen.findByRole('checkbox', { name: /galería/i })
    const contenido = screen.getByRole('checkbox', { name: /contenido/i })
    expect(galeria).not.toBeChecked()
    expect(contenido).not.toBeChecked()

    fireEvent.change(screen.getByLabelText(/el link de tu página/i), { target: { value: 'http://mi-idea.com' } })
    fireEvent.click(screen.getByRole('button', { name: /registrar mi link/i }))
    expect(await screen.findByText(/https:\/\//i)).toBeInTheDocument()
    expect(llamadasA(espia, 'POST /api/links')).toHaveLength(0)

    fireEvent.change(screen.getByLabelText(/el link de tu página/i), { target: { value: 'mi-idea.netlify.app' } })
    fireEvent.click(galeria)
    fireEvent.click(screen.getByRole('button', { name: /registrar mi link/i }))
    expect(await screen.findByText(/tu link quedó registrado/i)).toBeInTheDocument()
    expect(
      screen.getByText('Te mandamos un mail con tu link, para que lo tengas a mano y se lo puedas mandar a alguien.'),
    ).toBeInTheDocument()
    expect(cuerpoJson(llamadasA(espia, 'POST /api/links')[0][1])).toEqual({
      url: 'https://mi-idea.netlify.app',
      titulo: null,
      mostrar_galeria: true,
      uso_contenido: false,
    })
  })
})

describe('MisDatos', () => {
  it('borrar todo pide escribir BORRAR', async () => {
    const espia = simularFetch({
      ...CONFIG,
      'GET /api/yo': yo(),
      'DELETE /api/mis-datos': json({ ok: true }),
      'GET /api/legal/consentimientos': json({ version: 'x', textos: {}, texto_md: '' }),
    })
    abrir('/mis-datos')
    const boton = await screen.findByRole('button', { name: /borrar todos mis datos/i })
    expect(boton).toBeDisabled()
    fireEvent.change(screen.getByLabelText(/escribí BORRAR/i), { target: { value: 'borrar' } })
    expect(boton).toBeDisabled()
    fireEvent.change(screen.getByLabelText(/escribí BORRAR/i), { target: { value: 'BORRAR' } })
    fireEvent.click(boton)
    await waitFor(() => expect(llamadasA(espia, 'DELETE /api/mis-datos')).toHaveLength(1))
    expect(cuerpoJson(llamadasA(espia, 'DELETE /api/mis-datos')[0][1])).toEqual({ confirmar: 'BORRAR' })
    expect(await screen.findByText(/borramos todos tus datos/i)).toBeInTheDocument()
  })

  it('lista mis links, deja cambiar sus permisos y borrarlos con confirmación', async () => {
    const espia = simularFetch({
      ...CONFIG,
      'GET /api/yo': yo({ modulo_actual: 7 }),
      'GET /api/links': json([
        {
          id: 7,
          url: 'https://suenos.netlify.app',
          titulo: 'Registro de sueños',
          mostrar_galeria: false,
          uso_contenido: false,
          aprobado: false,
          creado: '2026-09-28T10:00:00+00:00',
        },
        {
          id: 9,
          url: 'https://mate.netlify.app',
          titulo: null,
          mostrar_galeria: true,
          uso_contenido: true,
          aprobado: true,
          creado: '2026-09-28T11:00:00+00:00',
        },
      ]),
      'PATCH /api/links/7': (init) => {
        const cambios = cuerpoJson(init) as Record<string, boolean>
        return json({
          id: 7,
          url: 'https://suenos.netlify.app',
          titulo: 'Registro de sueños',
          mostrar_galeria: false,
          uso_contenido: false,
          aprobado: false,
          creado: '2026-09-28T10:00:00+00:00',
          ...cambios,
        })
      },
      'DELETE /api/links/9': json({ ok: true }),
    })
    abrir('/mis-datos')
    const lista = await screen.findByRole('list', { name: /tus links/i })
    expect(screen.getByText(/recién cuando lo aprueba el curso/i)).toBeInTheDocument()
    const [primero, segundo] = within(lista).getAllByRole('listitem')
    expect(within(primero).getByText('Registro de sueños')).toBeInTheDocument()
    expect(within(segundo).getByText(/se ve en la galería/i)).toBeInTheDocument()

    fireEvent.click(within(primero).getByRole('checkbox', { name: /galería/i }))
    await waitFor(() => expect(llamadasA(espia, 'PATCH /api/links/7')).toHaveLength(1))
    expect(cuerpoJson(llamadasA(espia, 'PATCH /api/links/7')[0][1])).toEqual({ mostrar_galeria: true })
    expect(await within(primero).findByText(/espera que el curso lo apruebe/i)).toBeInTheDocument()

    fireEvent.click(within(primero).getByRole('checkbox', { name: /contenido/i }))
    await waitFor(() => expect(llamadasA(espia, 'PATCH /api/links/7')).toHaveLength(2))
    expect(cuerpoJson(llamadasA(espia, 'PATCH /api/links/7')[1][1])).toEqual({ uso_contenido: true })

    fireEvent.click(within(segundo).getByRole('button', { name: /borrar este link/i }))
    expect(llamadasA(espia, 'DELETE /api/links/9')).toHaveLength(0)
    fireEvent.click(within(segundo).getByRole('button', { name: /sí, borrarlo/i }))
    await waitFor(() => expect(llamadasA(espia, 'DELETE /api/links/9')).toHaveLength(1))
    await waitFor(() => expect(screen.queryByText('https://mate.netlify.app')).toBeNull())
    expect(screen.getByText('Registro de sueños')).toBeInTheDocument()
  })

  it('deja volver a recibir los mails y cambiar las novedades, con el texto legal vigente', async () => {
    const espia = simularFetch({
      ...config({ newsletter: 'Boletín del curso' }),
      ...TEXTOS_LEGALES,
      'GET /api/yo': yo({ consentimientos: { mails_curso: false, novedades: false } }),
      'PUT /api/consentimientos': json({ ok: true }),
    })
    abrir('/mis-datos')
    fireEvent.click(await screen.findByRole('button', { name: /volver a recibir los mails/i }))
    await waitFor(() => expect(llamadasA(espia, 'PUT /api/consentimientos')).toHaveLength(1))
    expect(cuerpoJson(llamadasA(espia, 'PUT /api/consentimientos')[0][1])).toEqual({ mails_curso: true })

    const novedades = await screen.findByRole('checkbox', { name: 'Quiero recibir las novedades del curso por mail.' })
    expect(novedades).not.toBeChecked()
    fireEvent.click(novedades)
    await waitFor(() => expect(llamadasA(espia, 'PUT /api/consentimientos')).toHaveLength(2))
    expect(cuerpoJson(llamadasA(espia, 'PUT /api/consentimientos')[1][1])).toEqual({ novedades: true })
  })

  it('sin newsletter configurado no muestra la casilla de novedades', async () => {
    const espia = simularFetch({
      ...config(),
      ...TEXTOS_LEGALES,
      'GET /api/yo': yo(),
      'GET /api/links': json([]),
    })
    abrir('/mis-datos')
    await screen.findByText(/todavía no registraste ningún link/i)
    expect(screen.queryByRole('checkbox', { name: /novedades/i })).toBeNull()
    expect(llamadasA(espia, 'GET /api/legal/consentimientos')).toHaveLength(0)
  })

  it('en mis links, la opción de contenido nombra al autor configurado', async () => {
    simularFetch({
      ...config({ autor_nombre: 'Ana' }),
      'GET /api/yo': yo({ modulo_actual: 7 }),
      'GET /api/links': json([
        {
          id: 7,
          url: 'https://suenos.netlify.app',
          titulo: 'Registro de sueños',
          mostrar_galeria: false,
          uso_contenido: false,
          aprobado: false,
          creado: '2026-09-28T10:00:00+00:00',
        },
      ]),
    })
    abrir('/mis-datos')
    const lista = await screen.findByRole('list', { name: /tus links/i })
    expect(
      within(lista).getByRole('checkbox', {
        name: 'Ana lo puede usar como contenido, por ejemplo para mostrarlo en sus redes.',
      }),
    ).toBeInTheDocument()
  })
})

describe('Baja', () => {
  it('hace el POST con el token y confirma', async () => {
    const espia = simularFetch({ ...CONFIG, 'POST /api/baja': json({ ok: true }) })
    abrir('/baja?t=abc.def')
    expect(await screen.findByText(/no te vamos a mandar más mails del curso/i)).toBeInTheDocument()
    const llamadas = llamadasA(espia, 'POST /api/baja')
    expect(llamadas).toHaveLength(1)
    expect(String(llamadas[0][0])).toBe('/api/baja?t=abc.def')
  })

  it('con un token inválido muestra el detalle', async () => {
    simularFetch({ ...CONFIG, 'POST /api/baja': json({ detalle: 'El link de baja no es válido.' }, 400) })
    abrir('/baja?t=roto')
    expect(await screen.findByText('El link de baja no es válido.')).toBeInTheDocument()
  })
})

describe('Galeria', () => {
  it('muestra solo links https', async () => {
    simularFetch({
      ...CONFIG,
      'GET /api/galeria': json([
        { titulo: 'Registro de sueños', url: 'https://suenos.netlify.app' },
        { titulo: 'Raro', url: 'javascript:alert(1)' },
      ]),
    })
    abrir('/galeria')
    const lista = await screen.findByRole('list', { name: /páginas de alumnos/i })
    expect(within(lista).getByRole('link', { name: /registro de sueños/i })).toHaveAttribute(
      'href',
      'https://suenos.netlify.app',
    )
    expect(within(lista).queryByText('Raro')).toBeNull()
  })
})

describe('MiIdea', () => {
  it('muestra la idea, deja editarla y guarda una versión nueva', async () => {
    const espia = simularFetch({
      ...CONFIG,
      'GET /api/idea': json({
        version: 2,
        texto_md: '# Registro de sueños\n\nPara mí.',
        que_sigue_md: 'Compartirlo.',
        autor: 'tutor',
        creado: '2026-09-28T10:00:00+00:00',
      }),
      'PUT /api/idea': json({ version: 3 }),
    })
    abrir('/mi-idea')
    expect(await screen.findByRole('heading', { name: 'Registro de sueños' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /editar/i }))
    fireEvent.change(screen.getByLabelText(/tu idea/i), { target: { value: '# Registro de sueños\n\nPara mí y mi hermana.' } })
    fireEvent.click(screen.getByRole('button', { name: /guardar/i }))
    await waitFor(() => expect(llamadasA(espia, 'PUT /api/idea')).toHaveLength(1))
    expect(cuerpoJson(llamadasA(espia, 'PUT /api/idea')[0][1])).toEqual({
      texto_md: '# Registro de sueños\n\nPara mí y mi hermana.',
      que_sigue_md: 'Compartirlo.',
    })
  })

  it('escribirla por mi cuenta arranca con la plantilla del curso', async () => {
    const plantilla = '# El nombre de tu idea\n\n## Qué es\n\n## El molde\n'
    simularFetch({
      ...CONFIG,
      'GET /api/idea': json({ detalle: 'Todavía no hay idea.' }, 404),
      'GET /api/idea/plantilla': json({ texto_md: plantilla }),
    })
    abrir('/mi-idea')
    fireEvent.click(await screen.findByRole('button', { name: /prefiero escribirla por mi cuenta/i }))
    await waitFor(() => expect(screen.getByLabelText(/tu idea/i)).toHaveValue(plantilla))
  })

  it('si la plantilla no carga, arranca con los títulos de la idea', async () => {
    simularFetch({
      ...CONFIG,
      'GET /api/idea': json({ detalle: 'Todavía no hay idea.' }, 404),
      'GET /api/idea/plantilla': json({ detalle: 'Algo falló.' }, 500),
    })
    abrir('/mi-idea')
    fireEvent.click(await screen.findByRole('button', { name: /prefiero escribirla por mi cuenta/i }))
    const texto = (await screen.findByLabelText(/tu idea/i)) as HTMLTextAreaElement
    for (const titulo of [
      '## Qué es',
      '## Para quién',
      '## Qué siento cuando la imagino funcionando y por qué me importa',
      '## La versión más chica que ya valdría la pena',
      '## El molde',
      '## Lo que la máquina no puede adivinar',
      '## Sé que funciona si',
    ]) {
      expect(texto.value).toContain(titulo)
    }
  })

  it('sin idea todavía explica dónde se arma', async () => {
    simularFetch({ ...CONFIG, 'GET /api/idea': json({ detalle: 'Todavía no hay idea.' }, 404) })
    abrir('/mi-idea')
    expect(await screen.findByText(/la armás con el tutor en el módulo 2/i)).toBeInTheDocument()
  })
})

describe('Admin', () => {
  it('muestra el reporte a quien administra', async () => {
    simularFetch({
      ...CONFIG,
      'GET /api/yo': yo({ es_admin: true }),
      'GET /api/admin/reporte': json({ embudo: { inscriptos: 12, kits: 3 }, gasto_mes_usd: 4.5 }),
    })
    abrir('/admin')
    expect(await screen.findByText('Inscriptos')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByText(/US\$\s?4,50/)).toBeInTheDocument()
  })

  it('con newsletter configurado baja la lista de novedades', async () => {
    const espia = simularFetch({
      ...config({ newsletter: 'Boletín del curso' }),
      'GET /api/yo': yo({ es_admin: true }),
      'GET /api/admin/reporte': json({ embudo: { inscriptos: 12 } }),
      'GET /api/admin/novedades.csv': new Response('email\npersona@ejemplo.com\n', {
        headers: { 'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename="novedades.csv"' },
      }),
    })
    vi.stubGlobal('URL', Object.assign(URL, { createObjectURL: vi.fn(() => 'blob:x'), revokeObjectURL: vi.fn() }))
    const clic = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined)
    try {
      abrir('/admin')
      expect(
        await screen.findByRole('heading', { name: 'Lista de novedades (Boletín del curso)' }),
      ).toBeInTheDocument()
      fireEvent.click(screen.getByRole('button', { name: /lista de novedades \(Boletín del curso\)/i }))
      await waitFor(() => expect(llamadasA(espia, 'GET /api/admin/novedades.csv')).toHaveLength(1))
      await waitFor(() => expect(clic).toHaveBeenCalled())
    } finally {
      clic.mockRestore()
    }
  })

  it('sin newsletter configurado no ofrece la lista de novedades', async () => {
    simularFetch({
      ...config(),
      'GET /api/yo': yo({ es_admin: true }),
      'GET /api/admin/reporte': json({ embudo: { inscriptos: 12 } }),
    })
    abrir('/admin')
    expect(await screen.findByText('Inscriptos')).toBeInTheDocument()
    expect(screen.queryByText(/lista de novedades/i)).toBeNull()
  })

  it('la galería por aprobar deja aprobar y sacar links', async () => {
    const espia = simularFetch({
      ...CONFIG,
      'GET /api/yo': yo({ es_admin: true }),
      'GET /api/admin/reporte': json({ embudo: { inscriptos: 12 } }),
      'GET /api/admin/links': json([
        {
          id: 1,
          url: 'https://suenos.netlify.app',
          titulo: 'Registro de sueños',
          mostrar_galeria: true,
          aprobado: false,
          creado: '2026-09-28T10:00:00+00:00',
        },
        {
          id: 2,
          url: 'https://mate.netlify.app',
          titulo: 'Mate',
          mostrar_galeria: true,
          aprobado: true,
          creado: '2026-09-27T10:00:00+00:00',
        },
      ]),
      'PUT /api/admin/links/1': json({ ok: true }),
      'PUT /api/admin/links/2': json({ ok: true }),
    })
    abrir('/admin')
    const lista = await screen.findByRole('list', { name: /galería por aprobar/i })
    const [pendiente, aprobado] = within(lista).getAllByRole('listitem')
    expect(within(pendiente).getByRole('link', { name: /registro de sueños/i })).toHaveAttribute(
      'href',
      'https://suenos.netlify.app',
    )
    fireEvent.click(within(pendiente).getByRole('button', { name: /aprobar/i }))
    await waitFor(() => expect(llamadasA(espia, 'PUT /api/admin/links/1')).toHaveLength(1))
    expect(cuerpoJson(llamadasA(espia, 'PUT /api/admin/links/1')[0][1])).toEqual({ aprobado: true })

    fireEvent.click(within(aprobado).getByRole('button', { name: /sacar/i }))
    await waitFor(() => expect(llamadasA(espia, 'PUT /api/admin/links/2')).toHaveLength(1))
    expect(cuerpoJson(llamadasA(espia, 'PUT /api/admin/links/2')[0][1])).toEqual({ aprobado: false })
  })

  it('a quien no administra no le muestra nada', async () => {
    const espia = simularFetch({ ...CONFIG, 'GET /api/yo': yo() })
    abrir('/admin')
    expect(await screen.findByText(/solo para quien administra el curso/i)).toBeInTheDocument()
    expect(llamadasA(espia, 'GET /api/admin/reporte')).toHaveLength(0)
    expect(llamadasA(espia, 'GET /api/admin/links')).toHaveLength(0)
  })
})
