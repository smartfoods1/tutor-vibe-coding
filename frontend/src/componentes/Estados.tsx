import type { ReactNode } from 'react'

export function Cargando({ texto = 'Cargando' }: { texto?: string }) {
  return (
    <p role="status" className="py-6 text-marron">
      <span className="puntos">{texto}</span>
    </p>
  )
}

interface PropsError {
  mensaje: string
  alReintentar?: () => void
  children?: ReactNode
}

export function MensajeError({ mensaje, alReintentar, children }: PropsError) {
  return (
    <div role="alert" className="aviso-error">
      <p>{mensaje}</p>
      {children}
      {alReintentar && (
        <button type="button" className="boton boton-sec boton-chico mt-3" onClick={alReintentar}>
          Reintentar
        </button>
      )}
    </div>
  )
}

export function mensajeDe(error: unknown): string {
  return error instanceof Error && error.message ? error.message : 'Algo falló. Probá de nuevo en un rato.'
}
