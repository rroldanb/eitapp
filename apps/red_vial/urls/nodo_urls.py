from django.urls import path
from ..views.nodo_views_cbv import (
    NodosListView,
    NodosCreateView,
    NodosUpdateView,
    NodosDeleteView,
    NodosBulkUpdateView,
    nodo_upload_image_view,
    nodo_delete_image_view,
    nodo_upload_plano_view,
    nodo_delete_plano_view,
    nodo_images_json_view,
)


# ========== NODO URLs (CBV DRY) ==========
urlpatterns = [
    path("proyecto/<uuid:proyecto_id>/nodos/", NodosListView.as_view(), name="nodos_list"),
    path("proyecto/<uuid:proyecto_id>/nodos/create/", NodosCreateView.as_view(), name="nodo_create"),
    path("nodo/<uuid:item_id>/update/", NodosUpdateView.as_view(), name="nodo_update"),
    path("nodo/<uuid:item_id>/delete/", NodosDeleteView.as_view(), name="nodo_delete"),
    path("proyecto/<uuid:proyecto_id>/nodos/bulk-update/", NodosBulkUpdateView.as_view(), name="nodos_bulk_update"),
    path("nodo/<uuid:item_id>/upload-image/", nodo_upload_image_view, name="nodo_upload_image"),
    path("nodo/<uuid:item_id>/delete-image/", nodo_delete_image_view, name="nodo_delete_image"),
    path("nodo/<uuid:item_id>/upload-plano/", nodo_upload_plano_view, name="nodo_upload_plano"),
    path("nodo/<uuid:item_id>/delete-plano/", nodo_delete_plano_view, name="nodo_delete_plano"),
    path("nodo/<uuid:item_id>/images/", nodo_images_json_view, name="nodo_images_json"),
]
    
