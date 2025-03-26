from django.db import models
from django.utils.translation import gettext_lazy as _
from core.common.models import TimeStampedModel
from core.inventory.models import InventoryTransaction
from django.contrib.auth import get_user_model


User = get_user_model()


class QualityCheck(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("in_progress", _("In Progress")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
    ]

    inventory_transaction = models.ForeignKey(
        InventoryTransaction,
        on_delete=models.CASCADE,
        related_name="quality_checks",
        verbose_name=_("Inventory Transaction"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
    )
    checked_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="quality_checks",
        verbose_name=_("Checked By"),
    )
    check_date = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Check Date")
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    requires_notification = models.BooleanField(
        default=False, verbose_name=_("Requires Notification")
    )

    def __str__(self):
        return f"QC-{self.id} - {self.inventory_transaction.material.name}"

    class Meta:
        verbose_name = _("Quality Check")
        verbose_name_plural = _("Quality Checks")
        db_table = "quality_checks"
