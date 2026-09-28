import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { api } from '../lib/api.ts'

/** Lo que la instalación configura en el backend y la app necesita saber (GET /api/config). */
export interface DatosConfig {
  turnstileSiteKey: string | null
  avisoPrueba: boolean
  /** AUTOR_NOMBRE: con quién se habla en los textos fijos ("Audio de …"). null = textos genéricos. */
  autorNombre: string | null
  /** NEWSLETTER_NOMBRE: si hay, se ofrece la casilla de novedades. null = no hay casilla. */
  newsletter: string | null
  /** MODO_DEMO: el tutor responde con un guion fijo, sin IA, y la voz queda apagada. */
  modoDemo: boolean
}

export interface ConfigApp extends DatosConfig {
  cargada: boolean
}

const texto = (valor: unknown): string | null => (typeof valor === 'string' && valor.trim() ? valor.trim() : null)

/** Traduce la respuesta de /api/config: lo que falta o no se entiende queda en null o en false. */
export function leerConfig(datos: unknown): DatosConfig {
  const d = datos && typeof datos === 'object' ? (datos as Record<string, unknown>) : {}
  return {
    turnstileSiteKey: texto(d.turnstile_site_key),
    avisoPrueba: d.aviso_prueba === true,
    autorNombre: texto(d.autor_nombre),
    newsletter: texto(d.newsletter),
    modoDemo: d.modo_demo === true,
  }
}

const INICIAL: ConfigApp = { ...leerConfig(null), cargada: false }

const Contexto = createContext<ConfigApp>(INICIAL)

export function ProveedorConfig({ children }: { children: ReactNode }) {
  const [config, setConfig] = useState<ConfigApp>(INICIAL)

  useEffect(() => {
    let vigente = true
    api
      .config()
      .then((datos) => {
        if (vigente) setConfig({ ...leerConfig(datos), cargada: true })
      })
      .catch(() => {
        if (vigente) setConfig((previa) => ({ ...previa, cargada: true }))
      })
    return () => {
      vigente = false
    }
  }, [])

  return <Contexto.Provider value={config}>{children}</Contexto.Provider>
}

export function useConfig(): ConfigApp {
  return useContext(Contexto)
}

function Franja({ children }: { children: ReactNode }) {
  return (
    <div role="note" className="border-b border-linea bg-hoja px-4 py-1 text-center text-[0.85rem] text-marron">
      {children}
    </div>
  )
}

export function AvisoPrueba() {
  const { avisoPrueba } = useConfig()
  if (!avisoPrueba) return null
  return <Franja>Versión de prueba: el curso todavía no se lanzó</Franja>
}

export function AvisoDemo() {
  const { modoDemo } = useConfig()
  if (!modoDemo) return null
  return <Franja>Modo demo: el tutor responde con un guion de ejemplo, sin IA</Franja>
}
