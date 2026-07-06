# EIT App — Transportation Engineering Project Management

> 🇺🇸 English · 🇪🇸 [Español](README.md) · 🇧🇷 [Português](README.pt-br.md)

Django backend for transportation engineering project management, road network modeling, traffic counts, flow analysis, and TRANSYT 8S export.

## Features

- **Clients & Contacts**: Manage client organizations with associated contacts. Spanish UI.
- **Projects**: Creation, tracking, images (drag-drop / paste / file picker), status (active / completed).
- **Road Network**: Full network modeling — streets, nodes (intersections), arcs (segments), regulations (STOP/YIELD/TRAFFIC_LIGHT/FREE), control points (intersection movements).
- **Periodization**: Manual vehicle counts in 15-minute intervals per control point and period. 8 vehicle types (VL, TXC, TXB, C2E, C_mas2E, pedestrian, cyclist, motorcycle) with automatic total flow (ftot) calculation using equivalence factors.
- **Crossing Coefficients**: Vehicle equivalence factors at two levels — global standards + project overrides. Inheritance resolution.
- **Flow Analysis**: Dashboard with data table, control point flow ranking, comparative table (CPs vs periods), and grouped bar Chart.js chart. Aggregated recalculation from periodization.
- **TRANSYT 8S**: Global config (cycle, W, K), arc parameters (saturation flow, weights), signal phases (green start/end). Generates .dat files in TRANSYT-8S format (80-column fixed width) with header/1/2/11/31/32 cards. Export by individual period (.dat) or multiple (.zip).
- **Authentication**: Registration, login, logout. `@login_required` protection on all views.
- **UI**: Consistent design with Tailwind CSS, modals, inline editable tables with HTMX, Spanish form labels, improved contrast on editable fields.

## Tech Stack

- **Python 3.11** + **Django 5.2**
- **PostgreSQL** (multi-DB: default + ORA for VPS)
- HTMX 2.x for interactivity (inline CRUD)
- Tailwind CSS v4 (dev mode with `python manage.py tailwind.dev`)
- WhiteNoise for static files
- Chart.js 4.x for analysis charts
- Font Awesome 6 (CDN) for icons
- Local filesystem for images (no Supabase)

## Tooling

| Tool | Usage |
|------|-------|
| **ruff** | Python linter + formatter |
| **ESLint** | JavaScript linter |
| **Prettier** | JavaScript formatter |
| **pre-commit** | Automated Git hooks |
| **coverage** | Test coverage (min. 80%) |
| **pytest** | Test runner |

## App Structure

| App | Description | Status |
|-----|-------------|--------|
| mandantes | Clients (mandantes) and contacts | ✅ |
| proyectos | Traffic projects with images and status | ✅ |
| red_vial | Road network, periodization, analysis, TRANSYT | ✅ |
| usuarios | Authentication and profiles | ✅ |
| tasks | Demo / testing (to be removed soon) | ⚠️ |

## Workflow (Quick Manual)

```
1. CLIENT → /mandantes/
   Create client/organization.
   Add associated contacts (name, email, phone, role).

2. PROJECT → /proyectos/ → "Create Project"
   Associate with a client. Fill general data, upload image.
   Project can be Active or Completed.

3. ROAD NETWORK → /proyectos/<id>/resumen/
   Project summary with street, node, arc, CP counts.
   Access each modeling section:

   a. Streets → Define study area streets
   b. Nodes → Define intersections (2-street crossing)
   c. Arcs → Connect nodes (origin → destination) with length
   d. Regulations → STOP / YIELD / TRAFFIC LIGHT / FREE
   e. Control Points → Assign movement (6 directions),
      turn (ST/RT/LT), entry/exit arc, regulation, lanes
   f. Periods → Define analysis windows (AM-P, PM-P, etc.)
   g. Crossing Coefficients → Vehicle equivalence factors
      (global standard + project override)

4. PERIODIZATION → /proyectos/<id>/periodizacion/
   Select nodes (CPs), periods, movement, date.
   "Generate" → creates 15-min interval rows.
   Enter counts by vehicle type (VL, TXC, TXB, etc.).
   ftot is calculated automatically.

5. FLOW ANALYSIS → /proyectos/<id>/analisis-flujos/
   Filter by node, period, movement, date.
   View:
   - Detail table (total flow, average, records)
   - Ranking (CPs sorted by descending flow)
   - Comparison (CPs vs periods, pivot table)
   - Chart.js chart (grouped bars by CP and period)
   "Recalculate" to aggregate periodization data into ResumenFlujo.

6. TRANSYT → /proyectos/<id>/configuracion-transyt/
   a. Global config → cycle, W, K, loss/gain
   b. Arc Parameters → saturation flow, weights
      (1 per CP, with auto-generated defaults)
   c. Signal Phases → green start/end by CP and phase
      (with auto-generated phase 1 per CP)

7. EXPORT .dat → From project detail
   Validate complete data. Select period or "all".
   Generates TRANSYT-8S file (.dat per period, .zip for all).
   80-column fixed width format with output validation.
```

## Main URLs

| Route | View |
|-------|------|
| `/` | Dashboard / Home |
| `/signin/` | Login |
| `/usuarios/` | User management (admin) |
| `/mandantes/` | Client list |
| `/mandantes/create/` | Create client |
| `/mandantes/<id>/` | Client detail / edit |
| `/proyectos/` | Project list |
| `/proyectos/<id>/` | Project detail |
| `/proyectos/<id>/resumen/` | Road network summary |
| `/proyectos/<id>/generar-dat/` | Export TRANSYT .dat |
| `/red-vial/proyecto/<id>/calles/` | Street management |
| `/red-vial/proyecto/<id>/nodos/` | Node management |
| `/red-vial/proyecto/<id>/arcos/` | Arc management |
| `/red-vial/proyecto/<id>/puntos-control/` | Control points |
| `/red-vial/proyecto/<id>/periodizacion/` | Vehicle counts |
| `/red-vial/proyecto/<id>/analisis-flujos/` | Flow dashboard |
| `/red-vial/proyecto/<id>/configuracion-transyt/` | TRANSYT config |
| `/red-vial/proyecto/<id>/parametros-arco/` | Arc parameters |
| `/red-vial/proyecto/<id>/fases-semaforicas/` | Signal phases |

## Branches

| Branch | Purpose | Protected | CI |
|--------|---------|-----------|----|
| `main` | Production | Yes (PR + checks) | Manual only (workflow_dispatch) |
| `staging` | Pre-production | Yes (PR + checks) | Auto-deploy on push |
| `feature/*` | Development | No | lint + test on PR |
| `fix/*` | Hotfix | No | lint + test on PR |

## Environments

| Environment | DB | URL | Deploy |
|-------------|----|-----|--------|
| local | PostgreSQL local (eitapp) | localhost:8000 | `python manage.py runserver` |
| staging | PostgreSQL (VPS ORA) | — | Auto on merge to `staging` |
| production | PostgreSQL (VPS ORA) | — | Manual via GitHub Actions |

### Multi-DB Architecture

```
                    ┌─────────────────────────────────┐
                    │      Django (settings.py)        │
                    │  default: DATABASE_URL cascade    │
                    │  ORA: DATABASE_URL_ORA (VPS)     │
                    │  pg_local: DATABASE_URL_LOCAL    │
                    └──────┬──────────────┬────────────┘
                           │              │
              ┌────────────┘              └────────────┐
              ▼                                         ▼
   ┌──────────────────┐                   ┌──────────────────────┐
   │  localhost:5432   │                   │  161.153.14.37:5432  │
   │  eitapp (default) │                   │  eitapp (ORA)       │
   │  Native PG        │                   │  Coolify / Docker   │
   └──────────────────┘                   └──────────────────────┘
```

### `default` resolution

```
DATABASE_URL=postgresql://user:pass@host:5432/eitapp    ← if set
  ↓ no
DATABASE_URL_ORA=postgresql://user:pass@161.153.14.37:5432/eitapp    ← VPS
  ↓ no
postgresql://postgres:1234@localhost:5432/eitapp    ← local fallback
```

- **Local**: `DATABASE_URL` points to local PostgreSQL (`eitapp`). `ORA` available for switching.
- **VPS (Coolify)**: Only `DATABASE_URL_ORA` is set → `default` falls back to ORA automatically. No extra config.

### Multi-tenancy (future)

The app will support two deployment models:

```
┌───────────────────────────────────────────────────────────────┐
│                   Load Balancer / Proxy                        │
│                 (nginx + server_name or path)                   │
└──────┬─────────────────────────┬───────────────────────────────┘
       │                         │
       ▼                         ▼
┌──────────────────┐   ┌───────────────────────────┐
│  Shared Plan      │   │    Pro Plan (consultancy) │
│  Shared DB        │   │  Individual Docker stack: │
│  schema: tenant_* │   │  - web (Django)           │
│  (postgres1)      │   │  - db (PostgreSQL)        │
│                   │   │  - pgadmin4 (optional)    │
│  Single pgAdmin   │   │  - redis (future)         │
│  multi-schema     │   │                            │
└──────────────────┘   └───────────────────────────┘
```

| Factor | Shared | Pro |
|--------|--------|-----|
| Data isolation | Schema | Independent database |
| Cost | Low (1 VPS) | Medium (1 VPS per tenant) |
| Scale | Up to ~50 tenants | Unlimited |
| Backup | Full + schema dump | Full per stack |
| Upgrade | Single deploy | Per stack (individual rollback) |
| Provisioning | `CREATE SCHEMA` | `docker compose up` |

**Status:** Design defined. Pending implementation (`ActiveDatabaseRouter` + `TenantMiddleware`).

## CI/CD

GitHub Actions pipelines run on every PR/push to `staging`:

1. **Lint** — ruff (Python) + ESLint + Prettier (JS)
2. **Test** — pytest + coverage (80% threshold)
3. **Build** — collectstatic
4. **Deploy Staging** — auto on push to `staging`
5. **Deploy Production** — manual via `workflow_dispatch`

## Quick Start

```bash
# Clone and create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pre-commit install

# Configure environment
cp .env.example .env

# Migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run
python manage.py runserver

# Dev mode (Tailwind):
python manage.py tailwind.dev
```

### Lint & Format (local)

```bash
ruff check .                          # Python lint
ruff format --check .                 # Python format check
npm run lint                          # JS lint
npm run format                        # JS format check
pre-commit run --all-files            # All together
```

## Environment Variables

```
SECRET_KEY=...
DEBUG=True
DATABASE_URL=...
```

## License

MIT
