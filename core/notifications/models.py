from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from core.common.models import TimeStampedModel


class AlertRule(TimeStampedModel):
    ALERT_TYPES = [
        ("inventory_low", _("Inventory Low")),
        ("qc_required", _("Quality Check Required")),
        ("po_received", _("Purchase Order Received")),
        ("request_approved", _("Request Approved")),
        ("custom", _("Custom")),
    ]

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    alert_type = models.CharField(
        max_length=20, choices=ALERT_TYPES, verbose_name=_("Alert Type")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_alert_rules",
        verbose_name=_("Created By"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    send_email = models.BooleanField(default=False, verbose_name=_("Send Email"))
    send_in_app = models.BooleanField(
        default=True, verbose_name=_("Send In-App Notification")
    )

    # For inventory alerts
    material = models.ForeignKey(
        "materials.Material",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="alert_rules",
        verbose_name=_("Material"),
    )

    # For custom alerts
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Content Type"),
    )
    object_id = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("Object ID")
    )
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Alert Rule")
        verbose_name_plural = _("Alert Rules")


class Notification(TimeStampedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("User"),
    )
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    message = models.TextField(verbose_name=_("Message"))
    is_read = models.BooleanField(default=False, verbose_name=_("Is Read"))
    alert_rule = models.ForeignKey(
        AlertRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name=_("Alert Rule"),
    )

    # Link to related object
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Content Type"),
    )
    object_id = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_("Object ID")
    )
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-created_at"]
