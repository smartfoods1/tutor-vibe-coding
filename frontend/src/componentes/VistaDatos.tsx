/** Muestra un JSON cualquiera (el reporte de admin) como listas y tablas legibles. */

const NUMERO = new Intl.NumberFormat('es-AR', { maximumFractionDigits: 2 })
const DINERO = new Intl.NumberFormat('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const ACENTOS: Record<string, string> = {
  modulo: 'módulo',
  modulos: 'módulos',
  ultimos: 'últimos',
  ultimo: 'último',
  dias: 'días',
  dia: 'día',
  version: 'versión',
  verificacion: 'verificación',
  inscripcion: 'inscripción',
  guia: 'guía',
  galeria: 'galería',
}

export function etiquetaDe(clave: string): string {
  const texto = clave
    .replace(/_usd$/i, '')
    .split('_')
    .map((palabra) => ACENTOS[palabra.toLowerCase()] ?? palabra)
    .join(' ')
    .trim()
  return texto.charAt(0).toUpperCase() + texto.slice(1)
}

function esDinero(clave: string): boolean {
  return /(^|_)(usd|costo|gasto|tope)(_|$)/i.test(clave)
}

function valorPlano(clave: string, valor: unknown): string {
  if (valor === null || valor === undefined) return '—'
  if (typeof valor === 'boolean') return valor ? 'Sí' : 'No'
  if (typeof valor === 'number') return esDinero(clave) ? `US$ ${DINERO.format(valor)}` : NUMERO.format(valor)
  return String(valor)
}

function esPlano(valor: unknown): boolean {
  return valor === null || typeof valor !== 'object'
}

function Tabla({ filas }: { filas: Record<string, unknown>[] }) {
  const columnas = Array.from(new Set(filas.flatMap((f) => Object.keys(f))))
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-left">
        <thead>
          <tr>
            {columnas.map((c) => (
              <th key={c} scope="col" className="border-b-2 border-tinta px-2 py-1 font-semibold">
                {etiquetaDe(c)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filas.map((fila, i) => (
            <tr key={i} className="border-b border-linea">
              {columnas.map((c) => (
                <td key={c} className="px-2 py-1 align-top">
                  {esPlano(fila[c]) ? valorPlano(c, fila[c]) : JSON.stringify(fila[c])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function VistaDatos({ datos, clave = '' }: { datos: unknown; clave?: string }) {
  if (esPlano(datos)) return <span>{valorPlano(clave, datos)}</span>
  if (Array.isArray(datos)) {
    if (datos.length === 0) return <span className="text-marron">Nada por ahora</span>
    if (datos.every((d) => d && typeof d === 'object' && !Array.isArray(d))) {
      return <Tabla filas={datos as Record<string, unknown>[]} />
    }
    return (
      <ul className="list-disc pl-6">
        {datos.map((d, i) => (
          <li key={i}>
            <VistaDatos datos={d} clave={clave} />
          </li>
        ))}
      </ul>
    )
  }
  const entradas = Object.entries(datos as Record<string, unknown>)
  return (
    <dl className="divide-y divide-linea">
      {entradas.map(([k, v]) => (
        <div key={k} className={esPlano(v) ? 'flex justify-between gap-4 py-2' : 'py-3'}>
          <dt className={esPlano(v) ? '' : 'mb-2 font-semibold'}>{etiquetaDe(k)}</dt>
          <dd className={esPlano(v) ? 'text-right font-semibold' : 'pl-3'}>
            <VistaDatos datos={v} clave={k} />
          </dd>
        </div>
      ))}
    </dl>
  )
}
