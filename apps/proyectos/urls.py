from django.urls import path
from .views.proyectos_views import *

urlpatterns = [
    path("", proyectos_view, name="proyectos"),
    path("create/", create_proyecto_view, name="proyecto_create"),
    path("<uuid:proyecto_id>/", proyecto_detail_view, name="proyecto_detail"),
    path("<uuid:proyecto_id>/delete/", proyecto_delete_view, name="proyecto_delete"),
    # Project sections
    path("<uuid:proyecto_id>/arcos/", proyecto_arcos_view, name="proyecto_arcos"),
    path("<uuid:proyecto_id>/nodos/", proyecto_nodos_view, name="proyecto_nodos"),
    path("<uuid:proyecto_id>/calles/", proyecto_calles_view, name="proyecto_calles"),
    path("<uuid:proyecto_id>/resumen/", proyecto_resumen_view, name="proyecto_resumen"),
]