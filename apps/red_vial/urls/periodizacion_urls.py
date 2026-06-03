from django.urls import path
from apps.red_vial.views.periodizacion_views import (
    PeriodizacionListView,
    PeriodizacionUpdateView,
    PeriodizacionDeleteView,
)

urlpatterns = [
    path('proyecto/<uuid:proyecto_id>/periodizacion/', PeriodizacionListView.as_view(), name='periodizacion_list'),
    path('proyecto/<uuid:proyecto_id>/periodizacion/generar/', PeriodizacionListView.as_view(), name='periodizacion_generar'),
    path('periodizacion/<uuid:item_id>/update/', PeriodizacionUpdateView.as_view(), name='periodizacion_update'),
    path('periodizacion/<uuid:item_id>/delete/', PeriodizacionDeleteView.as_view(), name='periodizacion_delete'),
]
