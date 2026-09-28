/// <reference types="vitest/config" />
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'
import { nombreCurso } from './src/lib/nombre.ts'

export default defineConfig(({ mode }) => {
  // El nombre del curso sale de VITE_NOMBRE_CURSO (frontend/.env, ver .env.example). Con define le
  // llega ya limpio a la app (import.meta.env) y a index.html, donde Vite reemplaza %VITE_NOMBRE_CURSO%.
  const env = loadEnv(mode, process.cwd(), 'VITE_')
  const nombre = nombreCurso(env.VITE_NOMBRE_CURSO)
  // El que aparece debajo del ícono en el celular: conviene que tenga 12 letras o menos.
  const nombreCorto = env.VITE_NOMBRE_CORTO?.trim() || 'Vibe coding'

  return {
    define: {
      'import.meta.env.VITE_NOMBRE_CURSO': JSON.stringify(nombre),
    },
    plugins: [
      react(),
      tailwindcss(),
      VitePWA({
        registerType: 'autoUpdate',
        // El registro del service worker va en un archivo (registerSW.js), nunca en un script en línea:
        // la CSP del sitio es "script-src 'self'".
        injectRegister: 'script',
        includeAssets: ['favicon.svg', 'apple-touch-icon.png'],
        manifest: {
          name: nombre,
          short_name: nombreCorto,
          description: 'De lo que imaginás a algo que existe.',
          lang: 'es-AR',
          start_url: '/inicio',
          scope: '/',
          display: 'standalone',
          // Los mismos colores que --color-papel y --color-oro de src/index.css (y theme-color de index.html).
          background_color: '#EDE6D6',
          theme_color: '#E4BC5C',
          icons: [
            { src: '/icono-192.png', sizes: '192x192', type: 'image/png' },
            { src: '/icono-512.png', sizes: '512x512', type: 'image/png' },
            { src: '/icono-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
          ],
        },
        workbox: {
          // Cada despliegue toma el control enseguida: si no, la versión nueva espera a que se cierren
          // todas las pestañas y un alumno con el curso abierto se queda con la vieja.
          skipWaiting: true,
          clientsClaim: true,
          cleanupOutdatedCaches: true,
          navigateFallback: '/index.html',
          // La API (incluida la página de baja) y los audios siempre van a la red.
          navigateFallbackDenylist: [/^\/api\//, /^\/audios\//],
          // Las fuentes (woff2, del propio sitio) no se precachean: hay una por alfabeto y el navegador
          // baja solo las que usa la página.
          globPatterns: ['**/*.{js,css,html,svg,png,webmanifest}'],
        },
      }),
    ],
    server: {
      proxy: { '/api': 'http://127.0.0.1:8000' },
    },
    test: {
      environment: 'jsdom',
      setupFiles: ['./tests/setup.ts'],
      include: ['tests/**/*.test.{ts,tsx}'],
    },
  }
})
