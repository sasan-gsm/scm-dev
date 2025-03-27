from django.db import models
from django.utils.translation import gettext_lazy as _
from core.common.models import TimeStampedModel
from core.inventory.models import InventoryTransaction
from core.projects.models import Project
from core.materials.models import Material
from django.contrib.auth import get_user_model


User = get_user_model()


class QualityStandard(TimeStampedModel):
    """
    Quality standards and criteria for quality checks.
    """

    name = models.CharField(max_length=255, verbose_name=_("Name"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Standard Code"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    criteria = models.TextField(blank=True, verbose_name=_("Criteria"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = _("Quality Standard")
        verbose_name_plural = _("Quality Standards")
        db_table = "quality_standards"


class QualityCheck(TimeStampedModel):
    """
    Quality check for materials and inventory transactions.
    """

    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("submitted", _("Submitted")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
        ("completed", _("Completed")),
        ("cancelled", _("Cancelled")),
    ]

    check_number = models.CharField(
        max_length=50, unique=True, verbose_name=_("Check Number")
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="quality_checks",
        verbose_name=_("Project"),
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name="quality_checks",
        verbose_name=_("Material"),
    )
    inventory_transaction = models.ForeignKey(
        InventoryTransaction,
        on_delete=models.CASCADE,
        related_name="quality_checks",
        verbose_name=_("Inventory Transaction"),
        null=True,
        blank=True,
    )
    check_date = models.DateTimeField(verbose_name=_("Check Date"))
    inspector = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="inspected_checks",
        verbose_name=_("Inspector"),
    )
    location = models.CharField(max_length=255, blank=True, verbose_name=_("Location"))
    batch_number = models.CharField(
        max_length=100, blank=True, verbose_name=_("Batch Number")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status"),
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    def __str__(self):
        return f"{self.check_number} - {self.material.name}"

    class Meta:
        verbose_name = _("Quality Check")
        verbose_name_plural = _("Quality Checks")
        db_table = "quality_checks"


class QualityCheckItem(TimeStampedModel):
    """
    Individual quality check items for a quality check.
    """

    quality_check = models.ForeignKey(
        QualityCheck,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Quality Check"),
    )
    standard = models.ForeignKey(
        QualityStandard,
        on_delete=models.PROTECT,
        related_name="check_items",
        verbose_name=_("Quality Standard"),
    )
    result = models.CharField(max_length=255, blank=True, verbose_name=_("Result"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    is_passed = models.BooleanField(default=False, verbose_name=_("Is Passed"))

    def __str__(self):
        return f"{self.quality_check.check_number} - {self.standard.name}"

    class Meta:
        verbose_name = _("Quality Check Item")
        verbose_name_plural = _("Quality Check Items")
        db_table = "quality_check_items"
