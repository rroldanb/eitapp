from django.urls import path

from . import views

app_name = "theme"

urlpatterns = [
    path("", views.base_view, name="base"),
]
