from django.urls import path

from apps.red_vial.views.coeficiente_cruce_views import (
    coeficientes_cruce_list_view,
    coeficiente_cruce_create_view,
    coeficiente_cruce_update_view,
    coeficiente_cruce_delete_view,
)

urlpatterns = [
    path('coeficientes-cruce/', coeficientes_cruce_list_view, name='coeficientes_cruce_list'),
    path('coeficientes-cruce/create/', coeficiente_cruce_create_view, name='coeficiente_cruce_create'),
    path('coeficiente-cruce/<uuid:item_id>/update/', coeficiente_cruce_update_view, name='coeficiente_cruce_update'),
    path('coeficiente-cruce/<uuid:item_id>/delete/', coeficiente_cruce_delete_view, name='coeficiente_cruce_delete'),
]
