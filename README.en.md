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
- SQLite (dev) / PostgreSQL (production)
- HTMX 2.x for interactivity (inline CRUD)
- Tailwind CSS v4 (dev mode with `python manage.py tailwind.dev`)
- WhiteNoise for static files
- Chart.js 4.x for analysis charts
- Font Awesome 6 (CDN) for icons
- Supabase Storage for project/node images

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
1. REGISTER → /signup/
   Create user account.

2. CLIENT → /mandantes/
   Create client/organization.
   Add associated contacts (name, email, phone, role).

3. PROJECT → /proyectos/ → "Create Project"
   Associate with a client. Fill general data, upload image.
   Project can be Active or Completed.

4. ROAD NETWORK → /proyectos/<id>/resumen/
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

5. PERIODIZATION → /proyectos/<id>/periodizacion/
   Select nodes (CPs), periods, movement, date.
   "Generate" → creates 15-min interval rows.
   Enter counts by vehicle type (VL, TXC, TXB, etc.).
   ftot is calculated automatically.

6. FLOW ANALYSIS → /proyectos/<id>/analisis-flujos/
   Filter by node, period, movement, date.
   View:
   - Detail table (total flow, average, records)
   - Ranking (CPs sorted by descending flow)
   - Comparison (CPs vs periods, pivot table)
   - Chart.js chart (grouped bars by CP and period)
   "Recalculate" to aggregate periodization data into ResumenFlujo.

7. TRANSYT → /proyectos/<id>/configuracion-transyt/
   a. Global config → cycle, W, K, loss/gain
   b. Arc Parameters → saturation flow, weights
      (1 per CP, with auto-generated defaults)
   c. Signal Phases → green start/end by CP and phase
      (with auto-generated phase 1 per CP)

8. EXPORT .dat → From project detail
   Validate complete data. Select period or "all".
   Generates TRANSYT-8S file (.dat per period, .zip for all).
   80-column fixed width format with output validation.
```

## Main URLs

| Route | View |
|-------|------|
| `/` | Dashboard / Home |
| `/signin/` | Login |
| `/signup/` | Register |
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
| local | SQLite | localhost:8000 | `python manage.py runserver` |
| staging | PostgreSQL (VPS) | — | Auto on merge to `staging` |
| production | PostgreSQL (VPS) | — | Manual via GitHub Actions |

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
