from django.urls import path

from ..views.red_vial_views import coeficiente_create_view, coeficientes_list_view

urlpatterns = [
    path("coeficientes/", coeficientes_list_view, name="coeficientes_list"),
    path("coeficientes/create/", coeficiente_create_view, name="coeficiente_create"),
]
