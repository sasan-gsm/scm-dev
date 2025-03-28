from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"expenses", views.ExpenseViewSet, basename="expense")
router.register(r"budgets", views.BudgetViewSet, basename="budget")
router.register(r"invoices", views.InvoiceViewSet, basename="invoice")

app_name = "accounting"

urlpatterns = [
    path("", include(router.urls)),
    # Add any custom endpoints here
    path(
        "budget-items/<int:budget_id>/",
        views.BudgetItemListView.as_view(),
        name="budget-items",
    ),
    path(
        "project-expenses/<int:project_id>/",
        views.ProjectExpensesView.as_view(),
        name="project-expenses",
    ),
    path(
        "expense-summary/", views.ExpenseSummaryView.as_view(), name="expense-summary"
    ),
]
