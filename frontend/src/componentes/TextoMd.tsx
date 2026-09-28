import { lazy, Suspense } from 'react'
import { Barrera } from './Barrera.tsx'

const Markdown = lazy(() => import('./Markdown.tsx'))

interface Props {
  texto: string
  bajarTitulos?: boolean
}

/** Markdown cargado aparte (la portada no lo necesita); mientras carga, o si no carga, se ve el texto tal cual. */
export default function TextoMd({ texto, bajarTitulos }: Props) {
  const plano = <div className="prosa whitespace-pre-wrap">{texto}</div>
  return (
    <Barrera fallback={plano}>
      <Suspense fallback={plano}>
        <Markdown texto={texto} bajarTitulos={bajarTitulos} />
      </Suspense>
    </Barrera>
  )
}
