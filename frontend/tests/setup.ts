import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Sin globals de vitest, Testing Library no desmonta solo entre tests.
afterEach(() => cleanup())

// jsdom no implementa scrollTo y lo avisa por consola en cada navegación.
window.scrollTo = (() => undefined) as typeof window.scrollTo

// Las páginas se cargan de forma diferida (lazy): con la máquina ocupada, 1 s no siempre alcanza.
import { configure } from '@testing-library/react'
configure({ asyncUtilTimeout: 5000 })
