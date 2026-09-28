/**
 * Aprobación manual de inscripciones (APROBACION_MANUAL): cada cuenta nueva queda "pendiente" hasta
 * que quien administra la aprueba. Mientras tanto la web muestra la pantalla del pedido pendiente.
 */
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from '../src/App.tsx'
import { leerConfig } from '../src/componentes/Configuracion.tsx'
import { ErrorApi, ErrorPendiente, alPendiente, api, esPendiente, pedir } from '../src/lib/api.ts'
import { json, llamadasA, simularFetch } from './ayudas.ts'

afterEach(() => {
  vi.unstubAllGlobals()
  alPendiente(null)
})

const DETALLE_PENDIENTE = 'Tu pedido de acceso está pendiente. Te avisamos por mail cuando esté aprobado.'
const PENDIENTE_403 = () => json({ detalle: DETALLE_PENDIENTE, estado: 'pendiente' }, 403)
const PANTALLA = 'Recibimos tu pedido. Te avisamos por mail cuando tengas acceso.'
const LINEA_LANDING = 'El acceso se aprueba a mano: te avisamos por mail cuando esté listo.'

function config(extra: Record<string, unknown> = {}) {
  return {
    'GET /api/config': json({
      turnstile_site_key: null,
      aviso_prueba: false,
      autor_nombre: null,
      newsletter: null,
      modo_demo: false,
      aprobacion_manual: true,
      ...extra,
    }),
  }
}

const TEXTOS_LEGALES = {
  'GET /api/legal/consentimientos': json({
    version: '2026-09-29',
    textos: {
      mails_curso: 'Acepto recibir los mails del curso.',
      transferencia: 'Acepto que mis datos se procesen con proveedores en Estados Unidos.',
    },
    texto_md: '',
  }),
}

function yo(extra: Record<string, unknown> = {}) {
  return json({
    email: 'nueva@ejemplo.com',
    es_admin: false,
    estado: 'pendiente',
    modulo_actual: 1,
    avance: [],
    idea: null,
    taller: { herramienta: null, sistema: null },
    tope: { bloqueado: false, alcance: null },
    consentimientos: { mails_curso: true, novedades: false },
    audios: [],
    ...extra,
  })
}

function abrir(ruta: string, state?: unknown) {
  return render(
    <MemoryRouter initialEntries={[state === undefined ? ruta : { pathname: ruta, state }]}>
      <App />
    </MemoryRouter>,
  )
}

/** Espera la pantalla del pedido pendiente y la devuelve (el contenido principal). */
async function pantallaPendiente() {
  const texto = await screen.findByText(PANTALLA)
  return texto.closest('main') as HTMLElement
}

describe('api: aprobación manual', () => {
  it('un 403 de cuenta pendiente es un caso propio y avisa al manejador', async () => {
    const alEstarPendiente = vi.fn()
    alPendiente(alEstarPendiente)
    simularFetch({ 'GET /api/idea': PENDIENTE_403 })
    const error = await pedir('/api/idea').catch((e: unknown) => e)
    expect(error).toBeInstanceOf(ErrorPendiente)
    expect(error).toBeInstanceOf(ErrorApi)
    expect(esPendiente(error)).toBe(true)
    expect((error as ErrorApi).status).toBe(403)
    expect((error as ErrorApi).message).toBe(DETALLE_PENDIENTE)
    expect(alEstarPendiente).toHaveBeenCalledTimes(1)
  })

  it('otro 403 sigue siendo un error común y no avisa al manejador', async () => {
    const alEstarPendiente = vi.fn()
    alPendiente(alEstarPendiente)
    simularFetch({ 'GET /api/modulos/3/guia': json({ detalle: 'Este módulo todavía no está abierto.' }, 403) })
    const error = await pedir('/api/modulos/3/guia').catch((e: unknown) => e)
    expect(error).toBeInstanceOf(ErrorApi)
    expect(esPendiente(error)).toBe(false)
    expect(alEstarPendiente).not.toHaveBeenCalled()
  })

  it('el turno del tutor con la cuenta pendiente levanta el error propio', async () => {
    const alEstarPendiente = vi.fn()
    alPendiente(alEstarPendiente)
    simularFetch({ 'POST /api/sesiones/4/turno': PENDIENTE_403 })
    const error = await api.turno(4, { texto: 'hola' }, () => undefined).catch((e: unknown) => e)
    expect(esPendiente(error)).toBe(true)
    expect(alEstarPendiente).toHaveBeenCalledTimes(1)
  })

  it('verificar trae el estado de la cuenta', async () => {
    simularFetch({ 'POST /api/auth/verificar': json({ ok: true, nuevo: true, estado: 'pendiente' }) })
    expect(await api.verificar('nueva@ejemplo.com', '123456')).toEqual({ ok: true, nuevo: true, estado: 'pendiente' })
  })

  it('los pedidos de acceso usan las rutas de admin', async () => {
    const espia = simularFetch({
      'GET /api/admin/pedidos': json([]),
      'POST /api/admin/pedidos/3/aprobar': json({ ok: true }),
      'DELETE /api/admin/pedidos/4': json({ ok: true }),
    })
    expect(await api.pedidosDeAcceso()).toEqual([])
    await api.aprobarPedido(3)
    await api.rechazarPedido(4)
    expect(llamadasA(espia, 'GET /api/admin/pedidos')).toHaveLength(1)
    expect(llamadasA(espia, 'POST /api/admin/pedidos/3/aprobar')).toHaveLength(1)
    expect(llamadasA(espia, 'DELETE /api/admin/pedidos/4')).toHaveLength(1)
  })

  it('leerConfig toma aprobacion_manual (y sin el campo queda apagada)', () => {
    expect(leerConfig({ aprobacion_manual: true }).aprobacionManual).toBe(true)
    expect(leerConfig({ aprobacion_manual: 'true' }).aprobacionManual).toBe(false)
    expect(leerConfig({}).aprobacionManual).toBe(false)
  })
})

describe('Landing con aprobación manual', () => {
  it('debajo del botón avisa que el acceso se aprueba a mano', async () => {
    simularFetch({ ...config(), ...TEXTOS_LEGALES, 'GET /api/yo': json({ detalle: 'no' }, 401) })
    abrir('/')
    const boton = await screen.findByRole('button', { name: /quiero empezar/i })
    const linea = screen.getByText(LINEA_LANDING)
    expect(boton.compareDocumentPosition(linea) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  })

  it('sin aprobación manual no dice nada de eso', async () => {
    simularFetch({ ...config({ aprobacion_manual: false }), ...TEXTOS_LEGALES, 'GET /api/yo': json({ detalle: 'no' }, 401) })
    abrir('/')
    await screen.findByRole('button', { name: /quiero empezar/i })
    expect(screen.queryByText(LINEA_LANDING)).toBeNull()
  })

  it('con una sesión pendiente no dice "ya estás adentro" sino que el pedido espera', async () => {
    simularFetch({ ...config(), ...TEXTOS_LEGALES, 'GET /api/yo': yo() })
    abrir('/')
    expect(await screen.findByText(/tu pedido de acceso está pendiente/i)).toBeInTheDocument()
    expect(screen.queryByText(/ya estás adentro/i)).toBeNull()
  })
})

describe('Entrar con aprobación manual', () => {
  it('si verificar devuelve pendiente, muestra la pantalla del pedido con el mail, Mis datos y Salir', async () => {
    const espia = simularFetch({
      ...config(),
      'POST /api/auth/codigo': json({ ok: true }),
      'POST /api/auth/verificar': json({ ok: true, nuevo: true, estado: 'pendiente' }),
      'GET /api/yo': yo(),
      'POST /api/auth/salir': json({ ok: true }),
      ...TEXTOS_LEGALES,
    })
    abrir('/entrar', { email: 'nueva@ejemplo.com', enviado: true })
    fireEvent.change(await screen.findByLabelText(/código/i), { target: { value: '123456' } })
    fireEvent.click(screen.getByRole('button', { name: /^entrar$/i }))

    const pantalla = await pantallaPendiente()
    expect(within(pantalla).getByText('nueva@ejemplo.com')).toBeInTheDocument()
    expect(within(pantalla).getByRole('link', { name: /mis datos/i })).toHaveAttribute('href', '/mis-datos')
    // No abre el módulo 1 ni el tutor.
    expect(llamadasA(espia, 'POST /api/modulos/1/sesion')).toHaveLength(0)

    fireEvent.click(within(pantalla).getByRole('button', { name: /salir/i }))
    await waitFor(() => expect(llamadasA(espia, 'POST /api/auth/salir')).toHaveLength(1))
    expect(await screen.findByRole('heading', { level: 1, name: /de lo que imaginás/i })).toBeInTheDocument()
  })

  it('si verificar devuelve aprobado, sigue como siempre (nuevo: al módulo 1)', async () => {
    simularFetch({
      ...config(),
      'POST /api/auth/verificar': json({ ok: true, nuevo: true, estado: 'aprobado' }),
      'GET /api/yo': yo({ estado: 'aprobado' }),
      'POST /api/modulos/1/sesion': json({ id: 3, retomada: true }),
      'GET /api/sesiones/3': json({ id: 3, modulo: 1, mensajes: [{ rol: 'tutor', texto: 'Hola.' }] }),
    })
    abrir('/entrar', { email: 'nueva@ejemplo.com', enviado: true })
    fireEvent.change(await screen.findByLabelText(/código/i), { target: { value: '123456' } })
    fireEvent.click(screen.getByRole('button', { name: /^entrar$/i }))
    expect(await screen.findByText('Hola.')).toBeInTheDocument()
    expect(screen.queryByText(PANTALLA)).toBeNull()
  })
})

describe('Pantalla del pedido pendiente', () => {
  it('aparece en Inicio si /api/yo trae estado pendiente', async () => {
    simularFetch({ ...config(), 'GET /api/yo': yo() })
    abrir('/inicio')
    const pantalla = await pantallaPendiente()
    expect(within(pantalla).getByText('nueva@ejemplo.com')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /empezar el módulo 1/i })).toBeNull()
  })

  it('aparece en un módulo sin abrir el tutor', async () => {
    const espia = simularFetch({ ...config(), 'GET /api/yo': yo() })
    abrir('/modulo/1')
    await pantallaPendiente()
    expect(llamadasA(espia, 'POST /api/modulos/1/sesion')).toHaveLength(0)
    expect(screen.queryByLabelText(/tu mensaje/i)).toBeNull()
  })

  it('aparece en Mostrar en lugar del formulario del link', async () => {
    simularFetch({ ...config(), 'GET /api/yo': yo() })
    abrir('/mostrar')
    await pantallaPendiente()
    expect(screen.queryByLabelText(/el link de tu página/i)).toBeNull()
  })

  it('aparece si cualquier pedido devuelve el 403 de pendiente', async () => {
    simularFetch({ ...config(), 'GET /api/idea': PENDIENTE_403, 'GET /api/yo': yo() })
    abrir('/mi-idea')
    const pantalla = await pantallaPendiente()
    expect(within(pantalla).getByText('nueva@ejemplo.com')).toBeInTheDocument()
  })

  it('una cuenta aprobada no se queda en la pantalla del pedido', async () => {
    simularFetch({ ...config(), 'GET /api/yo': yo({ estado: 'aprobado' }) })
    abrir('/pendiente')
    expect(await screen.findByRole('link', { name: /empezar el módulo 1/i })).toBeInTheDocument()
    expect(screen.queryByText(PANTALLA)).toBeNull()
  })

  it('Mis datos deja borrar todo sin pedir los links (que la cuenta pendiente no puede ver)', async () => {
    const espia = simularFetch({
      ...config(),
      'GET /api/yo': yo(),
      'GET /api/links': PENDIENTE_403,
      'DELETE /api/mis-datos': json({ ok: true }),
    })
    abrir('/mis-datos')
    const boton = await screen.findByRole('button', { name: /borrar todos mis datos/i })
    expect(llamadasA(espia, 'GET /api/links')).toHaveLength(0)
    fireEvent.change(screen.getByLabelText(/escribí BORRAR/i), { target: { value: 'BORRAR' } })
    fireEvent.click(boton)
    expect(await screen.findByText(/borramos todos tus datos/i)).toBeInTheDocument()
    expect(screen.queryByText(PANTALLA)).toBeNull()
  })
})

describe('Admin: pedidos de acceso', () => {
  const PEDIDOS = [
    { id: 11, email: 'primera@ejemplo.com', creado: '2026-09-27T13:00:00+00:00', fuente: 'radio-local' },
    { id: 12, email: 'segunda@ejemplo.com', creado: '2026-09-28T15:30:00+00:00', fuente: null },
  ]

  function rutasAdmin(extra: Record<string, unknown> = {}) {
    let pendientes = [...PEDIDOS]
    const espia = simularFetch({
      ...config(),
      'GET /api/yo': yo({ email: 'admin@ejemplo.com', es_admin: true, estado: 'aprobado' }),
      'GET /api/admin/reporte': json({ embudo: { inscriptos: 12 }, pendientes: 2 }),
      'GET /api/admin/links': json([]),
      'GET /api/admin/pedidos': () => json(pendientes),
      'POST /api/admin/pedidos/11/aprobar': () => {
        pendientes = pendientes.filter((p) => p.id !== 11)
        return json({ ok: true })
      },
      'DELETE /api/admin/pedidos/12': () => {
        pendientes = pendientes.filter((p) => p.id !== 12)
        return json({ ok: true })
      },
      ...(extra as Record<string, Response>),
    })
    return espia
  }

  it('la sección va arriba de todo, con la cantidad y cada pedido con mail, fecha y fuente', async () => {
    rutasAdmin()
    abrir('/admin')
    const titulo = await screen.findByRole('heading', { name: 'Pedidos de acceso' })
    const galeria = await screen.findByRole('heading', { name: /galería por aprobar/i })
    expect(titulo.compareDocumentPosition(galeria) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()

    const lista = await screen.findByRole('list', { name: 'Pedidos de acceso' })
    expect(screen.getByText('2 pedidos pendientes.')).toBeInTheDocument()
    const [primero, segundo] = within(lista).getAllByRole('listitem')
    expect(within(primero).getByText('primera@ejemplo.com')).toBeInTheDocument()
    expect(within(primero).getByText(/2026/)).toBeInTheDocument()
    expect(within(primero).getByText(/radio-local/)).toBeInTheDocument()
    expect(within(segundo).getByText('segunda@ejemplo.com')).toBeInTheDocument()
    expect(within(segundo).getByText(/sin fuente/i)).toBeInTheDocument()
  })

  it('aprobar manda el POST y la lista se actualiza', async () => {
    const espia = rutasAdmin()
    abrir('/admin')
    const lista = await screen.findByRole('list', { name: 'Pedidos de acceso' })
    const [primero] = within(lista).getAllByRole('listitem')
    fireEvent.click(within(primero).getByRole('button', { name: /aprobar/i }))
    await waitFor(() => expect(llamadasA(espia, 'POST /api/admin/pedidos/11/aprobar')).toHaveLength(1))
    await waitFor(() => expect(screen.queryByText('primera@ejemplo.com')).toBeNull())
    expect(screen.getByText('segunda@ejemplo.com')).toBeInTheDocument()
    expect(await screen.findByText('1 pedido pendiente.')).toBeInTheDocument()
  })

  it('rechazar pide confirmación ("Se borran sus datos. ¿Seguro?") y recién ahí borra', async () => {
    const espia = rutasAdmin()
    abrir('/admin')
    const lista = await screen.findByRole('list', { name: 'Pedidos de acceso' })
    const segundo = within(lista).getAllByRole('listitem')[1]

    fireEvent.click(within(segundo).getByRole('button', { name: /rechazar/i }))
    expect(within(segundo).getByText('Se borran sus datos. ¿Seguro?')).toBeInTheDocument()
    fireEvent.click(within(segundo).getByRole('button', { name: /cancelar/i }))
    expect(within(segundo).queryByText('Se borran sus datos. ¿Seguro?')).toBeNull()
    expect(llamadasA(espia, 'DELETE /api/admin/pedidos/12')).toHaveLength(0)

    fireEvent.click(within(segundo).getByRole('button', { name: /rechazar/i }))
    fireEvent.click(within(segundo).getByRole('button', { name: /sí, rechazar/i }))
    await waitFor(() => expect(llamadasA(espia, 'DELETE /api/admin/pedidos/12')).toHaveLength(1))
    await waitFor(() => expect(screen.queryByText('segunda@ejemplo.com')).toBeNull())
    expect(screen.getByText('primera@ejemplo.com')).toBeInTheDocument()
  })

  it('si el pedido ya se resolvió muestra el detalle y trae la lista de nuevo', async () => {
    let pedidos = [...PEDIDOS]
    const espia = rutasAdmin({
      'GET /api/admin/pedidos': () => json(pedidos),
      'POST /api/admin/pedidos/11/aprobar': () => {
        pedidos = pedidos.filter((p) => p.id !== 11)
        return json({ detalle: 'Ese pedido ya estaba aprobado.' }, 409)
      },
    })
    abrir('/admin')
    const lista = await screen.findByRole('list', { name: 'Pedidos de acceso' })
    fireEvent.click(within(within(lista).getAllByRole('listitem')[0]).getByRole('button', { name: /aprobar/i }))
    expect(await screen.findByText('Ese pedido ya estaba aprobado.')).toBeInTheDocument()
    await waitFor(() => expect(llamadasA(espia, 'GET /api/admin/pedidos').length).toBeGreaterThanOrEqual(2))
    await waitFor(() => expect(screen.queryByText('primera@ejemplo.com')).toBeNull())
  })

  it('sin pedidos lo dice', async () => {
    rutasAdmin({ 'GET /api/admin/pedidos': json([]) })
    abrir('/admin')
    expect(await screen.findByText('No hay pedidos pendientes.')).toBeInTheDocument()
    expect(screen.queryByRole('list', { name: 'Pedidos de acceso' })).toBeNull()
  })

  it('sin aprobación manual y sin pedidos no muestra la sección', async () => {
    const espia = rutasAdmin({ ...config({ aprobacion_manual: false }), 'GET /api/admin/pedidos': json([]) })
    abrir('/admin')
    await screen.findByRole('heading', { name: /galería por aprobar/i })
    await waitFor(() => expect(llamadasA(espia, 'GET /api/admin/pedidos')).toHaveLength(1))
    expect(screen.queryByRole('heading', { name: 'Pedidos de acceso' })).toBeNull()
  })

  it('aprobar va sin cuerpo', async () => {
    const espia = rutasAdmin()
    abrir('/admin')
    const lista = await screen.findByRole('list', { name: 'Pedidos de acceso' })
    fireEvent.click(within(within(lista).getAllByRole('listitem')[0]).getByRole('button', { name: /aprobar/i }))
    await waitFor(() => expect(llamadasA(espia, 'POST /api/admin/pedidos/11/aprobar')).toHaveLength(1))
    expect(llamadasA(espia, 'POST /api/admin/pedidos/11/aprobar')[0][1]?.body).toBeUndefined()
  })
})
