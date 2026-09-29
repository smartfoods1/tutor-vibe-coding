import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { api, type SiguientePaso } from '../lib/api.ts'

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
  /** APROBACION_MANUAL: cada inscripción nueva espera que quien administra la apruebe. */
  aprobacionManual: boolean
  /**
   * SIGUIENTE_PASO: los tres textos de la instalación para la pregunta después del primer link y el
   * aviso en "Mis datos". null = función apagada (o incompleta, que cuenta como apagada).
   */
  siguientePaso: SiguientePaso | null
}

export interface ConfigApp extends DatosConfig {
  cargada: boolean
}

const texto = (valor: unknown): string | null => (typeof valor === 'string' && valor.trim() ? valor.trim() : null)

/** Los textos del siguiente paso: si falta cualquiera de los tres, la función queda apagada (FR-001). */
function leerSiguientePaso(valor: unknown): SiguientePaso | null {
  if (!valor || typeof valor !== 'object') return null
  const d = valor as Record<string, unknown>
  const nombre = texto(d.nombre)
  const pregunta = texto(d.pregunta)
  const textoPaso = texto(d.texto)
  return nombre && pregunta && textoPaso ? { nombre, pregunta, texto: textoPaso } : null
}

/** Traduce la respuesta de /api/config: lo que falta o no se entiende queda en null o en false. */
export function leerConfig(datos: unknown): DatosConfig {
  const d = datos && typeof datos === 'object' ? (datos as Record<string, unknown>) : {}
  return {
    turnstileSiteKey: texto(d.turnstile_site_key),
    avisoPrueba: d.aviso_prueba === true,
    autorNombre: texto(d.autor_nombre),
    newsletter: texto(d.newsletter),
    modoDemo: d.modo_demo === true,
    aprobacionManual: d.aprobacion_manual === true,
    siguientePaso: leerSiguientePaso(d.siguiente_paso),
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
