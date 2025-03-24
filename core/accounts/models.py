from django.contrib.auth.models import AbstractUser
from django.db import models
from core.common.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _


class User(AbstractUser, TimeStampedModel):
    """
    Custom user model that extends Django's AbstractUser.
    Allows login with username, email, or phone number.
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

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.get_full_name() or self.username


class Department(TimeStampedModel):
    """
    Represents company departments in a hierarchical structure.
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
