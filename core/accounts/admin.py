from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Department


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "email", "phone_number")},
        ),
        (_("Organization"), {"fields": ("department", "position", "is_manager")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = (
        "username",
        "email",
        "phone_number",
        "first_name",
        "last_name",
        "department",
        "is_staff",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "department")
    search_fields = ("username", "first_name", "last_name", "email", "phone_number")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin configuration for the Department model."""

    list_display = ("name", "code", "manager", "parent")
    list_filter = ("parent",)
    search_fields = ("name", "code", "manager__username")
    autocomplete_fields = ["manager", "parent"]
