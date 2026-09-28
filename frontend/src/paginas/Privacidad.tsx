import { Cargando, MensajeError, mensajeDe } from '../componentes/Estados.tsx'
import Pagina from '../componentes/Pagina.tsx'
import TextoMd from '../componentes/TextoMd.tsx'
import { api } from '../lib/api.ts'
import { useCarga } from '../lib/useCarga.ts'

export default function Privacidad() {
  const { datos, error, cargando, recargar } = useCarga(() => api.privacidad())

  return (
    <Pagina titulo="Privacidad" navegacion="publica">
      {cargando ? (
        <Cargando />
      ) : !datos ? (
        <>
          <h1 className="text-[2rem] font-bold">Privacidad</h1>
          <div className="mt-6">
            <MensajeError mensaje={mensajeDe(error)} alReintentar={() => void recargar()} />
          </div>
        </>
      ) : (
        <>
          <h1 className="text-[2rem] font-bold">{datos.titulo || 'Privacidad'}</h1>
          {datos.version && <p className="mt-2 text-marron">Versión {datos.version}</p>}
          <div className="mt-6">
            <TextoMd texto={datos.texto_md} bajarTitulos />
          </div>
        </>
      )}
    </Pagina>
  )
}
