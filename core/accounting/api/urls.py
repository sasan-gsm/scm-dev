from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from . import es_views

router = DefaultRouter()
router.register(r"expenses", views.ExpenseViewSet, basename="expense")
router.register(r"budgets", views.BudgetViewSet, basename="budget")
router.register(r"invoices", views.InvoiceViewSet, basename="invoice")

# Elasticsearch document viewsets
es_router = DefaultRouter()
es_router.register(
    r"search/invoices", es_views.InvoiceDocumentViewSet, basename="invoice-search"
)
es_router.register(
    r"search/payments", es_views.PaymentDocumentViewSet, basename="payment-search"
)

app_name = "accounting"

urlpatterns = [
    path("", include(router.urls)),
    path("", include(es_router.urls)),  # Include Elasticsearch endpoints
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
