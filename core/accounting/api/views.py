from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum

from core.accounting.models import (
    GeneralExpense as Expense,
    AccountingEntry,
    ProjectIncome,
)
from core.accounting.services import (
    ExpenseService,
    BudgetService,
    BudgetItemService,
    InvoiceService,
)
from .serializers import (
    ExpenseListSerializer,
    ExpenseDetailSerializer,
    ExpenseCreateSerializer,
    BudgetListSerializer,
    BudgetDetailSerializer,
    BudgetCreateSerializer,
    BudgetItemSerializer,
    InvoiceSerializer,
)


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for expenses.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["project", "created_by"]
    search_fields = ["expense_number", "description", "notes"]
    ordering_fields = ["date", "amount", "created_at"]
    ordering = ["-date"]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return ExpenseListSerializer
        elif self.action == "create":
            return ExpenseCreateSerializer
        return ExpenseDetailSerializer

    def get_queryset(self):
        """Get the list of expenses for this view."""
        service = ExpenseService()
        return service.get_all()

    def create(self, request, *args, **kwargs):
        """Create a new expense."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ExpenseService()
        try:
            expense = service.create(serializer.validated_data)
            return Response(
                ExpenseDetailSerializer(expense).data, status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def my_expenses(self, request):
        """Get expenses created by the current user."""
        service = ExpenseService()
        expenses = service.get_by_user(request.user.id)
        page = self.paginate_queryset(expenses)

        if page is not None:
            serializer = ExpenseListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ExpenseListSerializer(expenses, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve an expense."""
        service = ExpenseService()
        try:
            expense = service.approve_expense(pk)
            if expense:
                return Response(ExpenseDetailSerializer(expense).data)
            return Response(
                {"detail": "Expense not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject an expense."""
        service = ExpenseService()
        try:
            expense = service.reject_expense(pk)
            if expense:
                return Response(ExpenseDetailSerializer(expense).data)
            return Response(
                {"detail": "Expense not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BudgetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for budgets.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["project", "status"]
    search_fields = ["budget_number", "name", "description"]
    ordering_fields = ["start_date", "end_date", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return BudgetListSerializer
        elif self.action == "create":
            return BudgetCreateSerializer
        return BudgetDetailSerializer

    def get_queryset(self):
        """Get the list of budgets for this view."""
        service = BudgetService()
        return service.get_all()

    def create(self, request, *args, **kwargs):
        """Create a new budget."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = BudgetService()
        try:
            budget = service.create(serializer.validated_data)
            return Response(
                BudgetDetailSerializer(budget).data, status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BudgetItemListView(APIView):
    """
    API endpoint for budget items.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, budget_id):
        """Get budget items for a specific budget."""
        service = BudgetItemService()
        items = service.get_by_budget(budget_id)
        serializer = BudgetItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request, budget_id):
        """Add a new budget item."""
        data = request.data.copy()
        data["budget"] = budget_id

        serializer = BudgetItemSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        service = BudgetItemService()
        try:
            item = service.create(serializer.validated_data)
            return Response(
                BudgetItemSerializer(item).data, status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProjectExpensesView(APIView):
    """
    API endpoint for project expenses.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        """Get expenses for a specific project."""
        service = ExpenseService()
        expenses = service.get_by_project(project_id)

        # Calculate total expenses
        total = expenses.aggregate(total=Sum("amount"))["total"] or 0

        # Get budget for comparison
        budget_service = BudgetService()
        budget = budget_service.get_by_project(project_id)
        budget_amount = budget.total_amount if budget else 0

        # Get expenses by category
        categories = expenses.values("category").annotate(total=Sum("amount"))

        serializer = ExpenseListSerializer(expenses, many=True)
        return Response(
            {
                "expenses": serializer.data,
                "total": total,
                "budget": budget_amount,
                "remaining": budget_amount - total,
                "categories": categories,
            }
        )


class ExpenseSummaryView(APIView):
    """
    API endpoint for expense summary.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get expense summary."""
        service = ExpenseService()

        # Get summary by project
        project_summary = service.get_summary_by_project()

        # Get summary by category
        category_summary = service.get_summary_by_category()

        # Get summary by month
        month_summary = service.get_summary_by_month()

        return Response(
            {
                "by_project": project_summary,
                "by_category": category_summary,
                "by_month": month_summary,
            }
        )


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for invoices.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvoiceSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["project", "status"]
    search_fields = ["invoice_number", "notes"]
    ordering_fields = ["issue_date", "due_date", "amount"]
    ordering = ["-issue_date"]

    def get_queryset(self):
        """Get the list of invoices for this view."""
        service = InvoiceService()
        return service.get_all()

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        """Get overdue invoices."""
        service = InvoiceService()
        invoices = service.get_overdue_invoices()
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        """Mark an invoice as paid."""
        service = InvoiceService()
        try:
            invoice = service.mark_as_paid(pk)
            if invoice:
                return Response(InvoiceSerializer(invoice).data)
            return Response(
                {"detail": "Invoice not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
