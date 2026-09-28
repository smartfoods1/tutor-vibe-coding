import { Component, lazy, type ComponentType, type ErrorInfo, type ReactNode } from 'react'

const CLAVE_RECARGA = 'vibe-recargado'

/**
 * lazy() que aguanta un despliegue nuevo: si el archivo de la página ya no existe (cambió de
 * nombre con el build), recarga una sola vez para traer la versión nueva.
 */
export function lazyConRecarga<T extends ComponentType<object>>(
  importar: () => Promise<{ default: T }>,
  recargar: () => void = () => window.location.reload(),
) {
  return lazy(async () => {
    try {
      const modulo = await importar()
      try {
        sessionStorage.removeItem(CLAVE_RECARGA)
      } catch {
        /* sin almacenamiento */
      }
      return modulo
    } catch (error) {
      let yaRecargo = true
      try {
        yaRecargo = sessionStorage.getItem(CLAVE_RECARGA) === '1'
        if (!yaRecargo) sessionStorage.setItem(CLAVE_RECARGA, '1')
      } catch {
        /* sin almacenamiento: no se arriesga un bucle de recargas */
      }
      if (!yaRecargo) {
        recargar()
        return new Promise<{ default: T }>(() => undefined)
      }
      throw error
    }
  })
}

interface Props {
  children: ReactNode
  /** Qué mostrar si algo adentro se rompe; por defecto, un aviso para recargar. */
  fallback?: ReactNode
}

export class Barrera extends Component<Props, { rota: boolean }> {
  state = { rota: false }

  static getDerivedStateFromError() {
    return { rota: true }
  }

  componentDidCatch(error: unknown, info: ErrorInfo) {
    console.error('Falla en la página', error, info.componentStack)
  }

  render() {
    if (!this.state.rota) return this.props.children
    if (this.props.fallback !== undefined) return this.props.fallback
    return (
      <div className="mx-auto max-w-2xl px-4 py-10">
        <div role="alert" className="aviso-error">
          <p>Algo no cargó bien. Puede que haya una versión nueva del curso.</p>
          <button type="button" className="boton mt-4 w-full" onClick={() => window.location.reload()}>
            Recargar la página
          </button>
        </div>
      </div>
    )
  }
}
