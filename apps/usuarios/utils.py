from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from .models import Role


def get_user_role(user):
    if not user.is_authenticated:
        return None
    if hasattr(user, "profile"):
        return user.profile.role
    return Role.ENCUESTADOR


def user_has_role(user, min_role):
    return user.is_authenticated and get_user_role(user) >= min_role


class RoleRequiredMixin(UserPassesTestMixin):
    min_role = Role.ENCUESTADOR

    def test_func(self):
        return user_has_role(self.request.user, self.min_role)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()
