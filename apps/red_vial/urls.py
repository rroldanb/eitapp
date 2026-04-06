from django.urls import path
from .views.red_vial_views import *
from .views.trafico_views import *

urlpatterns = [
    # ========== CALLE URLs ==========
    path("proyecto/<uuid:proyecto_id>/calles/", calles_list_view, name="calles_list"),
    path("proyecto/<uuid:proyecto_id>/calles/create/", calle_create_view, name="calle_create"),
    path("calle/<uuid:calle_id>/", calle_detail_view, name="calle_detail"),
    path("calle/<uuid:calle_id>/update/", calle_update_view, name="calle_update"),
    path("calle/<uuid:calle_id>/delete/", calle_delete_view, name="calle_delete"),

    # ========== NODO URLs ==========
    path("proyecto/<uuid:proyecto_id>/nodos/", nodos_list_view, name="nodos_list"),
    path("proyecto/<uuid:proyecto_id>/nodos/create/", nodo_create_view, name="nodo_create"),
    path("nodo/<uuid:nodo_id>/", nodo_detail_view, name="nodo_detail"),
    path("nodo/<uuid:nodo_id>/update/", nodo_update_view, name="nodo_update"),
    path("nodo/<uuid:nodo_id>/delete/", nodo_delete_view, name="nodo_delete"),

    # ========== ARCO URLs ==========
    path("proyecto/<uuid:proyecto_id>/arcos/", arcos_list_view, name="arcos_list"),
    path("proyecto/<uuid:proyecto_id>/arcos/create/", arco_create_view, name="arco_create"),
    path("arco/<uuid:arco_id>/", arco_detail_view, name="arco_detail"),
    path("arco/<uuid:arco_id>/update/", arco_update_view, name="arco_update"),
    path("arco/<uuid:arco_id>/delete/", arco_delete_view, name="arco_delete"),

    # ========== MOVIMIENTO URLs ==========
    path("movimientos/", movimientos_list_view, name="movimientos_list"),
    path("movimientos/create/", movimiento_create_view, name="movimiento_create"),

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
