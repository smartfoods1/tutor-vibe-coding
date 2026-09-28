# Desarrollo local

Cómo levantar el curso en tu compu para probarlo, cambiarlo y correr los tests. Con el modo demo no
hacen falta claves de API ni se gasta un peso.

Cloná el repo (o tu fork) y entrá a la carpeta:

```bash
git clone https://github.com/smartfoods1/tutor-vibe-coding.git tutor-vibe-coding
cd tutor-vibe-coding
```

Cada bloque de comandos de esta guía arranca desde esa carpeta, la raíz del repo, donde está
`README.md`. Si ya estás adentro de `backend/`, salteá el `cd backend`; en una terminal nueva,
primero entrá a la raíz del repo.

## Requisitos

| Qué | Versión | Para qué |
|---|---|---|
| Python | 3.12 | El backend (FastAPI). Con uv no hace falta instalarlo aparte: uv lo baja solo |
| [uv](https://docs.astral.sh/uv/) | cualquiera reciente | Crear el entorno de Python e instalar dependencias (también se puede con pip) |
| Node.js | 22.22.2 o más nuevo de la 22, 24.15 o más nuevo de la 24 (la que usa GitHub Actions), o 26 en adelante | El frontend (React con Vite) |
| ffmpeg | cualquiera reciente | Convertir audio: lo usan la voz del tutor y sus tests (en modo demo no hace falta) |
| git y curl | cualquiera | Clonar el repo y comprobar que el backend anda |

En Mac: `brew install uv node ffmpeg` (uv baja Python 3.12 solo, y `node` trae la versión más
nueva, que también anda). En Ubuntu: `sudo apt install ffmpeg`, más uv y Node desde sus páginas
oficiales (uv baja Python 3.12 solo). Si vas sin uv, `sudo apt install python3.12 python3.12-venv`
anda en Ubuntu 24.04; en 22.04 esos paquetes no están en los repositorios oficiales. En Windows
conviene usar WSL.

## 1. Backend

```bash
cd backend
uv venv --python 3.12 .venv
uv pip install --python .venv -e ".[dev]"
```

`--python .venv` hace que instale en `backend/.venv` aunque tengas otro entorno de Python activado
en la terminal. Sin uv: `python3.12 -m venv .venv && .venv/bin/pip install -e ".[dev]"`.

### Configuración local

El backend lee su configuración del archivo que indica `VIBE_ENV_FILE` (en el servidor es
`/etc/vibe-tutor/.env`). Para tu compu, creá `backend/.env.local`, que git ignora:

```bash
cd backend
cat > .env.local <<EOF
JWT_SECRET=$(openssl rand -hex 32)
ADMIN_EMAIL=vos@example.com
MAIL_FROM="Curso local <curso@example.com>"
DOMINIO=localhost:5173
DATA_DIR=./data
CONTENIDO_DIR=../contenido
TAREAS_ACTIVAS=false
DEV_CODIGO_FIJO=123456
MODO_DEMO=true
AUTOR_NOMBRE="Tu nombre"
EOF
```

Qué hace cada línea:

- `MODO_DEMO=true`: el tutor responde con un guion fijo sin llamar a Claude, la voz queda apagada,
  los mails no se mandan y no hacen falta claves de API. Por cada mail aparece en la terminal del
  backend una línea «modo demo: no se manda el mail…», y los del curso (no el del código) quedan
  anotados como enviados en la tabla `mails` de `backend/data/vibe.db`. Sirve para recorrer toda
  la web sin costo.
- `DEV_CODIGO_FIJO=123456`: entrás con ese código sin que se mande ningún mail. Solo vale cuando el
  pedido llega desde tu misma compu (localhost); igual, **nunca lo pongas en el servidor**.
- `ADMIN_EMAIL`: si entrás con ese mail, ves el panel de administración en `/admin`.
- `DOMINIO=localhost:5173`: la dirección del curso, sin https://. Va en los links del kit que bajás
  desde la web: con el puerto de Vite, esos links abren tu curso local.
- `DATA_DIR=./data`: la base SQLite queda en `backend/data/vibe.db` (git la ignora). Para empezar
  de cero, borrá esa carpeta.
- `TAREAS_ACTIVAS=false`: apaga la tarea periódica (recordatorios, avisos y borrado por
  retención), que en local no hace falta.

La lista completa de variables, con sus valores por defecto, está en
[deploy/.env.example](../deploy/.env.example).

### Arrancarlo

```bash
cd backend
VIBE_ENV_FILE=.env.local .venv/bin/uvicorn --factory vibe_tutor.main:crear_app --port 8000 --reload
```

Para comprobar que anda y que leyó tu configuración, en otra terminal:
`curl http://127.0.0.1:8000/api/config` devuelve un JSON con `"modo_demo":true`. No alcanza con
`/api/salud`: responde `{"ok":true}` aunque falte la configuración.

## 2. Frontend

En otra terminal:

```bash
cd frontend
npm ci
npm run dev
```

(`npm ci` instala exactamente lo de `package-lock.json`, igual que GitHub Actions; usá
`npm install` solo para sumar o actualizar dependencias.)

Abrí <http://localhost:5173>. Vite manda todo lo que empieza con `/api` al backend del puerto 8000.
Usá `localhost` (no la IP de tu red) y un navegador como Chrome o Firefox: la cookie de sesión es
`__Host-` y `Secure`, y esos navegadores la aceptan en localhost aunque no haya HTTPS.

Para probar con otro nombre de curso, copiá `frontend/.env.example` a `frontend/.env` (git lo
ignora), cambiá `VITE_NOMBRE_CURSO` y reiniciá `npm run dev`.

## 3. Recorrerlo

1. En la portada, inscribite con cualquier mail y aceptá los consentimientos obligatorios.
2. Cuando te pida el código, poné `123456`.
3. Hacé los módulos 1 a 3 con el tutor en modo demo: vas a ver el guion fijo, el avance y la idea
   en una página.
4. Entrá con el mail de `ADMIN_EMAIL` para ver `/admin` (embudo, gasto y datos vencidos del
   machete).

Los audios de los módulos no se ven en local: en el servidor los sirve nginx desde
`contenido/audios/`. Si no hay audio para un módulo, el módulo arranca sin él.

## 4. Probar con el tutor y la voz de verdad

Sacá `MODO_DEMO=true` (o ponelo en `false`) y sumá tus claves a `backend/.env.local`:

```bash
ANTHROPIC_API_KEY=...
GEMINI_API_KEY=...
RESEND_API_KEY=...
```

Después reiniciá el backend (Ctrl+C y el mismo comando de "Arrancarlo"): la configuración se lee
una sola vez al arrancar y `--reload` solo mira los archivos `.py`.

Esto sí tiene costo: rigen los mismos topes que en producción (`TOPE_ALUMNO_USD` y
`TOPE_MENSUAL_USD`); para probar, bajalos, por ejemplo a `0.2` y `2`. Fuera del modo demo el
backend exige las tres claves de API; si no querés mandar mails de verdad, poné cualquier texto en
`RESEND_API_KEY` (el envío falla, lo ves en la terminal del backend y con `DEV_CODIGO_FIJO` igual
entrás).

## 5. Armar un kit sin pasar por la web

```bash
cd backend
.venv/bin/python -m vibe_tutor.kit --idea ../contenido/ejemplos/kit-minimo/mi-idea.md \
    --herramienta codex --sistema mac --dominio localhost:5173 --salida .
```

Deja un `.zip` en `backend/` (git ignora los zip). `--herramienta` puede ser `codex` o `claude`, y
`--sistema`, `mac` o `windows`. Descomprimilo y abrí la carpeta en la app de escritorio de ChatGPT
(modo Codex) o de Claude (pestaña Code) para probar el tutor del kit.

## 6. Tests

Corrélos en una terminal libre, desde la raíz del repo (si el backend y Vite están andando, abrí
otra). Backend, que incluye los tests del contenido (esquema del machete, reglas de "gratis",
estructura y tamaño del kit):

```bash
cd backend
.venv/bin/pytest
```

Ningún test llama a servicios pagos: Claude, Gemini, Resend y Turnstile se simulan. La marca
`real` queda reservada para pruebas contra las APIs de verdad, que tienen costo, y hoy no hay
ninguna (`.venv/bin/pytest -m real` no corre nada). Si sumás una, no corre por defecto
(`pyproject.toml` la excluye) y se corre a mano con ese comando.

Frontend, de nuevo desde la raíz del repo:

```bash
cd frontend
npm test
npm run build
```

GitHub Actions corre las dos suites en cada push a `main` y en cada pull request
([.github/workflows/tests.yml](../.github/workflows/tests.yml)), sin secretos ni llamadas pagas.
En un fork, GitHub deja las Actions apagadas hasta que las habilitás en la pestaña Actions de tu
repo.

## Problemas comunes

- **`/api/config` devuelve `Internal Server Error`** (el backend arranca igual, pero al arrancar el
  registro dice "no se pudo leer la configuración" y `Field required` junto al nombre de la
  variable): revisá que `VIBE_ENV_FILE` apunte a tu `.env.local` y que `JWT_SECRET` tenga al menos
  32 caracteres.
- **Cambié `.env.local` y no pasó nada**: reiniciá el backend. La configuración se lee al arrancar.
- **El código 123456 no funciona**: entrá por `http://localhost:5173`, no por la IP de tu red, y
  revisá que `DEV_CODIGO_FIJO` esté en el archivo que lee el backend.
- **Entrás pero la sesión no queda**: probá con Chrome o Firefox (ver arriba lo de la cookie).
- **Fallan los tests de voz**: falta ffmpeg en el PATH.
