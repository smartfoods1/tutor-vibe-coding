import { Link } from 'react-router-dom'
import Pagina from '../componentes/Pagina.tsx'

export default function NoEncontrada() {
  return (
    <Pagina titulo="Página no encontrada">
      <h1 className="text-[2rem] font-bold">No encontramos esta página</h1>
      <p className="mt-4">Puede que el link esté incompleto.</p>
      <Link to="/" className="boton mt-6 w-full sm:w-auto">
        Ir al principio
      </Link>
    </Pagina>
  )
}
