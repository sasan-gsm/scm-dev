from typing import Optional, List
from django.db.models import Q, QuerySet, Sum, F
from django.utils import timezone

from core.common.repositories import BaseRepository
from .models import (
    Invoice,
    Payment,
    ExpenseCategory,
    GeneralExpense,
    Budget,
    BudgetItem,
)


class InvoiceRepository(BaseRepository[Invoice]):
    """
    Repository for Invoice model operations.

    Provides data access operations specific to the Invoice model.
    """

    def __init__(self):
        """
        Initialize the repository with the Invoice model.
        """
        super().__init__(Invoice)

    def get_by_number(self, number: str) -> Optional[Invoice]:
        """
        Retrieve an invoice by its number.

        Args:
            number: The invoice number

        Returns:
            The invoice if found, None otherwise
        """
        try:
            return self.model_class.objects.get(number=number)
        except self.model_class.DoesNotExist:
            return None

    def get_by_supplier(self, supplier_id: int) -> QuerySet:
        """
        Get invoices for a specific supplier.

        Args:
            supplier_id: The supplier ID

        Returns:
            QuerySet of invoices for the specified supplier
        """
        return self.model_class.objects.filter(supplier_id=supplier_id)

    def get_by_status(self, status: str) -> QuerySet:
        """
        Get invoices with a specific status.

        Args:
            status: The status

        Returns:
            QuerySet of invoices with the specified status
        """
        return self.model_class.objects.filter(status=status)

    def get_by_date_range(self, start_date, end_date) -> QuerySet:
        """
        Get invoices created within a date range.

        Args:
            start_date: The start date
            end_date: The end date

        Returns:
            QuerySet of invoices within the specified date range
        """
        return self.model_class.objects.filter(
            invoice_date__gte=start_date, invoice_date__lte=end_date
        )

    def get_unpaid_invoices(self) -> QuerySet:
        """
        Get unpaid invoices.

        Returns:
            QuerySet of unpaid invoices
        """
        return self.model_class.objects.filter(status="unpaid")

    def get_overdue_invoices(self) -> QuerySet:
        """
        Get overdue invoices.

        Returns:
            QuerySet of overdue invoices
        """
        today = timezone.now().date()
        return self.model_class.objects.filter(due_date__lt=today, status="unpaid")

    def get_total_by_supplier(self) -> QuerySet:
        """
        Get total invoice amount by supplier.

        Returns:
            QuerySet of suppliers with their total invoice amount
        """
        return (
            self.model_class.objects.values("supplier", "supplier__name")
            .annotate(total_amount=Sum("total_amount"))
            .order_by("-total_amount")
        )


class PaymentRepository(BaseRepository[Payment]):
    """
    Repository for Payment model operations.

    Provides data access operations specific to the Payment model.
    """

    def __init__(self):
        """
        Initialize the repository with the Payment model.
        """
        super().__init__(Payment)

    def get_by_reference(self, reference: str) -> Optional[Payment]:
        """
        Retrieve a payment by its reference number.

        Args:
            reference: The payment reference number

        Returns:
            The payment if found, None otherwise
        """
        try:
            return self.model_class.objects.get(reference=reference)
        except self.model_class.DoesNotExist:
            return None

    def get_by_invoice(self, invoice_id: int) -> QuerySet:
        """
        Get payments for a specific invoice.

        Args:
            invoice_id: The invoice ID

        Returns:
            QuerySet of payments for the specified invoice
        """
        return self.model_class.objects.filter(invoice_id=invoice_id)

    def get_by_supplier(self, supplier_id: int) -> QuerySet:
        """
        Get payments for a specific supplier.

        Args:
            supplier_id: The supplier ID

        Returns:
            QuerySet of payments for the specified supplier
        """
        return self.model_class.objects.filter(invoice__supplier_id=supplier_id)

    def get_by_date_range(self, start_date, end_date) -> QuerySet:
        """
        Get payments created within a date range.

        Args:
            start_date: The start date
            end_date: The end date

        Returns:
            QuerySet of payments within the specified date range
        """
        return self.model_class.objects.filter(
            payment_date__gte=start_date, payment_date__lte=end_date
        )

    def get_total_by_period(self, period: str) -> QuerySet:
        """
        Get total payment amount by period (month, quarter, year).

        Args:
            period: The period type ('month', 'quarter', 'year')

        Returns:
            QuerySet of periods with their total payment amount
        """
        if period == "month":
            return (
                self.model_class.objects.annotate(
                    month=F("payment_date__month"), year=F("payment_date__year")
                )
                .values("month", "year")
                .annotate(total_amount=Sum("amount"))
                .order_by("year", "month")
            )
        elif period == "quarter":
            return (
                self.model_class.objects.annotate(
                    quarter=F("payment_date__quarter"), year=F("payment_date__year")
                )
                .values("quarter", "year")
                .annotate(total_amount=Sum("amount"))
                .order_by("year", "quarter")
            )
        elif period == "year":
            return (
                self.model_class.objects.annotate(year=F("payment_date__year"))
                .values("year")
                .annotate(total_amount=Sum("amount"))
                .order_by("year")
            )
        else:
            raise ValueError(f"Invalid period: {period}")


class ExpenseCategoryRepository(BaseRepository[ExpenseCategory]):
    """
    Repository for ExpenseCategory model operations.

    Provides data access operations specific to the ExpenseCategory model.
    """

    def __init__(self):
        """
        Initialize the repository with the ExpenseCategory model.
        """
        super().__init__(ExpenseCategory)

    def get_by_name(self, name: str) -> Optional[ExpenseCategory]:
        """
        Retrieve an expense category by its name.

        Args:
            name: The category name

        Returns:
            The expense category if found, None otherwise
        """
        try:
            return self.model_class.objects.get(name=name)
        except self.model_class.DoesNotExist:
            return None

    def get_active_categories(self) -> QuerySet:
        """
        Get active expense categories.

        Returns:
            QuerySet of active expense categories
        """
        return self.model_class.objects.filter(is_active=True)


class ExpenseRepository(BaseRepository[GeneralExpense]):
    """
    Repository for GeneralExpense model operations.

    Provides data access operations specific to the GeneralExpense model.
    """

    def __init__(self):
        """
        Initialize the repository with the GeneralExpense model.
        """
        super().__init__(GeneralExpense)

    def get_by_reference(self, reference: str) -> Optional[GeneralExpense]:
        """
        Retrieve an expense by its reference number.

        Args:
            reference: The expense reference number

        Returns:
            The expense if found, None otherwise
        """
        try:
            return self.model_class.objects.get(reference=reference)
        except self.model_class.DoesNotExist:
            return None

    def get_by_category(self, category_id: int) -> QuerySet:
        """
        Get expenses for a specific category.

        Args:
            category_id: The category ID

        Returns:
            QuerySet of expenses for the specified category
        """
        return self.model_class.objects.filter(category_id=category_id)

    def get_by_project(self, project_id: int) -> QuerySet:
        """
        Get expenses for a specific project.

        Args:
            project_id: The project ID

        Returns:
            QuerySet of expenses for the specified project
        """
        return self.model_class.objects.filter(project_id=project_id)

    def get_by_date_range(self, start_date, end_date) -> QuerySet:
        """
        Get expenses created within a date range.

        Args:
            start_date: The start date
            end_date: The end date

        Returns:
            QuerySet of expenses within the specified date range
        """
        return self.model_class.objects.filter(
            expense_date__gte=start_date, expense_date__lte=end_date
        )

    def get_total_by_category(self) -> QuerySet:
        """
        Get total expense amount by category.

        Returns:
            QuerySet of categories with their total expense amount
        """
        return (
            self.model_class.objects.values("category", "category__name")
            .annotate(total_amount=Sum("amount"))
            .order_by("-total_amount")
        )

    def get_total_by_project(self) -> QuerySet:
        """
        Get total expense amount by project.

        Returns:
            QuerySet of projects with their total expense amount
        """
        return (
            self.model_class.objects.values("project", "project__name")
            .annotate(total_amount=Sum("amount"))
            .order_by("-total_amount")
        )


class BudgetRepository(BaseRepository[Budget]):
    """
    Repository for Budget model operations.
    """

    def __init__(self):
        """
        Initialize the repository with the Budget model.
        """
        super().__init__(Budget)

    def get_by_project(self, project_id: int) -> Optional[Budget]:
        """
        Get the active budget for a specific project.

        Args:
            project_id: The project ID

        Returns:
            The active budget if found, None otherwise
        """
        try:
            return self.model_class.objects.filter(
                project_id=project_id, status="active"
            ).latest("created_at")
        except self.model_class.DoesNotExist:
            return None

    def get_by_status(self, status: str) -> QuerySet:
        """
        Get budgets with a specific status.

        Args:
            status: The status

        Returns:
            QuerySet of budgets with the specified status
        """
        return self.model_class.objects.filter(status=status)


class BudgetItemRepository(BaseRepository[BudgetItem]):
    """
    Repository for BudgetItem model operations.
    """

    def __init__(self):
        """
        Initialize the repository with the BudgetItem model.
        """
        super().__init__(BudgetItem)

    def get_by_budget(self, budget_id: int) -> QuerySet:
        """
        Get budget items for a specific budget.

        Args:
            budget_id: The budget ID

        Returns:
            QuerySet of budget items for the specified budget
        """
        return self.model_class.objects.filter(budget_id=budget_id)
