from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from core.inventory.models import InventoryTransaction
from core.projects.models import Project


class AccountingEntry(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
    ]

    inventory_transaction = models.OneToOneField(
        InventoryTransaction,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="accounting_entry",
        verbose_name=_("Inventory Transaction"),
    )
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Unit Price")
    )
    total_price = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name=_("Total Price")
    )
    currency = models.CharField(max_length=3, default="IRR", verbose_name=_("Currency"))
    set_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="set_accounting_entries",
        verbose_name=_("Set By"),
    )
    set_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Set Date"))
    approved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_accounting_entries",
        verbose_name=_("Approved By"),
    )
    approved_date = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Approved Date")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    def __str__(self):
        return f"AE-{self.id}"

    class Meta:
        verbose_name = _("Accounting Entry")
        verbose_name_plural = _("Accounting Entries")


class GeneralExpense(TimeStampedModel):
    ALLOCATION_TYPES = [
        ("project_specific", _("Project Specific")),
        ("weight_based", _("Weight Based")),
    ]

    description = models.CharField(max_length=255, verbose_name=_("Description"))
    amount = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name=_("Amount")
    )
    expense_date = models.DateField(verbose_name=_("Expense Date"))
    allocation_type = models.CharField(
        max_length=20, choices=ALLOCATION_TYPES, verbose_name=_("Allocation Type")
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="specific_expenses",
        verbose_name=_("Project"),
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_expenses",
        verbose_name=_("Created By"),
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_expenses",
        verbose_name=_("Approved By"),
    )

    def __str__(self):
        return f"{self.description} - {self.amount}"

    class Meta:
        verbose_name = _("General Expense")
        verbose_name_plural = _("General Expenses")


class ProjectIncome(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="incomes",
        verbose_name=_("Project"),
    )
    description = models.CharField(max_length=255, verbose_name=_("Description"))
    amount = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name=_("Amount")
    )
    income_date = models.DateField(verbose_name=_("Income Date"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_incomes",
        verbose_name=_("Created By"),
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_incomes",
        verbose_name=_("Approved By"),
    )

    def __str__(self):
        return f"{self.project.number} - {self.description} - {self.amount}"

    class Meta:
        verbose_name = _("Project Income")
        verbose_name_plural = _("Project Incomes")
