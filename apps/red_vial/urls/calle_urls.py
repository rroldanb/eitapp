from django.urls import path

from apps.red_vial.views.calle_views import (
    CallesListView,
    CallesCreateView,
    CallesUpdateView,
    CallesDeleteView,
    CallesBulkUpdateView,
)

# ========== CALLE URLs ==========
urlpatterns = [
    path('proyecto/<uuid:proyecto_id>/calles/', CallesListView.as_view(), name='calles_list'),
    path('proyecto/<uuid:proyecto_id>/calles/create/', CallesCreateView.as_view(), name='calle_create'),
    path('calle/<uuid:item_id>/update/', CallesUpdateView.as_view(), name='calle_update'),
    path('calle/<uuid:item_id>/delete/', CallesDeleteView.as_view(), name='calle_delete'),
    path('proyecto/<uuid:proyecto_id>/calles/bulk-update/', CallesBulkUpdateView.as_view(), name='calles_bulk_update'),
]
