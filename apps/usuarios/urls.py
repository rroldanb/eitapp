from django.urls import path
from .views import (
    admin_create_user_view,
    user_management_view,
    user_toggle_active_view,
    user_change_role_view,
    user_change_password_view,
)

urlpatterns = [
    path('crear/', admin_create_user_view, name='admin_create_user'),
    path('', user_management_view, name='user_management'),
    path('<int:user_id>/toggle-active/', user_toggle_active_view, name='user_toggle_active'),
    path('<int:user_id>/change-role/', user_change_role_view, name='user_change_role'),
    path('<int:user_id>/change-password/', user_change_password_view, name='user_change_password'),
]
