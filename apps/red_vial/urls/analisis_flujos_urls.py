from django.urls import path

from apps.red_vial.views.analisis_flujos_views import AnalisisFlujosView

urlpatterns = [
    path(
        "proyecto/<uuid:proyecto_id>/analisis-flujos/",
        AnalisisFlujosView.as_view(),
        name="analisis_flujos",
    ),
]
