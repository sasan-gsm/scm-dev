from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from core.common.models import TimeStampedModel
from django.contrib.auth import get_user_model


User = get_user_model()


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
        db_table = "alert_rules"


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
    # Add notification_type field to match serializer and repository
    notification_type = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Notification Type")
    )
    read_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Read At"))

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
        db_table = "notifications"


class NotificationSetting(TimeStampedModel):
    """User notification preferences for different notification types."""

    NOTIFICATION_TYPES = [
        ("inventory_low", _("Inventory Low")),
        ("qc_required", _("Quality Check Required")),
        ("po_received", _("Purchase Order Received")),
        ("request_approved", _("Request Approved")),
        ("system", _("System Notifications")),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_settings",
        verbose_name=_("User"),
    )
    notification_type = models.CharField(
        max_length=50, choices=NOTIFICATION_TYPES, verbose_name=_("Notification Type")
    )
    email_enabled = models.BooleanField(default=True, verbose_name=_("Email Enabled"))
    push_enabled = models.BooleanField(default=True, verbose_name=_("Push Enabled"))
    in_app_enabled = models.BooleanField(default=True, verbose_name=_("In-App Enabled"))

    class Meta:
        verbose_name = _("Notification Setting")
        verbose_name_plural = _("Notification Settings")
        db_table = "notification_settings"
        unique_together = ["user", "notification_type"]

    def __str__(self):
        return f"{self.user.username} - {self.get_notification_type_display()}"


class NotificationTemplate(TimeStampedModel):
    """Templates for different types of notifications."""

    code = models.CharField(max_length=100, unique=True, verbose_name=_("Code"))
    notification_type = models.CharField(
        max_length=50, verbose_name=_("Notification Type")
    )
    subject = models.CharField(max_length=200, verbose_name=_("Subject"))
    body = models.TextField(verbose_name=_("Body"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        verbose_name = _("Notification Template")
        verbose_name_plural = _("Notification Templates")
        db_table = "notification_templates"

    def __str__(self):
        return self.code
