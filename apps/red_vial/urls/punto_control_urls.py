from django.urls import path

from apps.red_vial.views.punto_control_views import (
    PuntosControlListView,
    PuntosControlCreateView,
    PuntosControlUpdateView,
    PuntosControlDeleteView,
)

urlpatterns = [
    path('proyecto/<uuid:proyecto_id>/puntos-control/', PuntosControlListView.as_view(), name='puntos_control_list'),
    path('proyecto/<uuid:proyecto_id>/puntos-control/create/', PuntosControlCreateView.as_view(), name='punto_control_create'),
    path('punto-control/<uuid:item_id>/update/', PuntosControlUpdateView.as_view(), name='punto_control_update'),
    path('punto-control/<uuid:item_id>/delete/', PuntosControlDeleteView.as_view(), name='punto_control_delete'),
]
