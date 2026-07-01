from django.urls import path

from apps.red_vial.views.punto_control_views import (
    PuntosControlListView,
    PuntoControlCreateView,
    PuntoControlUpdateView,
    PuntoControlDeleteView,
)

urlpatterns = [
    path('proyecto/<uuid:proyecto_id>/puntos-control/', PuntosControlListView.as_view(), name='puntos_control_list'),
    path('proyecto/<uuid:proyecto_id>/puntos-control/create/', PuntoControlCreateView.as_view(), name='punto_control_create'),
    path('punto-control/<uuid:item_id>/update/', PuntoControlUpdateView.as_view(), name='punto_control_update'),
    path('punto-control/<uuid:item_id>/delete/', PuntoControlDeleteView.as_view(), name='punto_control_delete'),
]
