from django.urls import path

from apps.red_vial.views.calle_views import (
    CalleCreateView,
    CalleDeleteView,
    CalleListView,
    CalleUpdateView,
)

urlpatterns = [
    path("proyecto/<uuid:proyecto_id>/calles/", CalleListView.as_view(), name="calles_list"),
    path(
        "proyecto/<uuid:proyecto_id>/calles/create/", CalleCreateView.as_view(), name="calle_create"
    ),
    path("calle/<uuid:item_id>/update/", CalleUpdateView.as_view(), name="calle_update"),
    path("calle/<uuid:item_id>/delete/", CalleDeleteView.as_view(), name="calle_delete"),
]
