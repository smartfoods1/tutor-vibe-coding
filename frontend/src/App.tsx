import { Suspense, useLayoutEffect, useRef } from 'react'
import { Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { Barrera, lazyConRecarga } from './componentes/Barrera.tsx'
import { AvisoDemo, AvisoPrueba, ProveedorConfig } from './componentes/Configuracion.tsx'
import { Cargando } from './componentes/Estados.tsx'
import { alNoAutorizado, alPendiente } from './lib/api.ts'
import Entrar from './paginas/Entrar.tsx'
import Landing from './paginas/Landing.tsx'
import NoEncontrada from './paginas/NoEncontrada.tsx'

const Inicio = lazyConRecarga(() => import('./paginas/Inicio.tsx'))
const Modulo = lazyConRecarga(() => import('./paginas/Modulo.tsx'))
const MiIdea = lazyConRecarga(() => import('./paginas/MiIdea.tsx'))
const Mostrar = lazyConRecarga(() => import('./paginas/Mostrar.tsx'))
const Galeria = lazyConRecarga(() => import('./paginas/Galeria.tsx'))
const Privacidad = lazyConRecarga(() => import('./paginas/Privacidad.tsx'))
const MisDatos = lazyConRecarga(() => import('./paginas/MisDatos.tsx'))
const Baja = lazyConRecarga(() => import('./paginas/Baja.tsx'))
const Admin = lazyConRecarga(() => import('./paginas/Admin.tsx'))
const Pendiente = lazyConRecarga(() => import('./paginas/Pendiente.tsx'))

/** Las páginas que una cuenta pendiente sí puede usar: ahí un 403 de pendiente no la saca. */
const PERMITIDAS_PENDIENTE = new Set(['/pendiente', '/mis-datos'])

/** Al cambiar de página se vuelve arriba (en el celular, si no, se queda a mitad de pantalla). */
function SubirAlCambiar() {
  const { pathname } = useLocation()
  useLayoutEffect(() => {
    if (typeof window.scrollTo === 'function') window.scrollTo(0, 0)
  }, [pathname])
  return null
}

/** Un 401 en cualquier pedido privado lleva a /entrar y, al entrar, vuelve a donde estaba. */
function RedirigirSinSesion() {
  const navigate = useNavigate()
  const location = useLocation()
  const ruta = useRef(location.pathname)
  ruta.current = location.pathname

  useLayoutEffect(() => {
    alNoAutorizado(() => {
      if (ruta.current === '/entrar') return
      navigate('/entrar', { state: { desde: ruta.current } })
    })
    return () => alNoAutorizado(null)
  }, [navigate])

  return null
}

/** Un 403 de cuenta pendiente en cualquier pedido lleva a la pantalla del pedido de acceso. */
function RedirigirPendiente() {
  const navigate = useNavigate()
  const location = useLocation()
  const ruta = useRef(location.pathname)
  ruta.current = location.pathname

  useLayoutEffect(() => {
    alPendiente(() => {
      if (PERMITIDAS_PENDIENTE.has(ruta.current)) return
      navigate('/pendiente', { replace: true })
    })
    return () => alPendiente(null)
  }, [navigate])

  return null
}

function Rutas() {
  const { pathname } = useLocation()
  return (
    <Barrera key={pathname}>
      <Suspense
        fallback={
          <div className="mx-auto max-w-2xl px-4">
            <Cargando />
          </div>
        }
      >
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/entrar" element={<Entrar />} />
          <Route path="/inicio" element={<Inicio />} />
          <Route path="/modulo/:n" element={<Modulo />} />
          <Route path="/mi-idea" element={<MiIdea />} />
          <Route path="/mostrar" element={<Mostrar />} />
          <Route path="/galeria" element={<Galeria />} />
          <Route path="/privacidad" element={<Privacidad />} />
          <Route path="/mis-datos" element={<MisDatos />} />
          <Route path="/baja" element={<Baja />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/pendiente" element={<Pendiente />} />
          <Route path="*" element={<NoEncontrada />} />
        </Routes>
      </Suspense>
    </Barrera>
  )
}

export default function App() {
  return (
    <ProveedorConfig>
      <RedirigirSinSesion />
      <RedirigirPendiente />
      <SubirAlCambiar />
      <AvisoPrueba />
      <AvisoDemo />
      <Rutas />
    </ProveedorConfig>
  )
}
