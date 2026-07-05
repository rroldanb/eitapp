from django.urls import path

from apps.red_vial.views.arco_views import (
    ArcoCreateView,
    ArcoDeleteView,
    ArcosListView,
    ArcoUpdateView,
)

urlpatterns = [
    path("proyecto/<uuid:proyecto_id>/arcos/", ArcosListView.as_view(), name="arcos_list"),
    path("proyecto/<uuid:proyecto_id>/arcos/create/", ArcoCreateView.as_view(), name="arco_create"),
    path("arco/<uuid:item_id>/update/", ArcoUpdateView.as_view(), name="arco_update"),
    path("arco/<uuid:item_id>/delete/", ArcoDeleteView.as_view(), name="arco_delete"),
]
