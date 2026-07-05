from django.urls import path

from apps.red_vial.views.periodo_views import (
    PeriodoCreateView,
    PeriodoDeleteView,
    PeriodoListView,
    PeriodoUpdateView,
)

urlpatterns = [
    path("proyecto/<uuid:proyecto_id>/periodos/", PeriodoListView.as_view(), name="periodos_list"),
    path(
        "proyecto/<uuid:proyecto_id>/periodos/create/",
        PeriodoCreateView.as_view(),
        name="periodo_create",
    ),
    path("periodo/<uuid:item_id>/update/", PeriodoUpdateView.as_view(), name="periodo_update"),
    path("periodo/<uuid:item_id>/delete/", PeriodoDeleteView.as_view(), name="periodo_delete"),
]
