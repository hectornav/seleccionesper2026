# 🗳️ Elecciones Perú 2026

Plataforma ciudadana para informarse sobre los candidatos presidenciales y votar con conocimiento.

## Características

- 📋 **Perfiles de candidatos** — Biografía, experiencia y posición política
- 📊 **Comparador** — Compara hasta 3 candidatos lado a lado
- ⚡ **Test Electoral** — Descubre qué candidato se alinea con tus ideas
- 🔍 **Filtros** — Busca por nombre, partido o posición política

## Instalación y uso

```bash
# 1. Clonar / entrar al directorio
cd eleccionesper2026

# 2. Activar entorno virtual
source venv/bin/activate   # Linux/Mac
# .\venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. Cargar datos de ejemplo
python manage.py seed_data

# 6. Crear superusuario (opcional)
python manage.py createsuperuser

# 7. Ejecutar servidor
python manage.py runserver
```

Abrir en el navegador: **http://127.0.0.1:8000**

Panel de admin: **http://127.0.0.1:8000/admin** (admin / admin2026)

## Tecnologías

- Python + Django 6
- Bootstrap 5 + Bootstrap Icons
- SQLite (base de datos ligera)
- Vanilla JavaScript

## Aviso

Esta plataforma es de carácter **informativo y educativo**. No tiene afiliación política con ningún candidato o partido.
