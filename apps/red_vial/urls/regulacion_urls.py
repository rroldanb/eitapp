from django.urls import path

from apps.red_vial.views.regulacion_views import (
    RegulacionesListView,
    RegulacionCreateView,
    RegulacionUpdateView,
    RegulacionDeleteView,
)

urlpatterns = [
    path('proyecto/<uuid:proyecto_id>/regulaciones/', RegulacionesListView.as_view(), name='regulaciones_list'),
    path('regulaciones/create/', RegulacionCreateView.as_view(), name='regulacion_create'),
    path('regulacion/<uuid:item_id>/update/', RegulacionUpdateView.as_view(), name='regulacion_update'),
    path('regulacion/<uuid:item_id>/delete/', RegulacionDeleteView.as_view(), name='regulacion_delete'),
]
