import { useCallback, useEffect, useRef, useState, type DependencyList } from 'react'

interface Estado<T> {
  datos: T | null
  error: Error | null
  cargando: boolean
}

/**
 * Carga datos al montar. recargar() no borra lo que ya había (así no se desmonta nada mientras
 * se actualiza) y descarta respuestas viejas si hubo otra carga después.
 */
export function useCarga<T>(cargar: () => Promise<T>, dependencias: DependencyList = []) {
  const [estado, setEstado] = useState<Estado<T>>({ datos: null, error: null, cargando: true })
  const vigente = useRef(0)

  const recargar = useCallback(async () => {
    const turno = ++vigente.current
    try {
      const datos = await cargar()
      if (turno === vigente.current) setEstado({ datos, error: null, cargando: false })
    } catch (error) {
      if (turno === vigente.current) {
        setEstado((previo) => ({
          datos: previo.datos,
          error: error instanceof Error ? error : new Error(String(error)),
          cargando: false,
        }))
      }
    }
  }, dependencias)

  useEffect(() => {
    void recargar()
  }, [recargar])

  const poner = useCallback((datos: T) => {
    vigente.current++
    setEstado({ datos, error: null, cargando: false })
  }, [])

  return { ...estado, recargar, poner }
}
