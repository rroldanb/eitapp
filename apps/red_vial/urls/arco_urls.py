from django.urls import path, include
from django.contrib.auth.decorators import login_required

from ..views.arco_views import *

urlpatterns = [
        # ========== ARCO URLs ==========
    path("proyecto/<uuid:proyecto_id>/arcos/", arcos_list_view, name="arcos_list"),
    path("proyecto/<uuid:proyecto_id>/arcos/create/", arco_create_view, name="arco_create"),
    path("arco/<uuid:arco_id>/", arco_detail_view, name="arco_detail"),
    path("arco/<uuid:arco_id>/update/", arco_update_view, name="arco_update"),
    path("arco/<uuid:arco_id>/delete/", arco_delete_view, name="arco_delete"),
]
