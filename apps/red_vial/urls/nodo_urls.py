from django.urls import path
from ..views.nodo_views import *


    # ========== NODO URLs ==========
urlpatterns = [    
    path("proyecto/<uuid:proyecto_id>/nodos/", nodos_list_view, name="nodos_list"),
    path("proyecto/<uuid:proyecto_id>/nodos/create/", nodo_create_view, name="nodo_create"),
    path("nodo/<uuid:nodo_id>/", nodo_detail_view, name="nodo_detail"),
    path("nodo/<uuid:nodo_id>/update/", nodo_update_view, name="nodo_update"),
    path("nodo/<uuid:nodo_id>/delete/", nodo_delete_view, name="nodo_delete"),
    path("<uuid:proyecto_id>/nodos/", proyecto_nodos_view, name="proyecto_nodos"), #candidato
    ]
    
