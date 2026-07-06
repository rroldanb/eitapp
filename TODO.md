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

## ✅ Fase 0: PostgreSQL como DB por defecto

**Objetivo:** Reemplazar SQLite por PostgreSQL como motor principal, eliminar Supabase, unificar stack.

### Logros
- SQLite → PostgreSQL migration completada (206 tests pasan)
- Multi-DB routing: `default` (local PG o VPS ORA) + `ORA` (VPS) + `pg_local` (local switching)
- UUID inconsistencies reparadas (109 duplicados, 203 FK updates)
- Supabase eliminado: paquete, SDK, archivos legacy
- `default` DB cascade: `DATABASE_URL` → `DATABASE_URL_ORA` → local PG fallback

### Pendiente
- [ ] 0.5 — Dockerizar PostgreSQL + pgAdmin4 en VPS (opcional, para gestión visual)

## Fase 4: Multi-tenancy (Database-per-Tenant)

- [ ] 4.1 — Agregar modelo `Tenant` (nombre, schema, db_alias, plan: shared/pro)
- [ ] 4.2 — Middleware `TenantMiddleware`: extraer tenant del subdominio/request
- [ ] 4.3 — `TenantDatabaseRouter`: elegir DB según `request.tenant`
- [ ] 4.4 — Template database `eit_template` con schema vacío + seed data
- [ ] 4.5 — Flujo de creación de tenant: `CREATE DATABASE ... TEMPLATE eit_template`
- [ ] 4.6 — Registrar y exponer tenant en pgAdmin4 automáticamente (API)
- [ ] 4.7 — Actualizar vistas de login/signup para asociar usuario a tenant
- [ ] 4.8 — Backup por tenant: script que dumpera cada base/schema por separado

## ✅ Fase 5: Refactor y Eliminación de Legacy
- [x] 5.0 — Eliminar `apps/imagenes/utils/supabase_client.py` (legacy)
- [x] 5.0b — Eliminar management command `migrate_supabase_images.py` (one-time)
- [x] 5.0c — Eliminar SDK supabase de `requirements.txt`
- [x] 5.1 — Eliminar `_sort_header.html` (huérfano)
- [x] 5.2 — Eliminar `generic_views.py` (usa `inspect.signature()`, huérfano)
- [x] 5.3a — Eliminar `trafico_views.py` (4 FBVs período legacy)
- [x] 5.3b — Podar `red_vial_views.py` (solo 2 FBVs coeficiente vivos)
- [x] 5.3c — Podar `all_urls.py` (solo 2 patterns coeficiente FBV)
- [x] 5.3d — Podar `red_vial_service.py` (solo 7 funciones coeficiente)
- [x] 5.4 — Type hints en views (mandantes, proyectos, usuarios) — 31 FBVs tipadas
- [x] 5.5 — Type hints en services (mandantes, proyectos, imagenes, common) — 5 archivos

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

## ✅ Fase 8: DX y CI

### Completado
- [x] 8.1 — GitHub Action para deploy automático a Oracle VPS (.github/workflows/deploy.yml)
- [x] 8.2 — Pre-commit hooks configurados (ruff, eslint, prettier, trailing-whitespace, end-of-file-fixer)
- [x] 8.3 — ruff configurado como linter/formatter Python (`.ruff.toml`)

### Completado
- [x] 8.4 — Healthcheck endpoint para monitorear multi-DB / schema status

---

## Backlog ✅

- [x] Revisar partials no usados en `templates/partials/` — solo `_sort_header.html` está huérfano
- [x] Agregar `aria-*` faltantes en tablas editables — `aria-label` en Guardar/Eliminar (14 botones) + `aria-label` en 9 tablas
- [x] Verificar que `conftest.py` raíz no colisiona — solo hay un `conftest.py` en raíz, sin colisión
- [x] Cobertura de templates: todas las tablas CRUD usan CBVs, `generic_views.py` no se importa en ningún lado
- [x] Fix: tailwind dev moría con `Error: That port is already in use` / `rc=1` — matar proceso en 8000 + quitar `check_db_connections()` de `CommonConfig.ready()` + `--watch=always` + `.strip()` en ALLOWED_HOSTS
- [x] Migrar SQLite → PostgreSQL default (settings.py, requirements.txt, UUID dedup)
- [x] Eliminar Supabase del stack (SDK, archivos, requirements)

---

**Estado actual:** 206 tests pasan ✅ | Fase 5 completada ✅ | Type hints en views + services en todas las apps ✅ | PostgreSQL default ✅ | Supabase removed ✅
