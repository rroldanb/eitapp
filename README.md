# EIT App — Gestión de Proyectos de Ingeniería de Transporte

> 🇪🇸 Español · 🇺🇸 [English](README.en.md) · 🇧🇷 [Português](README.pt-br.md)

Backend Django para gestión de proyectos de ingeniería de transporte, modelado de red vial, conteos vehiculares, análisis de flujos y exportación a TRANSYT 8S.

## Características

- **Mandantes y Contactos**: Gestión de clientes/organizaciones con contactos asociados. Interfaz en español.
- **Proyectos**: Creación, seguimiento, imágenes (drag-drop / paste / file picker), estados (activo / finalizado).
- **Red Vial**: Modelado completo de red — calles, nodos (intersecciones), arcos (tramos), regulaciones (PARE/CEDA/SEMÁFORO/LIBRE), puntos de control (movimientos por intersección).
- **Periodización**: Conteos vehiculares manuales en intervalos de 15 minutos por punto de control y período. 8 tipos vehiculares (VL, TXC, TXB, C2E, C_mas2E, peatón, ciclista, moto) con cálculo automático de flujo total (ftot) usando factores de equivalencia.
- **Coeficientes de Cruce**: Factores de equivalencia vehicular en dos niveles — estándares globales + sobrescritura por proyecto. Resolución por herencia.
- **Análisis de Flujos**: Dashboard con tabla de datos, ranking de puntos de control por flujo, tabla comparativa (PCs vs períodos), y gráfico Chart.js de barras agrupadas. Recalculo agregado desde periodización.
- **TRANSYT 8S**: Configuración global (ciclo, W, K), parámetros de arco (flujo de saturación, ponderadores), fases semafóricas (verde inicio/fin). Generación de archivo .dat en formato TRANSYT-8S (ancho fijo 80 columnas) con cards header/1/2/11/31/32. Exportación por período individual (.dat) o múltiple (.zip).
- **Autenticación**: Registro, inicio de sesión, cierre de sesión. Protección `@login_required` en todas las vistas.
- **UI**: Diseño consistente con Tailwind CSS, modales, tablas editables inline con HTMX, formularios con labels en español, campos editables con contraste mejorado.

## Stack Tecnológico

- **Python 3.11** + **Django 5.2**
- **PostgreSQL** (multi-DB: default + ORA para VPS)
- HTMX 2.x para interactividad (CRUD inline)
- Tailwind CSS v4 (modo desarrollo con `python manage.py tailwind.dev`)
- WhiteNoise para archivos estáticos
- Chart.js 4.x para gráficos de análisis
- Font Awesome 6 (CDN) para iconografía
- Filesystem local para imágenes (Sin Supabase)

## Tooling

| Herramienta | Uso |
|-------------|-----|
| **ruff** | Linter + formatter Python |
| **ESLint** | Linter JavaScript |
| **Prettier** | Formatter JavaScript |
| **pre-commit** | Git hooks automáticos |
| **coverage** | Cobertura de tests (mín. 80%) |
| **pytest** | Test runner |

## Estructura de Apps

| App | Descripción | Estado |
|-----|-------------|--------|
| mandantes | Clientes (mandantes) y contactos | ✅ |
| proyectos | Proyectos de tráfico con imágenes y estados | ✅ |
| red_vial | Red vial, periodización, análisis, TRANSYT | ✅ |
| usuarios | Autenticación y perfiles | ✅ |
| tasks | Demo / pruebas (eliminar pronto) | ⚠️ |

## Flujo de Trabajo (Mini Manual)

```
1. MANDANTE → /mandantes/
   Crear cliente/organización.
   Agregar contactos asociados (nombre, email, teléfono, cargo).

2. PROYECTO → /proyectos/ → "Crear Proyecto"
   Asociar a un mandante. Completar datos generales, subir imagen.
   El proyecto puede estar Activo o Finalizado.

3. RED VIAL → /proyectos/<id>/resumen/
   Resumen del proyecto con cantidades de calles, nodos, arcos, PCs.
   Acceso a cada sección de modelado:

   a. Calles → Definir calles del área de estudio
   b. Nodos → Definir intersecciones (cruce de 2 calles)
   c. Arcos → Conectar nodos (origen → destino) con longitud
   d. Regulaciones → PARE / CEDA / SEMÁFORO / LIBRE
   e. Puntos de Control → Asignar movimiento (6 direcciones),
      viraje (DIR/DER/IZQ), arco entrada/salida, regulación, pistas
   f. Períodos → Definir ventanas de análisis (AM-L, PM-L, etc.)
    g. Coeficientes de Cruce → Factores de equivalencia vehicular
       (estándar global + sobreescritura por proyecto)

4. PERIODIZACIÓN → /proyectos/<id>/periodizacion/
   Seleccionar nodos (PCs), períodos, movimiento, fecha.
   "Generar" → crea filas de intervalos de 15 min.
   Ingresar conteos por tipo vehicular (VL, TXC, TXB, etc.).
   ftot se calcula automáticamente.

5. ANÁLISIS DE FLUJOS → /proyectos/<id>/analisis-flujos/
   Filtrar por nodo, período, movimiento, fecha.
   Visualizar:
   - Tabla detalle (flujo total, promedio, registros)
   - Ranking (PCs ordenados por flujo descendente)
   - Comparativa (PCs vs períodos, tabla pivote)
   - Gráfico Chart.js (barras agrupadas por PC y período)
   "Recalcular" para agregar datos de periodización a ResumenFlujo.

6. TRANSYT → /proyectos/<id>/configuracion-transyt/
   a. Configuración global → ciclo, W, K, pérdida/ganancia
   b. Parámetros de Arco → flujo saturación, ponderadores
      (1 por PC, con generación automática de defaults)
   c. Fases Semafóricas → verde inicio/fin por PC y fase
      (con generación automática de fase 1 por PC)

7. EXPORTAR .dat → Desde detalle del proyecto
   Validar datos completos. Seleccionar período o "todos".
   Genera archivo TRANSYT-8S (.dat por período, .zip para todos).
   Formato ancho fijo 80 columnas con validación de salida.
```

## URLs Principales

| Ruta | Vista |
|------|-------|
| `/` | Dashboard / Home |
| `/signin/` | Iniciar sesión |
| `/usuarios/` | Gestión de usuarios (admin) |
| `/mandantes/` | Lista de mandantes |
| `/mandantes/create/` | Crear mandante |
| `/mandantes/<id>/` | Detalle / editar mandante |
| `/proyectos/` | Lista de proyectos |
| `/proyectos/<id>/` | Detalle del proyecto |
| `/proyectos/<id>/resumen/` | Resumen de red vial |
| `/proyectos/<id>/generar-dat/` | Exportar TRANSYT .dat |
| `/red-vial/proyecto/<id>/calles/` | Gestión de calles |
| `/red-vial/proyecto/<id>/nodos/` | Gestión de nodos |
| `/red-vial/proyecto/<id>/arcos/` | Gestión de arcos |
| `/red-vial/proyecto/<id>/puntos-control/` | Puntos de control |
| `/red-vial/proyecto/<id>/periodizacion/` | Conteos vehiculares |
| `/red-vial/proyecto/<id>/analisis-flujos/` | Dashboard de flujos |
| `/red-vial/proyecto/<id>/configuracion-transyt/` | Configuración TRANSYT |
| `/red-vial/proyecto/<id>/parametros-arco/` | Parámetros de arco |
| `/red-vial/proyecto/<id>/fases-semaforicas/` | Fases semafóricas |

## Branches

| Rama | Propósito | Protegida | CI |
|------|-----------|-----------|----|
| `main` | Producción | Sí (PR + checks) | Solo manual (workflow_dispatch) |
| `staging` | Pre-producción | Sí (PR + checks) | Auto-deploy al push |
| `feature/*` | Desarrollo | No | lint + test en PR |
| `fix/*` | Hotfix | No | lint + test en PR |

## Ambientes

| Ambiente | DB | URL | Deploy |
|----------|----|-----|--------|
| local | PostgreSQL local (eitapp) | localhost:8000 | `python manage.py runserver` |
| staging | PostgreSQL (VPS ORA) | — | Automático al merge a `staging` |
| production | PostgreSQL (VPS ORA) | — | Manual via GitHub Actions |

### Arquitectura Multi-DB

```
                    ┌──────────────────────────────┐
                    │      Django (settings.py)      │
                    │  default: DATABASE_URL cascade   │
                    │  ORA: DATABASE_URL_ORA (VPS)    │
                    │  pg_local: DATABASE_URL_LOCAL   │
                    └──────┬───────────────┬─────────┘
                           │               │
              ┌────────────┘               └────────────┐
              ▼                                          ▼
   ┌──────────────────┐                    ┌──────────────────────┐
   │  localhost:5432   │                    │  161.153.14.37:5432  │
   │  eitapp (default) │                    │  eitapp (ORA)       │
   │  PG nativo        │                    │  Coolify / Docker   │
   └──────────────────┘                    └──────────────────────┘
```

### Resolución de `default`

```
DATABASE_URL=postgresql://user:pass@host:5432/eitapp    ← si está seteado
  ↓ no
DATABASE_URL_ORA=postgresql://user:pass@161.153.14.37:5432/eitapp    ← VPS
  ↓ no
postgresql://postgres:1234@localhost:5432/eitapp    ← fallback local
```

- **Local**: `DATABASE_URL` apunta a PostgreSQL local (`eitapp`). `ORA` disponible para switchear.
- **VPS (Coolify)**: Solo `DATABASE_URL_ORA` está definido → `default` cae a ORA automáticamente. Sin configuración extra.

### Multi-tenancy (futuro)

La aplicación soportará dos modelos de despliegue:

```
┌───────────────────────────────────────────────────────────────┐
│                   Balanceador / Proxy                          │
│                 (nginx + server_name o path)                    │
└──────┬─────────────────────────┬───────────────────────────────┘
       │                         │
       ▼                         ▼
┌──────────────────┐   ┌───────────────────────────┐
│  Plan Compartido  │   │    Plan Pro (consultora)  │
│  DB compartida    │   │  Stack Docker individual:  │
│  schema: tenant_* │   │  - web (Django)            │
│  (postgres1)      │   │  - db (PostgreSQL)         │
│                   │   │  - pgadmin4 (opcional)     │
│  Un solo pgAdmin  │   │  - redis (futuro)          │
│  multi-schema     │   │                             │
└──────────────────┘   └───────────────────────────┘
```

| Factor | Compartido | Pro |
|--------|-----------|------|
| Aislamiento de datos | Schema | Database independiente |
| Costo | Bajo (1 VPS) | Medio (1 VPS por tenant) |
| Escala | Hasta ~50 tenants | Ilimitado |
| Backup | Completo + schema dump | Completo por stack |
| Upgrade | Un deploy | Por stack (rollback individual) |
| Aprovisionamiento | `CREATE SCHEMA` | `docker compose up` |

**Estado:** Diseño definido. Pendiente de implementar (`ActiveDatabaseRouter` + `TenantMiddleware`).

## CI/CD

Los pipelines de GitHub Actions corren en cada PR/push a `staging`:

1. **Lint** — ruff (Python) + ESLint + Prettier (JS)
2. **Test** — pytest + coverage (umbral 80%)
3. **Build** — collectstatic
4. **Deploy Staging** — automático al push a `staging`
5. **Deploy Production** — manual via `workflow_dispatch`

## Inicio Rápido

```bash
# Clonar y crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pre-commit install

# Configurar entorno
cp .env.example .env

# Migraciones
python manage.py migrate

# Crear superuser
python manage.py createsuperuser

# Ejecutar
python manage.py runserver

# Modo desarrollo (Tailwind):
python manage.py tailwind.dev
```

### Lint & Format local

```bash
ruff check .                          # Python lint
ruff format --check .                 # Python format
npm run lint                          # JS lint
npm run format                        # JS format check
pre-commit run --all-files            # Todo junto
```

## Variables de Entorno

```
# Django
SECRET_KEY=...
DEBUG=True
DATABASE_URL=postgresql://postgres:1234@localhost:5432/eitapp  # default DB

# ORA (VPS / Coolify)
DATABASE_URL_ORA=postgresql://user:pass@161.153.14.37:5432/eitapp
CONN_MAX_AGE=600

# Local second DB (opcional, para switchear)
DATABASE_URL_LOCAL=postgresql://postgres:1234@localhost:5432/eitapp

# Cloud storage (local filesystem, no Supabase)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
```

## Licencia

MIT

---

## Índice

| # | Sección |
|---|---------|
| 1 | [Características](#características) |
| 2 | [Stack Tecnológico](#stack-tecnológico) |
| 3 | [Tooling](#tooling) |
| 4 | [Estructura de Apps](#estructura-de-apps) |
| 5 | [Flujo de Trabajo](#flujo-de-trabajo-mini-manual) |
| 6 | [URLs Principales](#urls-principales) |
| 7 | [Branches](#branches) |
| 8 | [Ambientes](#ambientes) |
| 9 | [Arquitectura Multi-DB](#arquitectura-multi-db) |
| 10 | [Multi-tenancy](#multi-tenancy-futuro) |
| 11 | [CI/CD](#cicd) |
| 12 | [Inicio Rápido](#inicio-rápido) |
| 13 | [Variables de Entorno](#variables-de-entorno) |
