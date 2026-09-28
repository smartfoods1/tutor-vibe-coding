import { Link } from 'react-router-dom'
import { Cargando, MensajeError, mensajeDe } from '../componentes/Estados.tsx'
import Pagina from '../componentes/Pagina.tsx'
import { api } from '../lib/api.ts'
import { useCarga } from '../lib/useCarga.ts'
import { esLinkSeguro } from '../lib/validar.ts'

function nombreDe(url: string): string {
  try {
    return new URL(url).hostname
  } catch {
    return url
  }
}

export default function Galeria() {
  const { datos, error, cargando, recargar } = useCarga(() => api.galeria())
  const links = (Array.isArray(datos) ? datos : []).filter((l) => esLinkSeguro(l?.url))

  return (
    <Pagina titulo="Galería" navegacion="publica">
      <h1 className="text-[2rem] font-bold">Galería</h1>
      <p className="mt-4">Páginas que hicieron personas del curso y que eligieron mostrar.</p>

      {cargando ? (
        <Cargando />
      ) : error && !datos ? (
        <div className="mt-6">
          <MensajeError mensaje={mensajeDe(error)} alReintentar={() => void recargar()} />
        </div>
      ) : links.length === 0 ? (
        <p className="aviso mt-6">Todavía no hay páginas para mostrar.</p>
      ) : (
        <ul aria-label="Páginas de alumnos" className="mt-6 divide-y divide-linea border-y border-linea">
          {links.map((l) => (
            <li key={l.url} className="py-4">
              <a
                href={l.url}
                target="_blank"
                rel="noopener noreferrer nofollow ugc"
                className="enlace text-[1.1rem]"
              >
                {l.titulo?.trim() || nombreDe(l.url)}
              </a>
              <p className="break-all text-marron">{nombreDe(l.url)}</p>
            </li>
          ))}
        </ul>
      )}

      <p className="mt-10">
        ¿Querés hacer la tuya?{' '}
        <Link to="/" className="enlace">
          Conocé el curso
        </Link>
      </p>
    </Pagina>
  )
}
