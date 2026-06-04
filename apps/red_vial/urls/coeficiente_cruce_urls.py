from django.urls import path
from apps.red_vial.views.coeficiente_cruce_views import (
    CoeficientesCruceListView,
    CoeficienteCruceCreateView,
    CoeficienteCruceUpdateView,
    CoeficienteCruceDeleteView,
)

urlpatterns = [
    path('proyecto/<uuid:proyecto_id>/coeficientes-cruce/', CoeficientesCruceListView.as_view(), name='coeficientes_cruce_list'),
    path('coeficientes-cruce/create/', CoeficienteCruceCreateView.as_view(), name='coeficiente_cruce_create'),
    path('coeficiente-cruce/<uuid:item_id>/update/', CoeficienteCruceUpdateView.as_view(), name='coeficiente_cruce_update'),
    path('coeficiente-cruce/<uuid:item_id>/delete/', CoeficienteCruceDeleteView.as_view(), name='coeficiente_cruce_delete'),
]
