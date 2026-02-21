# Guía de Despliegue en PythonAnywhere

Sigue estos pasos para desplegar tu proyecto (Elecciones Perú 2026) en una cuenta de [PythonAnywhere](https://www.pythonanywhere.com/).

## 1. Crear tu cuenta y abrir una consola

1. Crea una cuenta gratuita (Beginner) o de pago.
2. Ve a la pestaña **Consoles** y abre una nueva **Bash console**.

## 2. Clonar el repositorio y configurar el entorno

Dentro de la consola bash de PythonAnywhere, ejecuta los siguientes comandos:

```bash
# Sube o clona tu proyecto aquí:
# git clone <tu-repositorio-url> eleccionesper2026
# cd eleccionesper2026

# Crear y activar entorno virtual
mkvirtualenv --python=python3.10 mi-entorno-venv
# (O usa: python -m venv venv && source venv/bin/activate)

# Instalar dependencias
pip install -r requirements.txt
```

## 3. Configurar variables de entorno (`.env`)

Dentro de la carpeta de tu proyecto (donde está `manage.py`), crea tu archivo `.env`:

```bash
nano .env
```

Pega el siguiente contenido (puedes cambiar los valores después):

```env
SECRET_KEY=coloca_aqui_una_clave_larga_y_segura
DEBUG=False
ALLOWED_HOSTS=tu_usuario.pythonanywhere.com
# Si no usas postgresql, ignora la de DATABASE_URL y usará local sqlite!
```

Guarda presionando `Ctrl + O`, `Enter` y sal con `Ctrl + X`.

## 4. Migraciones y Archivos Estáticos

Continúa en la consola y ejecuta:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## 5. Configurar el Web App en PythonAnywhere

1. Ve a la pestaña **Web** en PythonAnywhere.
2. Da click en **"Add a new web app"**.
3. Elige tu dominio (ej: `tu_usuario.pythonanywhere.com`), dale a **Next**.
4. Selecciona **Manual configuration (including virtualenvs)** y luego la versión de Python que usaste (ej: Python 3.10).
5. Sigue a **Next** hasta que finalice.

### Configurando rutas en la pestaña Web

En tu nueva Web App, desliza hacia abajo hasta:

1. **Virtualenv**: Coloca la ruta de tu entorno virtual.
   - Si usaste `mkvirtualenv`, pon: `/home/tu_usuario/.virtualenvs/mi-entorno-venv`
   - Si creaste `./venv`, pon: `/home/tu_usuario/eleccionesper2026/venv`
2. **Source code**: Coloca `/home/tu_usuario/eleccionesper2026`

### Configurando Archivos Estáticos

Más abajo en la sección **Static Files**, añade un mapeo para que PythonAnywhere sirva tus estáticos eficientemente:
- **URL**: `/static/`
- **Directory**: `/home/tu_usuario/eleccionesper2026/staticfiles`

## 6. Configurar el WSGI file

En el apartado **Code** de tu pestaña Web, dale click al archivo bajo **WSGI configuration file**.

Borra todo su contenido y pega el siguiente código:

```python
import os
import sys

# Ruta donde está tu proyecto (ajusta 'tu_usuario' y 'eleccionesper2026' si es distinto)
path = '/home/tu_usuario/eleccionesper2026'
if path not in sys.path:
    sys.path.append(path)

# Variables de entorno
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

# Configuración de Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Guarda los cambios de ese archivo (botón "Save").

## 7. ¡Recargar y Listo!

Regresa a la pestaña **Web** y haz click en el botón verde grande que dice **"Reload tu_usuario.pythonanywhere.com"**.

Entra a tu url (`http://tu_usuario.pythonanywhere.com`) y pruébalo.

---
**Nota sobre SSL**: 
En PythonAnywhere el soporte de certificado temporal HTTPS ("Force HTTPS") lo puedes activar en la misma pestaña **Web** scrolleando hasta "Security". Así tu tráfico irá cifrado igual que en DigitalOcean.
