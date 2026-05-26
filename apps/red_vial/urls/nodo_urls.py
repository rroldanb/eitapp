from django.urls import path
from ..views.nodo_views_cbv import (
    NodosListView,
    NodosCreateView,
    NodosUpdateView,
    NodosDeleteView,
    NodosBulkUpdateView,
)


# ========== NODO URLs (CBV DRY) ==========
urlpatterns = [
    path("proyecto/<uuid:proyecto_id>/nodos/", NodosListView.as_view(), name="nodos_list"),
    path("proyecto/<uuid:proyecto_id>/nodos/create/", NodosCreateView.as_view(), name="nodo_create"),
    path("nodo/<uuid:item_id>/update/", NodosUpdateView.as_view(), name="nodo_update"),
    path("nodo/<uuid:item_id>/delete/", NodosDeleteView.as_view(), name="nodo_delete"),
    path("proyecto/<uuid:proyecto_id>/nodos/bulk-update/", NodosBulkUpdateView.as_view(), name="nodos_bulk_update"),
]
    
