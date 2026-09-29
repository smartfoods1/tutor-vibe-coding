import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import AvisoTope from '../componentes/AvisoTope.tsx'
import Chat from '../componentes/Chat.tsx'
import { useConfig } from '../componentes/Configuracion.tsx'
import { Cargando, MensajeError, mensajeDe } from '../componentes/Estados.tsx'
import GuiaEscrita from '../componentes/GuiaEscrita.tsx'
import Pagina from '../componentes/Pagina.tsx'
import PedidoPendiente from '../componentes/PedidoPendiente.tsx'
import Reproductor from '../componentes/Reproductor.tsx'
import Taller from '../componentes/Taller.tsx'
import { api, cuentaPendiente, type Alcance, type Yo } from '../lib/api.ts'
import { TITULOS_MODULOS } from '../lib/marca.ts'
import { useCarga } from '../lib/useCarga.ts'
import NoEncontrada from './NoEncontrada.tsx'

/**
 * Un módulo está terminado si figura en el avance. En el 1 y el 2 también si ya se pasó al siguiente;
 * en el 3 no: al 4 se pasa bajando el kit, y eso puede pasar a mitad del módulo.
 */
export function moduloTerminado(yo: Yo, modulo: number): boolean {
  if (yo.avance.some((a) => a.modulo === modulo)) return true
  return modulo < 3 && modulo < yo.modulo_actual
}

export default function Modulo() {
  const { n } = useParams()
  const modulo = Number(n)
  if (!Number.isInteger(modulo) || modulo < 1 || modulo > 3) return <NoEncontrada />
  return <VistaModulo key={modulo} modulo={modulo} />
}

function VistaModulo({ modulo }: { modulo: number }) {
  const { autorNombre, modoDemo } = useConfig()
  const { datos: yo, error, cargando, recargar } = useCarga(() => api.yo())
  const [tope, setTope] = useState<Alcance | null>(null)
  const [verGuia, setVerGuia] = useState(false)
  // En un módulo ya terminado el chat se abre solo si la persona lo pide (el saludo cuesta).
  const [conversar, setConversar] = useState<boolean | null>(null)
  const titulo = TITULOS_MODULOS[modulo]

  const encabezado = (
    <>
      <p className="etiqueta">Módulo {modulo} de 7</p>
      <h1 className="mt-1 text-[2rem] font-bold">{titulo}</h1>
    </>
  )

  if (cargando) {
    return (
      <Pagina titulo={`Módulo ${modulo}`} navegacion="privada">
        {encabezado}
        <Cargando />
      </Pagina>
    )
  }
  if (!yo) {
    return (
      <Pagina titulo={`Módulo ${modulo}`} navegacion="privada">
        {encabezado}
        <div className="mt-6">
          <MensajeError mensaje={mensajeDe(error)} alReintentar={() => void recargar()} />
        </div>
      </Pagina>
    )
  }

  // Sin aprobar no se abre el tutor (ni se gasta el saludo).
  if (cuentaPendiente(yo)) return <PedidoPendiente email={yo.email} />

  if (modulo > yo.modulo_actual) {
    return (
      <Pagina titulo={`Módulo ${modulo}`} navegacion="privada">
        {encabezado}
        <div className="aviso mt-6">
          <p>Este módulo se abre cuando termines el módulo {yo.modulo_actual}.</p>
          <Link to={`/modulo/${yo.modulo_actual}`} className="boton mt-4 w-full">
            Ir al módulo {yo.modulo_actual}
          </Link>
        </div>
      </Pagina>
    )
  }

  const bloqueado: Alcance | null = tope ?? (yo.tope.bloqueado ? (yo.tope.alcance ?? 'alumno') : null)
  const terminado = moduloTerminado(yo, modulo)
  const conChat = conversar ?? !terminado
  const audio = yo.audios?.find((a) => a.modulo === modulo)
  // En el 3, "ya lo hice" deja registrado el módulo; al 4 se pasa recién bajando el kit.
  const conYaLoHice = !terminado
  const faltaKit = modulo === 3 && yo.modulo_actual <= 3

  return (
    <Pagina titulo={`Módulo ${modulo}`} navegacion="privada">
      {encabezado}

      {terminado && (
        <div className="aviso aviso-logro mt-6">
          {faltaKit ? (
            <>
              <p>Ya terminaste este módulo. Te falta bajar tu kit para seguir en tu computadora.</p>
              <a href="#kit" className="enlace mt-2 inline-block">
                Bajar tu kit
              </a>
            </>
          ) : (
            <>
              <p>Ya terminaste este módulo. Podés volver a conversar o seguir adelante.</p>
              <Link
                to={yo.modulo_actual <= 3 ? `/modulo/${yo.modulo_actual}` : '/inicio'}
                className="enlace mt-2 inline-block"
              >
                {yo.modulo_actual <= 3 ? `Ir al módulo ${yo.modulo_actual}` : 'Volver al inicio'}
              </Link>
            </>
          )}
        </div>
      )}

      {audio && <Reproductor audio={audio} />}

      {modulo === 3 && (
        <p className="mt-6">
          Este módulo conviene hacerlo desde la computadora que vas a usar. Si te trabás al instalar, mandale al tutor
          una captura de la pantalla (o una foto hecha con el celular).
        </p>
      )}

      {bloqueado ? (
        <>
          <AvisoTope alcance={bloqueado} />
          <GuiaEscrita modulo={modulo} conYaLoHice={conYaLoHice} alCompletar={() => void recargar()} />
        </>
      ) : (
        <>
          {conChat ? (
            <>
              {/* En modo demo no hay voz: no se ofrece Escuchar. */}
              {!modoDemo && (
                <p className="mt-6 text-marron">
                  El tutor escribe. Si preferís escucharlo, tocá Escuchar debajo de cada mensaje: es una voz sintética,{' '}
                  {autorNombre ? `no la de ${autorNombre}` : 'no la del autor del curso'}.
                </p>
              )}
              <Chat
                modulo={modulo}
                conCaptura={modulo === 3}
                ideaAlAbrir={modulo === 2 && !terminado ? (yo.idea?.version ?? null) : null}
                alTope={setTope}
                alAvance={() => {
                  // El chat sigue a la vista: el tutor todavía escribe su cierre.
                  setConversar(true)
                  void recargar()
                }}
                alTaller={() => void recargar()}
              />
            </>
          ) : (
            <button type="button" className="boton boton-sec mt-6 w-full" onClick={() => setConversar(true)}>
              Volver a conversar con el tutor
            </button>
          )}
          <div className="mt-8">
            <button
              type="button"
              className="enlace"
              aria-expanded={verGuia}
              onClick={() => setVerGuia((v) => !v)}
            >
              {verGuia ? 'Ocultar la guía escrita' : 'Prefiero leer la guía escrita'}
            </button>
            {verGuia && (
              <GuiaEscrita modulo={modulo} conYaLoHice={conYaLoHice} alCompletar={() => void recargar()} />
            )}
          </div>
        </>
      )}

      {modulo === 3 && <Taller yo={yo} alCambiar={() => void recargar()} />}
    </Pagina>
  )
}
