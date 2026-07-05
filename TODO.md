# TODO — Proyecto EIT App

---

## ✅ Fase 1: Limpieza
- [x] 1.1 — Eliminar `print()` en producción
- [x] 1.2 — Eliminar `htmx-csrf.js` + desvincular de `base.html`
- [x] 1.3 — Eliminar `crud_events.js` (duplicado)
- [x] 1.4 — `objects.get()` → `get_object_or_404` (16 lugares)
- [x] 1.5 — Quitar `style="display:none"` redundante en `htmx-indicator`
- [x] 1.6 — Setup pytest (`pytest.ini` + `conftest.py`)

## ✅ Fase 2: Migración a CBVs built-in + click-to-activate
- [x] 2.1–2.7 — Calle piloto (ListView, View, click-to-activate, 18 tests)
- [x] 2.8 — Nodo
- [x] 2.9a — Arco
- [x] 2.9b — Regulación
- [x] 2.9c — PuntoControl
- [x] 2.10 — CoeficienteCruce, Período
- [x] 2.11 — ParametroArco, FaseSemaforica (Transyt)
- [x] ~~Periodización~~ → SKIP (funcionalidad distinta)

## ✅ Fase 3: Pulido
- [x] 3.1 — Quitar `hx-push-url="true"` (6 ocurrencias) + stale CSS sort classes
- [x] 3.2 — Type hints en 16/16 services + 14/14 views de red_vial
- [x] 3.3 — Configurar eslint + prettier para JS

---

## Fase 0: Infraestructura Docker (PostgreSQL + pgAdmin4)

**Objetivo:** Reemplazar SQLite/ORA por PostgreSQL en Docker, migrar datos, estandarizar stack.

### Arquitectura objetivo: Multi-tenancy Database-per-Tenant

La aplicación soportará dos modelos de despliegue según el plan del tenant:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Balanceador / Proxy                       │
│                      (nginx + server_name o path)                 │
└──────┬──────────────────────────┬────────────────────────────────┘
       │                          │
       ▼                          ▼
┌──────────────────┐   ┌────────────────────────────┐
│  Plan Compartido  │   │     Plan Pro (consultora)   │
│  DB compartida    │   │  Stack Docker individual:   │
│  schema: tenant_* │   │  - web (Django)             │
│  (postgres1)      │   │  - db (PostgreSQL)          │
│                   │   │  - pgadmin4 (opcional)      │
│  Un solo pgAdmin  │   │  - redis (futuro)           │
│  multi-schema     │   │                              │
└──────────────────┘   └────────────────────────────┘
```

**Criterio de decisión (escala):**

| Factor | Compartido | Pro |
|--------|-----------|-----|
| Aislamiento de datos | Schema | Database independiente |
| Costo | Bajo (1 VPS) | Medio (1 VPS por tenant) |
| Escala | Hasta ~50 tenants | Ilimitado |
| Backup | Completo + schema dump | Completo por stack |
| Upgrade automático | Sí (un deploy) | Por stack (rollback individual) |
| Aprovisionamiento | Instantáneo (CREATE SCHEMA) | `docker compose up` |

**Decisión:** Implementar primero con DB compartida + schema por tenant
(compatible con `ActiveDatabaseRouter`). El stack Pro se agrega después sin
cambiar el modelo de datos — solo cambia el router de base de datos.

### Tareas

- [ ] 0.1 — Escribir `postgres-compose.yml` (PostgreSQL 16 + pgAdmin4 oficial)
- [ ] 0.2 — Migrar dump SQLite/ORA a PostgreSQL local
- [ ] 0.3 — Cambiar `settings.py`: `ENGINE=django.db.backends.postgresql`, multi-DB si aplica
- [ ] 0.4 — Probar migraciones + `python manage.py check --deploy`
- [ ] 0.5 — pgAdmin4: configurar server groups + login por tenant
- [ ] 0.6 — Deploy a VPS: postgres + pgadmin en Docker, apuntar Django a contenedor DB

## Fase 4: Multi-tenancy (Database-per-Tenant)

- [ ] 4.1 — Agregar modelo `Tenant` (nombre, schema, db_alias, plan: shared/pro)
- [ ] 4.2 — Middleware `TenantMiddleware`: extraer tenant del subdominio/request
- [ ] 4.3 — `TenantDatabaseRouter`: elegir DB según `request.tenant`
- [ ] 4.4 — Template database `eit_template` con schema vacío + seed data
- [ ] 4.5 — Flujo de creación de tenant: `CREATE DATABASE ... TEMPLATE eit_template`
- [ ] 4.6 — Registrar y exponer tenant en pgAdmin4 automáticamente (API)
- [ ] 4.7 — Actualizar vistas de login/signup para asociar usuario a tenant
- [ ] 4.8 — Backup por tenant: script que dumpera cada base/schema por separado

## Fase 5: Refactor y Eliminación de Legacy

- [ ] 5.1 — Eliminar `_sort_header.html` (huérfano, ninguna tabla lo incluye)
- [ ] 5.2 — Eliminar o simplificar `generic_views.py` (usa `inspect.signature()`, no se usa en producción)
- [ ] 5.3 — Revisar `red_vial_views.py` y `trafico_views.py` (FBVs legacy que referencian vistas ya migradas a CBVs)
- [ ] 5.4 — Type hints en views de otras apps (`mandantes/`, `proyectos/`, `usuarios/`)
- [ ] 5.5 — Type hints en servicios de otras apps

## Fase 6: Tests

- [ ] 6.1 — Tests para CRUD views (no solo services) — probar HTMX partials, HX-Trigger, status codes
- [ ] 6.2 — Tests para importación Excel
- [ ] 6.3 — Tests para generación .dat TRANSYT
- [ ] 6.4 — Tests para periodización (funcionalidad SKIPeada)
- [ ] 6.5 — Tests para apps mandantes, proyectos, usuarios
- [ ] 6.6 — Tests multi-tenant: aislamiento entre schemas/DBs

## Fase 7: Funcionalidad Pendiente

- [ ] 7.1 — Integrar app `tasks/` con proyectos
- [ ] 7.2 — Periodización: migrar a CBVs built-in + click-to-activate (re-evaluar si aplica)
- [ ] 7.3 — Planes Compartido vs Pro: billing, provisioning UI, monitoreo

## Fase 8: DX y CI

- [x] 8.1 — GitHub Action para deploy automático a Oracle VPS (.github/workflows/deploy.yml)
- [ ] 8.2 — Pre-commit hooks (ruff, eslint, prettier)
- [ ] 8.3 — Configurar ruff como linter/formatter Python
- [ ] 8.4 — Healthcheck endpoint para monitorear multi-DB / schema status

---

## Backlog ✅

- [x] Revisar partials no usados en `templates/partials/` — solo `_sort_header.html` está huérfano
- [x] Agregar `aria-*` faltantes en tablas editables — `aria-label` en Guardar/Eliminar (14 botones) + `aria-label` en 9 tablas
- [x] Verificar que `conftest.py` raíz no colisiona — solo hay un `conftest.py` en raíz, sin colisión
- [x] Cobertura de templates: todas las tablas CRUD usan CBVs, `generic_views.py` no se importa en ningún lado
- [x] Fix: tailwind dev moría con `Error: That port is already in use` / `rc=1` — matar proceso en 8000 + quitar `check_db_connections()` de `CommonConfig.ready()` + `--watch=always` + `.strip()` en ALLOWED_HOSTS

---

**Estado actual:** 200 tests pasan ✅ | `npm run lint`: 0 errors, 19 warnings ✅
