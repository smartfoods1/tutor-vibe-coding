import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ErrorApi, api } from '../lib/api.ts'
import { useCarga } from '../lib/useCarga.ts'
import { Cargando, MensajeError, mensajeDe } from './Estados.tsx'
import TextoMd from './TextoMd.tsx'

interface Props {
  modulo: number
  /** Muestra "Ya lo hice", que marca el módulo como hecho con la guía escrita. */
  conYaLoHice?: boolean
  alCompletar?: (moduloActual: number) => void
}

export default function GuiaEscrita({ modulo, conYaLoHice = true, alCompletar }: Props) {
  const { datos: guia, error, cargando, recargar } = useCarga(() => api.guia(modulo), [modulo])
  const [marcando, setMarcando] = useState(false)
  const [falla, setFalla] = useState<{ mensaje: string; faltaIdea: boolean } | null>(null)
  const [listo, setListo] = useState<number | null>(null)

  async function yaLoHice() {
    setFalla(null)
    setMarcando(true)
    try {
      const respuesta = await api.completar(modulo)
      const actual = typeof respuesta?.modulo_actual === 'number' ? respuesta.modulo_actual : modulo + 1
      setListo(actual)
      alCompletar?.(actual)
    } catch (e) {
      setFalla({ mensaje: mensajeDe(e), faltaIdea: e instanceof ErrorApi && e.status === 409 && modulo === 2 })
    } finally {
      setMarcando(false)
    }
  }

  return (
    <section aria-labelledby={`guia-${modulo}`} className="tarjeta mt-6">
      <p className="etiqueta">Guía escrita</p>
      {cargando ? (
        <Cargando />
      ) : !guia ? (
        <MensajeError mensaje={mensajeDe(error)} alReintentar={() => void recargar()} />
      ) : (
        <>
          <h2 id={`guia-${modulo}`} className="mt-2 text-[1.5rem] font-bold">
            {guia.titulo}
          </h2>
          <div className="mt-4">
            <TextoMd texto={guia.guia_md} bajarTitulos />
          </div>
        </>
      )}

      {conYaLoHice && guia && listo === null && (
        <div className="mt-6 border-t border-linea pt-5">
          <p>Cuando hayas hecho lo que dice la guía, marcalo acá.</p>
          {falla && (
            <div className="mt-3">
              <MensajeError mensaje={falla.mensaje}>
                {falla.faltaIdea && (
                  <Link to="/mi-idea" className="enlace mt-2 inline-block text-tinta">
                    Escribir mi idea
                  </Link>
                )}
              </MensajeError>
            </div>
          )}
          <button type="button" className="boton mt-3 w-full" onClick={() => void yaLoHice()} disabled={marcando}>
            {marcando ? 'Guardando…' : 'Ya lo hice'}
          </button>
        </div>
      )}

      {listo !== null && (
        <div role="status" className="aviso aviso-logro mt-6">
          <p className="font-semibold">Terminaste el módulo {modulo}.</p>
          {modulo === 3 && listo <= 3 ? (
            <>
              <p className="mt-2">Te falta un paso: bajar tu kit, la carpeta con la que seguís el curso.</p>
              <a href="#kit" className="boton mt-3 w-full">
                Bajar tu kit
              </a>
            </>
          ) : listo > modulo && listo <= 3 ? (
            <Link to={`/modulo/${listo}`} className="boton mt-3 w-full">
              Seguir con el módulo {listo}
            </Link>
          ) : (
            <Link to="/inicio" className="boton mt-3 w-full">
              Volver al inicio
            </Link>
          )}
        </div>
      )}
    </section>
  )
}
