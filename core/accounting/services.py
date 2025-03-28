from typing import Dict, List, Optional, Any
from django.db import transaction
from django.utils import timezone

from .repositories import (
    InvoiceRepository,
    ExpenseRepository,  # This should be updated if the repository name is different
    BudgetRepository,
    BudgetItemRepository,
)
from .models import Invoice, GeneralExpense as Expense, Budget, BudgetItem


class ExpenseService:
    """Service for expense operations."""

    def __init__(self):
        self.repository = ExpenseRepository()

    def get_all(self):
        """Get all expenses."""
        return self.repository.get_all()

    def get_by_id(self, expense_id):
        """Get expense by ID."""
        return self.repository.get_by_id(expense_id)

    def get_by_user(self, user_id):
        """Get expenses created by a specific user."""
        return self.repository.get_by_user(user_id)

    def get_by_project(self, project_id):
        """Get expenses for a specific project."""
        return self.repository.get_by_project(project_id)

    def get_summary_by_project(self):
        """Get expense summary by project."""
        return self.repository.get_total_by_project()

    def get_summary_by_category(self):
        """Get expense summary by category."""
        return self.repository.get_total_by_category()

    def get_summary_by_month(self):
        """Get expense summary by month."""
        # Implementation depends on your specific requirements
        pass

    @transaction.atomic
    def create(self, data):
        """Create a new expense."""
        return self.repository.create(data)

    @transaction.atomic
    def approve_expense(self, expense_id):
        """Approve an expense."""
        expense = self.repository.get_by_id(expense_id)
        if not expense:
            return None

        # Update expense status logic here
        return expense

    @transaction.atomic
    def reject_expense(self, expense_id):
        """Reject an expense."""
        expense = self.repository.get_by_id(expense_id)
        if not expense:
            return None

        # Update expense status logic here
        return expense


class BudgetService:
    """Service for budget operations."""

    def __init__(self):
        self.repository = BudgetRepository()

    def get_all(self):
        """Get all budgets."""
        return self.repository.get_all()

    def get_by_id(self, budget_id):
        """Get budget by ID."""
        return self.repository.get_by_id(budget_id)

    def get_by_project(self, project_id):
        """Get budget for a specific project."""
        return self.repository.get_by_project(project_id)

    @transaction.atomic
    def create(self, data):
        """Create a new budget."""
        return self.repository.create(data)


class BudgetItemService:
    """Service for budget item operations."""

    def __init__(self):
        self.repository = BudgetItemRepository()

    def get_by_budget(self, budget_id):
        """Get budget items for a specific budget."""
        return self.repository.get_by_budget(budget_id)

    @transaction.atomic
    def create(self, data):
        """Create a new budget item."""
        return self.repository.create(data)


class InvoiceService:
    """Service for invoice operations."""

    def __init__(self):
        self.repository = InvoiceRepository()

    def get_all(self):
        """Get all invoices."""
        return self.repository.get_all()

    def get_by_id(self, invoice_id):
        """Get invoice by ID."""
        return self.repository.get_by_id(invoice_id)

    def get_overdue_invoices(self):
        """Get overdue invoices."""
        return self.repository.get_overdue_invoices()

    @transaction.atomic
    def mark_as_paid(self, invoice_id):
        """Mark an invoice as paid."""
        invoice = self.repository.get_by_id(invoice_id)
        if not invoice:
            return None

        invoice.status = "paid"
        invoice.save()
        return invoice
