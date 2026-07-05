from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Perfil"


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ("username", "email", "is_staff", "get_role", "is_active")
    list_select_related = ("profile",)

    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, "profile") else "-"

    get_role.short_description = "Rol"
    get_role.admin_order_field = "profile__role"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
