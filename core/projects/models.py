from django.db import models
from django.utils.translation import gettext_lazy as _
from core.common.models import TimeStampedModel
from django.contrib.auth import get_user_model


User = get_user_model()


class Project(TimeStampedModel):
    STATUS_CHOICES = [
        ("planning", _("Planning")),
        ("active", _("Active")),
        ("on_hold", _("On Hold")),
        ("completed", _("Completed")),
        ("cancelled", _("Cancelled")),
    ]

    name = models.CharField(max_length=200, verbose_name=_("Name"))
    number = models.CharField(
        max_length=50, unique=True, verbose_name=_("Project Number")
    )
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("End Date"))
    weight_factor = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Weight Factor")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planning",
        verbose_name=_("Status"),
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="managed_projects",
        verbose_name=_("Project Manager"),
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))

    def __str__(self):
        return f"{self.number} - {self.name}"

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        db_table = "project"
