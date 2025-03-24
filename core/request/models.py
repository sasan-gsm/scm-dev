from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from core.projects.models import Project
from core.materials.models import Material


class RequestList(TimeStampedModel):
    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("submitted", _("Submitted")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
        ("completed", _("Completed")),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="request_lists",
        verbose_name=_("Project"),
    )
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_requests",
        verbose_name=_("Created By"),
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name=_("Status")
    )
    approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="approved_requests",
        verbose_name=_("Approved By"),
    )
    approved_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Approved At")
    )

    def __str__(self):
        return f"{self.project.number} - {self.title}"

    class Meta:
        verbose_name = _("Request List")
        verbose_name_plural = _("Request Lists")


class RequestItem(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("procured", _("Procured")),
        ("received", _("Received")),
        ("distributed", _("Distributed")),
    ]

    request_list = models.ForeignKey(
        RequestList,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Request List"),
    )
    material = models.ForeignKey(
        Material, on_delete=models.PROTECT, verbose_name=_("Material")
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Quantity")
    )
    technical_specs = models.JSONField(
        default=dict, verbose_name=_("Technical Specifications")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    def __str__(self):
        return f"{self.material.name} - {self.quantity}"

    class Meta:
        verbose_name = _("Request Item")
        verbose_name_plural = _("Request Items")
