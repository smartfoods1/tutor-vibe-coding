import type { Alcance } from '../lib/api.ts'

/** Cuando el tutor llega a un tope, el curso sigue con la guía escrita y sin perder el avance. */
export default function AvisoTope({ alcance }: { alcance: Alcance }) {
  return (
    <div role="status" className="aviso mt-6">
      <p className="font-semibold">
        {alcance === 'mes'
          ? 'El tutor llegó a su límite de uso este mes.'
          : 'Llegaste al límite de conversación con el tutor que tiene cada persona del curso.'}
      </p>
      <p className="mt-2">
        Tu avance está guardado. Seguí con la guía escrita de abajo: tiene lo mismo, paso a paso.
        {alcance === 'mes' ? ' El tutor vuelve a estar disponible el mes que viene.' : ''}
      </p>
    </div>
  )
}
