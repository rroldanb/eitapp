# EIT App — Gestión de Proyectos de Ingeniería de Transporte

Aplicación web para modelar redes viales, gestionar conteos vehiculares, analizar flujos de tráfico y exportar configuraciones a TRANSYT 8S. Orientada a ingenieros de tránsito y gestores de proyectos.

## Stack

- **Python 3.11** + **Django 5.2**
- **PostgreSQL 16** (dev con Docker compose, prod con Coolify) con multi-DB router (`ActiveDatabaseRouter` + `DatabaseSelectorMiddleware`)
- **Docker** + **Docker Compose** para dev y prod
- **Coolify** para orquestación en VPS (2 servicios: `db` + `web`)
- **HTMX 2.0.8** + **hyperscript 0.9.91** (CDN, `defer`, sin bundler)
- **Tailwind CSS 4** via `django-tailwind` (app `theme/`)
- **Chart.js 4.4** + **OpenSeadragon** para imágenes
- **Volumen Docker persistente** para imágenes de proyecto/nodo
- **Gunicorn** + **WhiteNoise** para producción
- **pytest** + **pytest-django** para tests

## Comandos

- `python manage.py runserver` — arranca servidor Django
- `python manage.py tailwind.dev` — compila Tailwind en modo dev (requiere `runserver` aparte)
- `python manage.py tailwind.build` — compila Tailwind para producción
- `python manage.py test apps/<app>/tests/` — ejecuta tests Django
- `python manage.py test apps/red_vial/tests/ --verbosity=2` — tests detallados
- `npm run lint` — eslint (JS)
- `npm run lint:fix` — eslint con auto-fix
- `npm run format` — prettier check (JS)
- `npm run format:fix` — prettier format (JS)
- `honcho start` — levanta `runserver` + `tailwind.dev` simultáneo (si existe `Procfile`)
- `docker compose up` — levanta entorno local (PostgreSQL + Django) con un solo comando
- `docker compose -f docker-compose.prod.yml up -d` — levanta en producción (2 contenedores)
- `docker compose down` — detiene contenedores locales
- `git push origin main` — CI corre lint+tests+build, luego webhook gatilla rebuild en Coolify

## Estructura del proyecto

```
apps/
  common/           — BaseModel (UUID pk, timestamps), mixins, templates base, static (CSS/JS)
  mandantes/        — Clientes (mandantes) + contactos asociados
  proyectos/        — Proyectos con imágenes, estados (activo/finalizado), CRUD
  red_vial/         — Núcleo: calles, nodos, arcos, regulaciones, PCs, periodización, TRANSYT
    models/         — Modelos por dominio (calle, nodo, arco, transyt, etc.)
    views/          — CBVs built-in (ListView, View) + FBVs legacy
    services/       — Funciones CRUD + generación .dat + importación Excel
    urls/           — Modular por entidad (calle_urls.py, nodo_urls.py, etc.)
    tests/          — Tests por entidad (test_calle.py, test_nodo.py, etc.)
    templates/      — Templates por feature (red_vial/, partials/)
    forms/          — ModelForms por entidad
  usuarios/         — Auth (signup/signin/signout), perfiles, roles
  tasks/            — App demo/WIP (a integrar con proyectos)
  theme/            — Tailwind config + build (django-tailwind)
transito_backend/   — settings.py, urls.py raíz
```

## Convenciones

### Django Models
- Todos heredan de `apps.common.models.BaseModel` (UUID pk + `created_at`/`updated_at`)
- `related_name` explícito en cada `ForeignKey`
- Usar `select_related()` / `prefetch_related()` en vistas con N+1
- NO usar `objects.get()` sin try/except; preferir `get_object_or_404()` o `filter().first()`
- NO dejar `print()` en producción

### Django Views
- Preferir **class-based views** (ListView, View de Django) con `@method_decorator(login_required)`
- NO usar `GenericListView`, `GenericCreateView` etc. de `generic_views.py` — duplican funcionalidad built-in
- NO usar `inspect.signature()` — firmas explícitas siempre
- Para HTMX: retornar partial cuando `request.headers.get('HX-Request')`, full template cuando no
- `HttpResponse(status=204)` para DELETE exitoso
- `HX-Trigger` header para eventos post-operación

### Services
- Una función por operación CRUD (`get_X_by_proyecto`, `create_X`, `update_X`, `delete_X`)
- Recibir `proyecto_id: str`, devolver `QuerySet[X]` o `X`
- Firmas explícitas con type hints (`: str`, `-> QuerySet[X]`, `-> X`, `-> None`)
- `apply_sort_to_queryset()` de `base_service.py` para ordenamiento reusable

### Urls
- `red-vial/` con `include()` modular por entidad
- Nombres con prefijo: `calle_create`, `nodo_list`, `arco_update`
- UUID en URLs: `<uuid:proyecto_id>`, `<uuid:item_id>`

### Forms
- `ModelForm` con `Meta.fields` explícitos (nunca `'__all__'`)
- `Meta.widgets` con clases Tailwind
- Validación via `clean_<campo>()` o `clean()`
- Si necesita `proyecto`, recibirlo en `__init__` como kwarg

### HTMX (patrón click-to-edit row-swapping)
1. **Ver**: `GET /entity/{id}/` → fila con valores + botón Edit
2. **Editar**: Click en span → input + botón Guardar (hyperscript)
3. **Guardar**: Enter o click btn → `PUT /entity/{id}` → reemplaza fila con `outerHTML`
4. **Cancelar**: Escape → descarta cambios, vuelve a display
5. **Eliminar**: `DELETE /entity/{id}` → `hx-target="closest tr"` + `hx-swap="outerHTML"`
- NO usar patrón "always-editing" (inputs fijos con botón Actualizar)
- CSRF: `<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` en `base.html` (única fuente)
- HX-Trigger del servidor preferido sobre `htmx:afterRequest` en JS
- NO usar `hx-push-url="true"` en sort headers
- HTMX no swapea 400/204 por defecto → `htmx:beforeSwap` global en `proyecto_base.html`

### JavaScript
- `const` / `let` — NO `var`
- IIFE `(function() { ... })()` (sin bundler, sin ES modules)
- Archivos en `apps/common/static/js/{core,features}/`
- API globales: `showToast(msg, isSuccess, duration)`, `openModal(id)`, `closeModal(id)`, `ModalUtils.setupAutoClose(id)`
- NO usar `location.reload()` — dejar que htmx maneje el swap
- NO exponer API keys o secretos
- `defer` en todos los `<script>`

### Tailwind CSS
- Clases utilitarias, NO CSS custom salvo excepciones
- Gradiente primario: `bg-gradient-to-r from-indigo-600 to-purple-600` (solo sidebar y headers de sección)
- NO usar clases Bootstrap, gradient text (`background-clip: text`), glassmorphism
- Tema en `theme/static_src/tailwind.config.js`

## No hagas

- No instalar dependencias (pip / npm) sin avisar
- No tocar `apps/tasks/` — app WIP, postergada
- No usar `any` en Python sin justificarlo (preferir `Any` explícito con `from typing import Any`)
- No subir archivos `.env*`, `*.sqlite3`, `__pycache__/`, `node_modules/` al repositorio
- No usar `print()` en producción (usar logging si es necesario)
- No usar `objects.get()` suelto (siempre `get_object_or_404` o `filter().first()`)
- No mezclar function-based y class-based views para el mismo CRUD
- No hacer `git commit` sin `git status` + `git diff` previo
- No sombrear superficies en reposo (shadows solo para modals, toasts, dropdowns)
- No editar `docker-compose.yml` o `docker-compose.prod.yml` sin actualizar Coolify si corresponde
- No hacer deploy manual por SSH salvo emergencia — usar `git push origin main` + CI

## Flujo de trabajo

- Antes de una tarea no trivial, propón un plan y espera OK.
- Una tarea a la vez; al terminar, reporta qué cambiaste.
- Si no estás seguro al 80%, pregunta. No inventes.
- Los tests deben pasar antes de cada commit/PR.
- `npm run lint` + `npm run format` deben estar limpios antes de cada PR.
- El deploy a producción es automático: `git push origin main` → CI (lint+test+build) → webhook Coolify → rebuild de contenedores.
- Para staging: `git push origin staging` (si está configurado en Coolify).

## Notas

### Coolify / Docker
- **Arquitectura**: 2 contenedores en la VPS de OCI:
  1. `db` — PostgreSQL 16 Alpine (volumen persistente `postgres_data`)
  2. `web` — Django + Gunicorn (volumen persistente `media_data` para imágenes)
- **Coolify** orquesta ambos contenedores usando `docker-compose.prod.yml`. Coolify inyecta las variables de entorno desde su dashboard.
- **pgAdmin**: Si se requiere, dockerizar con `dpage/pgadmin4` conectado a la misma red Docker para gestión visual de PostgreSQL.
- **Almacenamiento de imágenes**: Las imágenes de proyecto/nodo se guardan en el volumen Docker `media_data` montado en `/app/media`. No se usa almacenamiento externo (ni Supabase, ni S3).

### Ambientes
- **Local con Docker compose**: `docker compose up` levanta PostgreSQL + Django. La DB local es efímera (el volumen `postgres_data` persiste datos).
- **Local sin Docker**: `DATABASE_URL` apunta a PostgreSQL nativo instalado en la máquina. Se puede switchear a la DB de VPS via `DATABASE_URL_ORA` con el middleware `DatabaseSelectorMiddleware`.
- **Producción (VPS)**: Coolify maneja el ciclo de vida de los contenedores. La app se conecta a su propio contenedor PostgreSQL via `DATABASE_URL` que Coolify setea automáticamente.

### CI/CD
- **GitHub Actions** corre lint + tests + build en cada push/PR a staging/main.
- **Webhook**: Si CI pasa en `main`, se dispara un webhook a Coolify que gatilla rebuild y deploy automático.
- **Fallback**: Los workflows `deploy-prod.yml`, `deploy-staging.yml` y `deploy.yml` existen como alternativa manual por SSH (deprecados, no usar en el día a día).

### Otros
- **Signup**: La vista `signup` existe en `apps/usuarios/views/views.py` pero NO está cableada en las URLs. Los usuarios se crean desde dentro del sistema (admin).
- **URLs documentadas** en README.md (`URLs Principales`) — actualizar si se agregan/quitan rutas.

## Documentación

- `PRODUCT.md` — descripción del producto, usuarios, principios de diseño
- `DESIGN.md` — sistema de diseño completo (colores, tipografía, componentes, reglas)
- `README.md` — guía rápida, URLs principales, flujo de trabajo completo
- `AGENTS.md` — este archivo (convenciones de desarrollo)
- `TODO.md` — tareas pendientes y próximas
- `opencode.json` — configuración de opencode
- `.opencode/skills/` — skills de opencode (formato-salida, htmx-edit-row, impeccable, etc.)
