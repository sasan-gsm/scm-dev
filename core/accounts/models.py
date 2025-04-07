from django.contrib.auth.models import AbstractUser
from django.db import models
from core.common.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _


class User(AbstractUser, TimeStampedModel):
    """
    Custom user model extends Django's AbstractUser.
    Login with username, email, or phone number.
    """

    email = models.EmailField(_("email address"), unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    department = models.ForeignKey(
        "Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    position = models.CharField(max_length=100, blank=True)
    is_manager = models.BooleanField(default=False)
    custom_permissions = models.ManyToManyField(
        "Permission",
        verbose_name=_("custom permissions"),
        blank=True,
        help_text=_("Custom permissions for this user."),
        related_name="users_with_permission",
    )

    def __str__(self):
        return self.get_full_name() or self.username

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        db_table = "users"


class Department(TimeStampedModel):
    """
    Company departments structure.
    """

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_departments",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_departments",
    )

    def __str__(self):
        return self.name

    def get_all_children(self):
        """Get all sub-departments recursively."""
        children = list(self.sub_departments.all())
        for child in list(children):
            children.extend(child.get_all_children())
        return children

    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        db_table = "departments"


class Permission(TimeStampedModel):
    """
    Custom permission model for fine-grained access control.
    Permissions can be assigned to departments or individual users.
    """

    name = models.CharField(
        max_length=100, verbose_name=_("Name"), help_text=_("Permission name")
    )
    codename = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Codename"),
        help_text=_("Unique permission identifier"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Detailed description of what this permission allows"),
    )
    is_basic = models.BooleanField(
        default=False,
        verbose_name=_("Is Basic Permission"),
        help_text=_("If True, all users in the department get this permission"),
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="permissions",
        verbose_name=_("Department"),
        help_text=_("Department this permission belongs to"),
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Permission")
        verbose_name_plural = _("Permissions")
        db_table = "permissions"
        indexes = [
            models.Index(fields=["codename"]),
            models.Index(fields=["department", "is_basic"]),
        ]
