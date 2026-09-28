import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from '../src/App.tsx'
import { cuerpoJson, json, llamadasA, simularFetch } from './ayudas.ts'

const TEXTOS = {
  version: '2026-09-28',
  textos: {
    mails_curso: 'Acepto recibir los mails del curso.',
    transferencia: 'Acepto que mis datos se procesen con proveedores en Estados Unidos.',
    novedades: 'Quiero recibir las novedades del curso por mail.',
  },
  texto_md: 'Te explicamos **por qué** te pedimos cada cosa.',
}

/** Config con casilla de novedades: el backend manda el nombre del newsletter. */
function config(extra: Record<string, unknown> = {}) {
  return json({
    turnstile_site_key: null,
    aviso_prueba: false,
    autor_nombre: null,
    newsletter: 'Boletín del curso',
    modo_demo: false,
    ...extra,
  })
}

function rutas(extra: Record<string, Response | ((init?: RequestInit) => Response)> = {}) {
  return simularFetch({
    'GET /api/config': config(),
    'GET /api/legal/consentimientos': json(TEXTOS),
    'GET /api/yo': json({ detalle: 'Tu sesión venció.' }, 401),
    'POST /api/auth/codigo': json({ ok: true }),
    ...extra,
  })
}

function abrir(ruta = '/') {
  return render(
    <MemoryRouter initialEntries={[ruta]}>
      <App />
    </MemoryRouter>,
  )
}

async function completarMail(mail = 'persona@ejemplo.com') {
  fireEvent.change(await screen.findByLabelText(/tu mail/i), { target: { value: mail } })
}

beforeEach(() => {
  try {
    sessionStorage.clear()
  } catch {
    /* sin almacenamiento */
  }
})

afterEach(() => {
  vi.unstubAllGlobals()
  document.querySelectorAll('script[src*="turnstile"]').forEach((s) => s.remove())
  delete (window as { turnstile?: unknown }).turnstile
})

describe('Landing', () => {
  it('muestra las tres casillas con los textos legales y todas desmarcadas', async () => {
    rutas()
    abrir()
    const mails = await screen.findByRole('checkbox', { name: /mails del curso/i })
    const transferencia = screen.getByRole('checkbox', { name: /Estados Unidos/i })
    const novedades = screen.getByRole('checkbox', { name: /novedades del curso/i })
    expect(mails).not.toBeChecked()
    expect(transferencia).not.toBeChecked()
    expect(novedades).not.toBeChecked()
    expect(screen.getAllByText(/obligatori/i).length).toBeGreaterThanOrEqual(2)
    expect(screen.getByText(/opcional/i)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /cómo cuidamos tus datos/i })).toHaveAttribute('href', '/privacidad')
  })

  it('sin las dos casillas obligatorias explica por qué y no manda nada', async () => {
    const espia = rutas()
    abrir()
    await completarMail()
    fireEvent.click(screen.getByRole('checkbox', { name: /mails del curso/i }))
    fireEvent.click(screen.getByRole('button', { name: /quiero empezar/i }))
    expect(
      await screen.findByText(
        'El curso funciona con proveedores en Estados Unidos y Brasil; sin ese permiso no podemos darte el curso.',
      ),
    ).toBeInTheDocument()
    expect(llamadasA(espia, 'POST /api/auth/codigo')).toHaveLength(0)
  })

  it('con un mail que no es válido lo avisa', async () => {
    const espia = rutas()
    abrir()
    await completarMail('persona-sin-arroba')
    fireEvent.click(screen.getByRole('button', { name: /quiero empezar/i }))
    expect(await screen.findByText(/no parece una dirección válida/i)).toBeInTheDocument()
    expect(llamadasA(espia, 'POST /api/auth/codigo')).toHaveLength(0)
  })

  it('manda el mail, los consentimientos y la fuente del ?ref=, y pasa a pedir el código', async () => {
    const espia = rutas()
    abrir('/?ref=Radio-Local')
    await completarMail(' Persona@Ejemplo.com ')
    fireEvent.click(screen.getByRole('checkbox', { name: /mails del curso/i }))
    fireEvent.click(screen.getByRole('checkbox', { name: /Estados Unidos/i }))
    fireEvent.click(screen.getByRole('button', { name: /quiero empezar/i }))

    expect(await screen.findByLabelText(/código/i)).toBeInTheDocument()
    expect(screen.getByText(/persona@ejemplo.com/i)).toBeInTheDocument()
    const [llamada] = llamadasA(espia, 'POST /api/auth/codigo')
    expect(cuerpoJson(llamada[1])).toEqual({
      email: 'persona@ejemplo.com',
      consentimientos: { mails_curso: true, transferencia: true, novedades: false },
      fuente: 'radio-local',
    })
  })

  it('si marca la casilla de novedades la manda en true', async () => {
    const espia = rutas()
    abrir()
    await completarMail()
    fireEvent.click(screen.getByRole('checkbox', { name: /mails del curso/i }))
    fireEvent.click(screen.getByRole('checkbox', { name: /Estados Unidos/i }))
    fireEvent.click(screen.getByRole('checkbox', { name: /novedades del curso/i }))
    fireEvent.click(screen.getByRole('button', { name: /quiero empezar/i }))
    await screen.findByLabelText(/código/i)
    const [llamada] = llamadasA(espia, 'POST /api/auth/codigo')
    expect(cuerpoJson(llamada[1])).toMatchObject({
      consentimientos: { mails_curso: true, transferencia: true, novedades: true },
    })
  })

  it('sin newsletter configurado no muestra la casilla de novedades y la manda en false', async () => {
    const { novedades: _sinUso, ...sinNovedades } = TEXTOS.textos
    const espia = rutas({
      'GET /api/config': config({ newsletter: null }),
      'GET /api/legal/consentimientos': json({ ...TEXTOS, textos: sinNovedades }),
    })
    abrir()
    await screen.findByRole('checkbox', { name: /mails del curso/i })
    expect(screen.getAllByRole('checkbox')).toHaveLength(2)
    expect(screen.queryByText(/opcional/i)).toBeNull()
    expect(screen.queryByText(/no pudimos cargar los textos/i)).toBeNull()

    await completarMail()
    fireEvent.click(screen.getByRole('checkbox', { name: /mails del curso/i }))
    fireEvent.click(screen.getByRole('checkbox', { name: /Estados Unidos/i }))
    fireEvent.click(screen.getByRole('button', { name: /quiero empezar/i }))
    await screen.findByLabelText(/código/i)
    const [llamada] = llamadasA(espia, 'POST /api/auth/codigo')
    expect(cuerpoJson(llamada[1])).toMatchObject({
      consentimientos: { mails_curso: true, transferencia: true, novedades: false },
    })
  })

  it('con newsletter, si falta el texto legal de novedades no inscribe', async () => {
    const { novedades: _sinUso, ...sinNovedades } = TEXTOS.textos
    rutas({ 'GET /api/legal/consentimientos': json({ ...TEXTOS, textos: sinNovedades }) })
    abrir()
    expect(await screen.findByText(/no pudimos cargar los textos de la inscripción/i)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /quiero empezar/i })).toBeNull()
  })

  it('muestra el motivo que devuelve el servidor', async () => {
    rutas({ 'POST /api/auth/codigo': json({ detalle: 'Revisá el mail: no parece una dirección válida.' }, 422) })
    abrir()
    await completarMail('raro@ejemplo.com')
    fireEvent.click(screen.getByRole('checkbox', { name: /mails del curso/i }))
    fireEvent.click(screen.getByRole('checkbox', { name: /Estados Unidos/i }))
    fireEvent.click(screen.getByRole('button', { name: /quiero empezar/i }))
    expect(await screen.findByText('Revisá el mail: no parece una dirección válida.')).toBeInTheDocument()
  })

  it('si falta el texto legal de una casilla muestra un error y no un texto inventado', async () => {
    const espia = rutas({
      'GET /api/legal/consentimientos': json({
        ...TEXTOS,
        textos: { mails_curso: TEXTOS.textos.mails_curso, novedades: TEXTOS.textos.novedades },
      }),
    })
    abrir()
    expect(await screen.findByText(/no pudimos cargar los textos de la inscripción/i)).toBeInTheDocument()
    expect(screen.queryByRole('checkbox', { name: /Estados Unidos/i })).toBeNull()
    expect(screen.queryByRole('button', { name: /quiero empezar/i })).toBeNull()
    expect(llamadasA(espia, 'POST /api/auth/codigo')).toHaveLength(0)
  })

  it('sin clave de Turnstile no carga el widget', async () => {
    rutas()
    abrir()
    await screen.findByRole('checkbox', { name: /mails del curso/i })
    expect(document.querySelector('script[src*="challenges.cloudflare.com/turnstile"]')).toBeNull()
    expect(screen.queryByTestId('turnstile')).toBeNull()
  })

  it('con clave de Turnstile carga el widget con la acción inscripcion y manda el token', async () => {
    const dibujar = vi.fn((_el: HTMLElement, opciones: { callback: (t: string) => void }) => {
      opciones.callback('token-prueba')
      return 'w1'
    })
    ;(window as { turnstile?: unknown }).turnstile = { render: dibujar, reset: vi.fn(), remove: vi.fn() }
    const espia = rutas({ 'GET /api/config': config({ turnstile_site_key: 'clave-sitio' }) })
    abrir()
    expect(await screen.findByTestId('turnstile')).toBeInTheDocument()
    await waitFor(() => expect(dibujar).toHaveBeenCalled())
    expect(dibujar.mock.calls[0][1]).toMatchObject({ sitekey: 'clave-sitio', action: 'inscripcion' })

    await completarMail()
    fireEvent.click(screen.getByRole('checkbox', { name: /mails del curso/i }))
    fireEvent.click(screen.getByRole('checkbox', { name: /Estados Unidos/i }))
    fireEvent.click(screen.getByRole('button', { name: /quiero empezar/i }))
    await screen.findByLabelText(/código/i)
    const [llamada] = llamadasA(espia, 'POST /api/auth/codigo')
    expect(cuerpoJson(llamada[1])).toMatchObject({ turnstile: 'token-prueba' })
  })

  it('carga el script de Turnstile cuando todavía no está', async () => {
    rutas({ 'GET /api/config': config({ turnstile_site_key: 'clave-sitio' }) })
    abrir()
    await screen.findByTestId('turnstile')
    await waitFor(() =>
      expect(document.querySelector('script[src*="challenges.cloudflare.com/turnstile"]')).not.toBeNull(),
    )
  })

  it('muestra la franja de versión de prueba solo si la config lo pide', async () => {
    rutas({ 'GET /api/config': config({ aviso_prueba: true }) })
    const { unmount } = abrir()
    expect(await screen.findByText('Versión de prueba: el curso todavía no se lanzó')).toBeInTheDocument()
    unmount()
    rutas()
    abrir()
    await screen.findByRole('checkbox', { name: /mails del curso/i })
    expect(screen.queryByText(/versión de prueba/i)).toBeNull()
  })
})

describe('Entrar', () => {
  it('quien ya está inscripto pide el código solo con el mail y entra', async () => {
    const espia = rutas({
      'POST /api/auth/verificar': json({ ok: true, nuevo: false }),
      'GET /api/yo': json({
        email: 'persona@ejemplo.com',
        modulo_actual: 2,
        avance: [{ modulo: 1, completado: '2026-09-28T10:00:00+00:00', via: 'tutor' }],
        idea: null,
        taller: { herramienta: null, sistema: null },
        tope: { bloqueado: false, alcance: null },
        consentimientos: { mails_curso: true, novedades: false },
        audios: [],
      }),
    })
    abrir('/entrar')
    fireEvent.change(await screen.findByLabelText(/tu mail/i), { target: { value: 'persona@ejemplo.com' } })
    fireEvent.click(screen.getByRole('button', { name: /mandame el código/i }))
    const codigo = await screen.findByLabelText(/código/i)
    const [pedido] = llamadasA(espia, 'POST /api/auth/codigo')
    expect(cuerpoJson(pedido[1])).toEqual({ email: 'persona@ejemplo.com' })

    fireEvent.change(codigo, { target: { value: '123 456' } })
    fireEvent.click(screen.getByRole('button', { name: /^entrar$/i }))
    await waitFor(() => expect(llamadasA(espia, 'POST /api/auth/verificar')).toHaveLength(1))
    expect(cuerpoJson(llamadasA(espia, 'POST /api/auth/verificar')[0][1])).toEqual({
      email: 'persona@ejemplo.com',
      codigo: '123456',
    })
    expect(await screen.findByRole('link', { name: /seguir con el módulo 2/i })).toBeInTheDocument()
  })

  it('si pide otro código después de anotarse, reenvía los permisos y la fuente de la portada', async () => {
    const espia = rutas()
    abrir('/?ref=radio-local')
    await completarMail('persona@ejemplo.com')
    fireEvent.click(screen.getByRole('checkbox', { name: /mails del curso/i }))
    fireEvent.click(screen.getByRole('checkbox', { name: /Estados Unidos/i }))
    fireEvent.click(screen.getByRole('button', { name: /quiero empezar/i }))
    await screen.findByLabelText(/código/i)

    fireEvent.click(screen.getByRole('button', { name: /pedir otro código/i }))
    expect(await screen.findByLabelText(/tu mail/i)).toHaveValue('persona@ejemplo.com')
    fireEvent.click(screen.getByRole('button', { name: /mandame el código/i }))
    await screen.findByLabelText(/código/i)
    const pedidos = llamadasA(espia, 'POST /api/auth/codigo')
    expect(pedidos).toHaveLength(2)
    expect(cuerpoJson(pedidos[1][1])).toEqual({
      email: 'persona@ejemplo.com',
      consentimientos: { mails_curso: true, transferencia: true, novedades: false },
      fuente: 'radio-local',
    })
  })

  it('quien llega a /entrar sin anotarse ve el motivo y el link a la portada para anotarse', async () => {
    rutas({
      'POST /api/auth/codigo': json({ detalle: 'Para hacer el curso necesitamos mandarte mails del curso.' }, 422),
    })
    abrir('/entrar')
    fireEvent.change(await screen.findByLabelText(/tu mail/i), { target: { value: 'nueva@ejemplo.com' } })
    fireEvent.click(screen.getByRole('button', { name: /mandame el código/i }))
    const alerta = await screen.findByRole('alert')
    expect(alerta).toHaveTextContent('Para hacer el curso necesitamos mandarte mails del curso.')
    const anotarse = screen.getAllByRole('link', { name: /anotate/i })
    expect(anotarse.some((l) => alerta.contains(l) && l.getAttribute('href') === '/')).toBe(true)
  })

  it('un código equivocado muestra el detalle y deja probar de nuevo', async () => {
    rutas({ 'POST /api/auth/verificar': json({ detalle: 'El código no es válido o ya venció. Pedí uno nuevo.' }, 401) })
    abrir('/entrar')
    fireEvent.change(await screen.findByLabelText(/tu mail/i), { target: { value: 'a@ejemplo.com' } })
    fireEvent.click(screen.getByRole('button', { name: /mandame el código/i }))
    fireEvent.change(await screen.findByLabelText(/código/i), { target: { value: '000000' } })
    fireEvent.click(screen.getByRole('button', { name: /^entrar$/i }))
    expect(await screen.findByText(/no es válido o ya venció/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/código/i)).toBeInTheDocument()
  })
})
