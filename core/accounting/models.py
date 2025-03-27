from django.db import models
from django.utils.translation import gettext_lazy as _
from core.common.models import TimeStampedModel
from core.inventory.models import InventoryTransaction
from core.projects.models import Project
from django.contrib.auth import get_user_model


User = get_user_model()


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
        db_table = "accounting_entry"


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
        db_table = "general_expense"


class ExpenseCategory(TimeStampedModel):
    """
    Categories for classifying expenses.
    """

    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
        verbose_name=_("Parent Category"),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Expense Category")
        verbose_name_plural = _("Expense Categories")
        db_table = "expense_category"


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
        db_table = "project_income"


class Budget(TimeStampedModel):
    """
    Budget model for tracking project or department budgets.
    """

    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("active", _("Active")),
        ("closed", _("Closed")),
    ]

    budget_number = models.CharField(
        max_length=50, unique=True, verbose_name=_("Budget Number")
    )
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="budgets",
        verbose_name=_("Project"),
    )
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    total_amount = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name=_("Total Amount")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status"),
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_budgets",
        verbose_name=_("Created By"),
    )

    def __str__(self):
        return f"{self.budget_number} - {self.name}"

    class Meta:
        verbose_name = _("Budget")
        verbose_name_plural = _("Budgets")
        db_table = "budget"


class BudgetItem(TimeStampedModel):
    """
    Individual line items within a budget.
    """

    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Budget"),
    )
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    amount = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name=_("Amount")
    )

    def __str__(self):
        return f"{self.budget.budget_number} - {self.name}"

    class Meta:
        verbose_name = _("Budget Item")
        verbose_name_plural = _("Budget Items")
        db_table = "budget_item"


class Invoice(TimeStampedModel):
    """
    Invoice model for tracking invoices from suppliers.
    """

    STATUS_CHOICES = [
        ("unpaid", _("Unpaid")),
        ("paid", _("Paid")),
        ("cancelled", _("Cancelled")),
    ]

    number = models.CharField(
        max_length=50, unique=True, verbose_name=_("Invoice Number")
    )
    supplier = models.ForeignKey(
        "procurement.Supplier",  # Assuming this is the correct path
        on_delete=models.PROTECT,
        related_name="invoices",
        verbose_name=_("Supplier"),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="invoices",
        verbose_name=_("Project"),
    )
    invoice_date = models.DateField(verbose_name=_("Invoice Date"))
    due_date = models.DateField(verbose_name=_("Due Date"))
    amount = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name=_("Amount")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="unpaid",
        verbose_name=_("Status"),
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    def __str__(self):
        return f"{self.number} - {self.supplier.name}"

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        db_table = "invoice"


class Payment(TimeStampedModel):
    """
    Payment model for tracking payments made to suppliers.
    """

    reference = models.CharField(
        max_length=50, unique=True, verbose_name=_("Payment Reference")
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name=_("Invoice"),
    )
    amount = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name=_("Amount")
    )
    payment_date = models.DateField(verbose_name=_("Payment Date"))
    payment_method = models.CharField(max_length=50, verbose_name=_("Payment Method"))
    transaction_id = models.CharField(
        max_length=100, blank=True, verbose_name=_("Transaction ID")
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_payments",
        verbose_name=_("Created By"),
    )

    def __str__(self):
        return f"{self.reference} - {self.invoice.number}"

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        db_table = "payment"
