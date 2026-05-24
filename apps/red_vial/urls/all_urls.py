from django.urls import path, include
from django.contrib.auth.decorators import login_required
from ..views.red_vial_views import *
from ..views.trafico_views import *

urlpatterns = [


    # ========== REGULACIÓN URLs ==========
    path("regulaciones/", regulaciones_list_view, name="regulaciones_list"),
    path("regulaciones/create/", regulacion_create_view, name="regulacion_create"),

    # ========== NODO MOVIMIENTO URLs ==========
    path("proyecto/<uuid:proyecto_id>/nodos-movimientos/", nodos_movimientos_list_view, name="nodos_movimientos_list"),
    path("proyecto/<uuid:proyecto_id>/nodos-movimientos/create/", nodo_movimiento_create_view, name="nodo_movimiento_create"),

    # ========== COEFICIENTE URLs ==========
    path("coeficientes/", coeficientes_list_view, name="coeficientes_list"),
    path("coeficientes/create/", coeficiente_create_view, name="coeficiente_create"),

    # ========== PERIODO URLs ==========
    path("periodos/", periodos_list_view, name="periodos_list"),
    path("periodos/create/", periodo_create_view, name="periodo_create"),
    path("periodo/<uuid:periodo_id>/update/", periodo_update_view, name="periodo_update"),
    path("periodo/<uuid:periodo_id>/delete/", periodo_delete_view, name="periodo_delete"),

    # ========== CONTEO VEHICULAR URLs ==========
    path("proyecto/<uuid:proyecto_id>/conteos/", conteos_list_view, name="conteos_list"),
    path("proyecto/<uuid:proyecto_id>/conteos/create/", conteo_create_view, name="conteo_create"),
    path("conteo/<uuid:conteo_id>/", conteo_detail_view, name="conteo_detail"),
    path("conteo/<uuid:conteo_id>/update/", conteo_update_view, name="conteo_update"),
    path("conteo/<uuid:conteo_id>/delete/", conteo_delete_view, name="conteo_delete"),

    # ========== FLUJO MOVIMIENTO URLs ==========
    path("proyecto/<uuid:proyecto_id>/flujos/", flujos_list_view, name="flujos_list"),
    path("proyecto/<uuid:proyecto_id>/flujos/create/", flujo_create_view, name="flujo_create"),
    path("flujo/<uuid:flujo_id>/update/", flujo_update_view, name="flujo_update"),
    path("flujo/<uuid:flujo_id>/delete/", flujo_delete_view, name="flujo_delete"),

    # ========== ANALISIS URLs ==========
    path("proyecto/<uuid:proyecto_id>/analisis/", analisis_trafico_view, name="analisis_trafico"),

    # ========== API URLs ==========
    path("api/proyecto/<uuid:proyecto_id>/calles/", api_calles_by_proyecto, name="api_calles"),
    path("api/proyecto/<uuid:proyecto_id>/nodos/", api_nodos_by_proyecto, name="api_nodos"),
    path("api/proyecto/<uuid:proyecto_id>/arcos/", api_arcos_by_proyecto, name="api_arcos"),
    path("api/periodos/", api_periodos, name="api_periodos"),
    path("api/proyecto/<uuid:proyecto_id>/conteos/", api_conteos_by_proyecto, name="api_conteos"),
    path("api/proyecto/<uuid:proyecto_id>/flujos/", api_flujos_by_proyecto, name="api_flujos"),
    path("api/proyecto/<uuid:proyecto_id>/analisis/promedios/", api_analisis_promedios, name="api_analisis_promedios"),
]
