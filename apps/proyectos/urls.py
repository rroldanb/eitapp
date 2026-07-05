from django.urls import path

from .views.proyectos_views import *

urlpatterns = [
    path("", proyectos_view, name="proyectos"),
    path("create/", proyecto_create_view, name="proyecto_create"),
    path("<uuid:proyecto_id>/", proyecto_detail_view, name="proyecto_detail"),
    path("<uuid:proyecto_id>/delete/", proyecto_delete_view, name="proyecto_delete"),
    path(
        "<uuid:proyecto_id>/delete-image/", proyecto_delete_image_view, name="proyecto_delete_image"
    ),
    path("<uuid:proyecto_id>/finalizar/", proyecto_finalizar_view, name="proyecto_finalizar"),
    path("<uuid:proyecto_id>/reactivar/", proyecto_reactivar_view, name="proyecto_reactivar"),
    path("<uuid:proyecto_id>/resumen/", proyecto_resumen_view, name="proyecto_resumen"),
    path("<uuid:proyecto_id>/generar-dat/", proyecto_generar_dat_view, name="proyecto_generar_dat"),
    path(
        "<uuid:proyecto_id>/generar-planilla/",
        proyecto_generar_plantilla_view,
        name="proyecto_generar_plantilla",
    ),
    path(
        "<uuid:proyecto_id>/generar-parametros-arco/",
        proyecto_generar_parametros_arco_view,
        name="proyecto_generar_parametros_arco",
    ),
    path(
        "<uuid:proyecto_id>/generar-fases-semaforicas/",
        proyecto_generar_fases_semaforicas_view,
        name="proyecto_generar_fases_semaforicas",
    ),
]
