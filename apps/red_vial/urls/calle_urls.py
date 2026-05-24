from django.urls import path

from apps.red_vial.views.calle_views import (
    calles_list_view,
    calle_create_view,
    calle_update_view,
    calle_delete_view,
    calles_bulk_update_view,
)

# ========== CALLE URLs ==========
urlpatterns = [
    path('proyecto/<uuid:proyecto_id>/calles/', calles_list_view, name='calles_list'),
    path('proyecto/<uuid:proyecto_id>/calles/create/', calle_create_view, name='calle_create'),
    path('calle/<uuid:calle_id>/update/', calle_update_view, name='calle_update'),
    path('calle/<uuid:calle_id>/delete/', calle_delete_view, name='calle_delete'),
    path('proyecto/<uuid:proyecto_id>/calles/bulk-update/', calles_bulk_update_view, name='calles_bulk_update'),
]
