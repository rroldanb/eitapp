from django.urls import path

from ..views.arco_views_cbv import (
    ArcosListView,
    ArcosCreateView,
    ArcosUpdateView,
    ArcosDeleteView,
    ArcosBulkUpdateView,
)

urlpatterns = [
        # ========== ARCO URLs ==========
    path("proyecto/<uuid:proyecto_id>/arcos/", ArcosListView.as_view(), name="arcos_list"),
    path("proyecto/<uuid:proyecto_id>/arcos/create/", ArcosCreateView.as_view(), name="arco_create"),
    path("arco/<uuid:item_id>/update/", ArcosUpdateView.as_view(), name="arco_update"),
    path("arco/<uuid:item_id>/delete/", ArcosDeleteView.as_view(), name="arco_delete"),
    path("proyecto/<uuid:proyecto_id>/arcos/bulk-update/", ArcosBulkUpdateView.as_view(), name="arcos_bulk_update"),
]
