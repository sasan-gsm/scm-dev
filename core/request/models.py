from django.db import models
from django.utils.translation import gettext_lazy as _
from core.common.models import TimeStampedModel
from core.projects.models import Project
from core.materials.models import Material
from django.contrib.auth import get_user_model

User = get_user_model()


class Request(TimeStampedModel):
    """
    Request model for material requests from users.
    """

    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("pending_approval", _("Pending Approval")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
        ("in_progress", _("In Progress")),
        ("completed", _("Completed")),
        ("cancelled", _("Cancelled")),
    ]

    PRIORITY_CHOICES = [
        ("low", _("Low")),
        ("medium", _("Medium")),
        ("high", _("High")),
        ("urgent", _("Urgent")),
    ]

    number = models.CharField(
        max_length=50, unique=True, verbose_name=_("Request Number")
    )
    requester = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="requests",
        verbose_name=_("Requester"),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="requests",
        verbose_name=_("Project"),
    )
    request_date = models.DateField(verbose_name=_("Request Date"))
    required_date = models.DateField(verbose_name=_("Required Date"))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status"),
    )
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_requests",
        verbose_name=_("Approver"),
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        verbose_name=_("Priority"),
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    fulfillment_date = models.DateField(
        null=True, blank=True, verbose_name=_("Fulfillment Date")
    )

    def __str__(self):
        return f"{self.number} - {self.requester.username}"

    class Meta:
        verbose_name = _("Request")
        verbose_name_plural = _("Requests")
        db_table = "request"


class RequestItem(TimeStampedModel):
    """
    Individual items within a request.
    """

    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("fulfilled", _("Fulfilled")),
        ("partially_fulfilled", _("Partially Fulfilled")),
        ("cancelled", _("Cancelled")),
    ]

    request = models.ForeignKey(
        Request,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Request"),
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name="request_items",
        verbose_name=_("Material"),
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Quantity")
    )
    quantity_fulfilled = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name=_("Quantity Fulfilled")
    )
    is_fulfilled = models.BooleanField(default=False, verbose_name=_("Is Fulfilled"))
    fulfillment_date = models.DateField(
        null=True, blank=True, verbose_name=_("Fulfillment Date")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    def __str__(self):
        return f"{self.request.number} - {self.material.name} ({self.quantity})"

    class Meta:
        verbose_name = _("Request Item")
        verbose_name_plural = _("Request Items")
        db_table = "request_item"
