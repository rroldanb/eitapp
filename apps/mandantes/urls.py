from django.urls import path
from .views.mandantes_views import *

urlpatterns = [
    path("", mandantes_view, name="mandantes"),
    path("create/", mandante_create_view, name="mandante_create"),
    path("<uuid:mandante_id>/", mandante_detail_view, name="mandante_detail"),
    path("<uuid:mandante_id>/delete/", mandante_delete_view, name="mandante_delete"),

    path("contactos/<uuid:mandante_id>/", contactos_view, name="contactos"),
    path("contacto/<uuid:contacto_id>/", contacto_detail_view, name="contacto_detail"),
    path("contacto/<uuid:contacto_id>/delete/", contacto_delete_view, name="contacto_delete"),
    path("contacto_create/<uuid:mandante_id>/", contacto_create_view, name="contacto_create"),
]