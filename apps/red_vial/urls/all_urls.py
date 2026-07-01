from django.urls import path, include
from django.contrib.auth.decorators import login_required
from ..views.red_vial_views import *
from ..views.trafico_views import *

urlpatterns = [

    # ========== COEFICIENTE URLs ==========
    path("coeficientes/", coeficientes_list_view, name="coeficientes_list"),
    path("coeficientes/create/", coeficiente_create_view, name="coeficiente_create"),

    # ========== PERIODO URLs ==========
    path("periodos/", periodos_list_view, name="periodos_list"),
    path("periodos/create/", periodo_create_view, name="periodo_create"),
    path("periodo/<uuid:periodo_id>/update/", periodo_update_view, name="periodo_update"),
    path("periodo/<uuid:periodo_id>/delete/", periodo_delete_view, name="periodo_delete"),
]
