from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SupplierViewSet,
    SupplierContactViewSet,
    PurchaseOrderViewSet,
    PurchaseOrderItemViewSet,
)

app_name = "procurement"

router = DefaultRouter()
router.register(r"suppliers", SupplierViewSet, basename="supplier")
router.register(
    r"supplier-contacts", SupplierContactViewSet, basename="supplier-contact"
)
router.register(r"purchase-orders", PurchaseOrderViewSet, basename="purchase-order")
router.register(
    r"purchase-order-items", PurchaseOrderItemViewSet, basename="purchase-order-item"
)

urlpatterns = [
    path("", include(router.urls)),
]
