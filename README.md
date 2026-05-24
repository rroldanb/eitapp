# eitapp


# 🚦 Transit App - Gestión de Proyectos de Tráfico

Backend Django para gestión de proyectos de ingeniería de transporte y análisis de tráfico.

## 📋 Características

- **Mandantes**: Gestión de clientes/organizaciones
- **Proyectos**: Creación y seguimiento de proyectos de tráfico
- **Red Vial**: Modelo de red (calles, nodos, arcos, movimientos)
- **Tráfico**: Conteos vehiculares, flujos, períodos
- **Usuarios**: Autenticación y permisos

## 🛠️ Tech Stack

- Django 4.2+
- SQLite (dev) / PostgreSQL (prod)
- HTMX para interactividad
- WhiteNoise para static files
- dotenv para configuración

## 🚀 Inicio Rápido

```bash
# Clonar y crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno
cp .env.example .env

# Migraciones
python manage.py migrate

# Crear superuser
python manage.py createsuperuser

# Ejecutar
python manage.py runserver
```

## 📁 Estructura de Apps

| App | Descripción | Estado |
|-----|-------------|--------|
| mandantes | Clientes y contactos | ✅ |
| proyectos | Proyectos de tráfico | 🟡 |
| red_vial | Red vial, nodos, arcos | 🟡 |
| trafico | Conteos y flujos | 🟡 |
| usuarios | Auth y perfiles | ⚠️ |
| tasks | Demo (eliminar) | ⚠️ |

## 🌐 URLs Principales

- `/` - Dashboard
- `/mandantes/` - Clientes
- `/proyectos/` - Proyectos
- `/proyectos/<id>/red-vial/` - Red vial del proyecto
- `/signin/` - Iniciar sesión
- `/signup/` - Registrarse

## 📝 Variables de Entorno

```
SECRET_KEY=...
DEBUG=True
DATABASE_URL=...
```

## 📄 Licencia

MIT
```

---

