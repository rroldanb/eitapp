from django.contrib import admin
from django.urls import path, include
from apps.usuarios import views as user_views
from apps.admin_views import descargar_plantilla, backup_database, restore_database, migracion_gui, migracion_reporte, migracion_descarga_xlsx, migracion_descarga_csv
from django.conf import settings

urlpatterns = [
    path('admin/generar-planilla/', descargar_plantilla, name='generar_planilla'),
    path('admin/migracion/', migracion_gui, name='migracion_gui'),
    path('admin/migracion/<str:token>/', migracion_reporte, name='migracion_reporte'),
    path('admin/migracion/<str:token>/xlsx/', migracion_descarga_xlsx, name='migracion_descarga_xlsx'),
    path('admin/migracion/<str:token>/csv/<str:sheet>/', migracion_descarga_csv, name='migracion_descarga_csv'),
    path('admin/backup-db/', backup_database, name='backup_database'),
    path('admin/restore-db/', restore_database, name='restore_database'),
    path('admin/', admin.site.urls),
    path('', user_views.home, name='home'),
    path('logout/', user_views.signout, name='signout'),
    path('signin/', user_views.signin, name='signin'),
    path('usuarios/', include('apps.usuarios.urls')),



    path('tasks/', include('apps.tasks.urls')),
    path('mandantes/', include('apps.mandantes.urls')),
    path('proyectos/', include('apps.proyectos.urls')),
    path('red-vial/', include('apps.red_vial.urls')),
    path('theme/', include('theme.urls')),
]


if settings.DEBUG:
    # Include django_browser_reload URLs only in DEBUG mode
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]