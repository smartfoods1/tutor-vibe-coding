/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** El nombre del curso (ver frontend/.env.example). vite.config.ts le pone el valor por defecto. */
  readonly VITE_NOMBRE_CURSO?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
