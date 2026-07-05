from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

from apps.admin_views import (
    backup_database,
    descargar_plantilla,
    migracion_descarga_csv,
    migracion_descarga_xlsx,
    migracion_gui,
    migracion_reporte,
    restore_database,
)
from apps.usuarios import views as user_views

urlpatterns = [
    path("health/", lambda r: HttpResponse("OK"), name="health"),
    path("admin/generar-planilla/", descargar_plantilla, name="generar_planilla"),
    path("admin/migracion/", migracion_gui, name="migracion_gui"),
    path("admin/migracion/<str:token>/", migracion_reporte, name="migracion_reporte"),
    path(
        "admin/migracion/<str:token>/xlsx/", migracion_descarga_xlsx, name="migracion_descarga_xlsx"
    ),
    path(
        "admin/migracion/<str:token>/csv/<str:sheet>/",
        migracion_descarga_csv,
        name="migracion_descarga_csv",
    ),
    path("admin/backup-db/", backup_database, name="backup_database"),
    path("admin/restore-db/", restore_database, name="restore_database"),
    path("admin/", admin.site.urls),
    path("", user_views.home, name="home"),
    path("switch-db/<str:alias>/", user_views.switch_db, name="switch_db"),
    path("logout/", user_views.signout, name="signout"),
    path("signin/", user_views.signin, name="signin"),
    path("usuarios/", include("apps.usuarios.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("mandantes/", include("apps.mandantes.urls")),
    path("proyectos/", include("apps.proyectos.urls")),
    path("red-vial/", include("apps.red_vial.urls")),
    path("theme/", include("theme.urls")),
]


if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
