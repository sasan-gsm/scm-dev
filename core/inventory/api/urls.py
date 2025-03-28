from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"warehouses", views.WarehouseViewSet, basename="warehouse")
# router.register(r"locations", views.LocationViewSet, basename="location")
router.register(r"items", views.InventoryItemViewSet, basename="inventory")
router.register(
    r"transactions", views.InventoryTransactionViewSet, basename="inventory-transaction"
)

app_name = "inventory"

urlpatterns = [
    path("", include(router.urls)),
]
