import ReactMarkdown, { type Components } from 'react-markdown'

interface Props {
  texto: string
  /** Baja un nivel los títulos (# pasa a h2), para no competir con el título de la página. */
  bajarTitulos?: boolean
}

const enlaces: Components = {
  a: ({ node: _node, ...props }) => <a {...props} target="_blank" rel="noopener noreferrer" />,
  // Las imágenes no se cargan nunca: una imagen de otro sitio avisa a ese sitio quién la abrió (y
  // en su dirección puede llevarse datos). Queda solo su texto alternativo, entre corchetes.
  img: ({ alt }) => (alt ? <span>[{alt}]</span> : null),
}

const bajados: Components = {
  ...enlaces,
  h1: ({ node: _node, ...props }) => <h2 {...props} />,
  h2: ({ node: _node, ...props }) => <h3 {...props} />,
  h3: ({ node: _node, ...props }) => <h4 {...props} />,
}

/** Markdown sin HTML crudo ni imágenes (react-markdown ya sanea los links peligrosos). */
export default function Markdown({ texto, bajarTitulos = false }: Props) {
  return (
    <div className="prosa">
      <ReactMarkdown skipHtml components={bajarTitulos ? bajados : enlaces}>
        {texto}
      </ReactMarkdown>
    </div>
  )
}
