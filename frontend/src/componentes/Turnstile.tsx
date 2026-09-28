import { useEffect, useRef } from 'react'

export const URL_TURNSTILE = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit'
const ACCION = 'inscripcion'

interface OpcionesTurnstile {
  sitekey: string
  action: string
  language?: string
  theme?: 'light' | 'dark' | 'auto'
  size?: 'normal' | 'flexible' | 'compact'
  callback: (token: string) => void
  'expired-callback'?: () => void
  'error-callback'?: () => void
}

interface ApiTurnstile {
  render: (elemento: HTMLElement, opciones: OpcionesTurnstile) => string | undefined
  reset: (id?: string) => void
  remove: (id?: string) => void
}

declare global {
  interface Window {
    turnstile?: ApiTurnstile
  }
}

let cargaDelScript: Promise<void> | null = null

function cargarScript(): Promise<void> {
  if (window.turnstile) return Promise.resolve()
  if (cargaDelScript) return cargaDelScript
  cargaDelScript = new Promise<void>((listo, fallo) => {
    const script = document.createElement('script')
    script.src = URL_TURNSTILE
    script.async = true
    script.defer = true
    script.addEventListener('load', () => listo())
    script.addEventListener('error', () => {
      cargaDelScript = null
      script.remove()
      fallo(new Error('No se pudo cargar Turnstile'))
    })
    document.head.appendChild(script)
  })
  return cargaDelScript
}

interface Props {
  siteKey: string
  alToken: (token: string | null) => void
  /** Cambiar este número pide un token nuevo (los tokens se usan una sola vez). */
  reinicio?: number
}

/** Verificación anti-robots de Cloudflare. Solo se muestra si el servidor tiene clave. */
export default function Turnstile({ siteKey, alToken, reinicio = 0 }: Props) {
  const contenedor = useRef<HTMLDivElement>(null)
  const widget = useRef<string | undefined>(undefined)
  const alTokenActual = useRef(alToken)
  alTokenActual.current = alToken

  useEffect(() => {
    let vigente = true
    cargarScript()
      .then(() => {
        if (!vigente || !contenedor.current || !window.turnstile) return
        widget.current = window.turnstile.render(contenedor.current, {
          sitekey: siteKey,
          action: ACCION,
          language: 'es',
          theme: 'light',
          size: 'flexible',
          callback: (token) => alTokenActual.current(token),
          'expired-callback': () => alTokenActual.current(null),
          'error-callback': () => alTokenActual.current(null),
        })
      })
      .catch(() => alTokenActual.current(null))
    return () => {
      vigente = false
      if (widget.current !== undefined) window.turnstile?.remove(widget.current)
      widget.current = undefined
    }
  }, [siteKey])

  useEffect(() => {
    if (reinicio > 0 && widget.current !== undefined) {
      alTokenActual.current(null)
      window.turnstile?.reset(widget.current)
    }
  }, [reinicio])

  return <div ref={contenedor} data-testid="turnstile" className="min-h-[65px]" />
}
