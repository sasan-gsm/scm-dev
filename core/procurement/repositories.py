from typing import Optional, List
from django.db.models import Q, QuerySet, Count, Sum, F, Avg
from django.utils import timezone
from datetime import timedelta

from core.common.repositories import BaseRepository
from .models import PurchaseOrder, PurchaseOrderItem, Supplier, SupplierContact


class SupplierRepository(BaseRepository[Supplier]):
    """
    Repository for Supplier model operations.
    """

    def __init__(self):
        """
        Initialize the repository with the Supplier model.
        """
        super().__init__(Supplier)

    def get_by_code(self, code: str) -> Optional[Supplier]:
        """
        Retrieve a supplier by its code.

        Args:
            code: The supplier code

        Returns:
            The supplier if found, None otherwise
        """
        try:
            return self.model_class.objects.get(code=code)
        except self.model_class.DoesNotExist:
            return None

    def get_active_suppliers(self) -> QuerySet:
        """
        Get active suppliers.

        Returns:
            QuerySet of active suppliers
        """
        return self.model_class.objects.filter(is_active=True)


class SupplierContactRepository(BaseRepository[SupplierContact]):
    """
    Repository for SupplierContact model operations.
    """

    def __init__(self):
        """
        Initialize the repository with the SupplierContact model.
        """
        super().__init__(SupplierContact)

    def get_by_supplier(self, supplier_id: int) -> QuerySet:
        """
        Get contacts for a specific supplier.

        Args:
            supplier_id: The supplier ID

        Returns:
            QuerySet of contacts for the specified supplier
        """
        return self.model_class.objects.filter(supplier_id=supplier_id)

    def get_primary_contact(self, supplier_id: int) -> Optional[SupplierContact]:
        """
        Get the primary contact for a supplier.

        Args:
            supplier_id: The supplier ID

        Returns:
            The primary contact if found, None otherwise
        """
        try:
            return self.model_class.objects.get(
                supplier_id=supplier_id, is_primary=True
            )
        except (
            self.model_class.DoesNotExist,
            self.model_class.MultipleObjectsReturned,
        ):
            return None


class PurchaseOrderRepository(BaseRepository[PurchaseOrder]):
    """
    Repository for PurchaseOrder model operations.

    Provides data access operations specific to the PurchaseOrder model.
    """

    def __init__(self):
        """
        Initialize the repository with the PurchaseOrder model.
        """
        super().__init__(PurchaseOrder)

    def get_by_number(self, number: str) -> Optional[PurchaseOrder]:
        """
        Retrieve a purchase order by its number.

        Args:
            number: The purchase order number

        Returns:
            The purchase order if found, None otherwise
        """
        try:
            return self.model_class.objects.get(number=number)
        except self.model_class.DoesNotExist:
            return None

    def get_by_supplier(self, supplier_id: int) -> QuerySet:
        """
        Get purchase orders for a specific supplier.

        Args:
            supplier_id: The supplier ID

        Returns:
            QuerySet of purchase orders for the specified supplier
        """
        return self.model_class.objects.filter(supplier_id=supplier_id)

    def get_by_status(self, status: str) -> QuerySet:
        """
        Get purchase orders with a specific status.

        Args:
            status: The status

        Returns:
            QuerySet of purchase orders with the specified status
        """
        return self.model_class.objects.filter(status=status)

    def get_by_date_range(self, start_date, end_date) -> QuerySet:
        """
        Get purchase orders created within a date range.

        Args:
            start_date: The start date
            end_date: The end date

        Returns:
            QuerySet of purchase orders within the specified date range
        """
        return self.model_class.objects.filter(
            created_at__gte=start_date, created_at__lte=end_date
        )

    def get_orders_due_soon(self, days: int = 7) -> QuerySet:
        """
        Get purchase orders due within the specified number of days.

        Args:
            days: Number of days from now

        Returns:
            QuerySet of purchase orders due soon
        """
        due_date = timezone.now().date() + timedelta(days=days)
        return self.model_class.objects.filter(
            expected_delivery_date__lte=due_date,
            status__in=["draft", "sent", "confirmed"],
        )

    def get_orders_with_items(self) -> QuerySet:
        """
        Get purchase orders with their items prefetched.

        Returns:
            QuerySet of purchase orders with prefetched items
        """
        return self.model_class.objects.prefetch_related("items")

    def get_total_by_supplier(self) -> QuerySet:
        """
        Get total purchase amount by supplier.

        Returns:
            QuerySet of suppliers with their total purchase amount
        """
        return (
            self.model_class.objects.values("supplier")
            .annotate(total_amount=Sum("total_amount"))
            .order_by("-total_amount")
        )


class PurchaseOrderItemRepository(BaseRepository[PurchaseOrderItem]):
    """
    Repository for PurchaseOrderItem model operations.

    Provides data access operations specific to the PurchaseOrderItem model.
    """

    def __init__(self):
        """
        Initialize the repository with the PurchaseOrderItem model.
        """
        super().__init__(PurchaseOrderItem)

    def get_by_order(self, order_id: int) -> QuerySet:
        """
        Get items for a specific purchase order.

        Args:
            order_id: The purchase order ID

        Returns:
            QuerySet of items for the specified purchase order
        """
        return self.model_class.objects.filter(purchase_order_id=order_id)

    def get_by_material(self, material_id: int) -> QuerySet:
        """
        Get purchase order items for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of purchase order items for the specified material
        """
        return self.model_class.objects.filter(material_id=material_id)

    def get_pending_receipt_items(self) -> QuerySet:
        """
        Get items that have been ordered but not fully received.

        Returns:
            QuerySet of items pending receipt
        """
        return self.model_class.objects.filter(
            quantity_received__lt=F("quantity"),
            purchase_order__status__in=["sent", "confirmed", "partially_received"],
        )

    def get_most_ordered_materials(self, limit: int = 10) -> QuerySet:
        """
        Get most frequently ordered materials.

        Args:
            limit: Maximum number of materials to return

        Returns:
            QuerySet of most ordered materials
        """
        return (
            self.model_class.objects.values("material")
            .annotate(order_count=Count("id"), total_quantity=Sum("quantity"))
            .order_by("-order_count")[:limit]
        )

    def get_average_price_by_material(self) -> QuerySet:
        """
        Get average price by material.

        Returns:
            QuerySet of materials with their average price
        """
        return (
            self.model_class.objects.values("material")
            .annotate(avg_price=Avg("unit_price"))
            .order_by("material")
        )


class SupplierRepository(BaseRepository[Supplier]):
    """
    Repository for Supplier model operations.

    Provides data access operations specific to the Supplier model.
    """

    def __init__(self):
        """
        Initialize the repository with the Supplier model.
        """
        super().__init__(Supplier)

    def get_by_code(self, code: str) -> Optional[Supplier]:
        """
        Retrieve a supplier by its code.

        Args:
            code: The supplier code

        Returns:
            The supplier if found, None otherwise
        """
        try:
            return self.model_class.objects.get(code=code)
        except self.model_class.DoesNotExist:
            return None

    def search(self, query: str) -> QuerySet:
        """
        Search for suppliers by name, code, or description.

        Args:
            query: The search query

        Returns:
            QuerySet of matching suppliers
        """
        return self.model_class.objects.filter(
            Q(name__icontains=query)
            | Q(code__icontains=query)
            | Q(description__icontains=query)
        )

    def get_active_suppliers(self) -> QuerySet:
        """
        Get active suppliers.

        Returns:
            QuerySet of active suppliers
        """
        return self.model_class.objects.filter(is_active=True)

    def get_suppliers_with_contacts(self) -> QuerySet:
        """
        Get suppliers with their contacts prefetched.

        Returns:
            QuerySet of suppliers with prefetched contacts
        """
        return self.model_class.objects.prefetch_related("contacts")

    def get_suppliers_by_material(self, material_id: int) -> QuerySet:
        """
        Get suppliers that provide a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of suppliers that provide the specified material
        """
        return self.model_class.objects.filter(materials__id=material_id)


class SupplierContactRepository(BaseRepository[SupplierContact]):
    """
    Repository for SupplierContact model operations.

    Provides data access operations specific to the SupplierContact model.
    """

    def __init__(self):
        """
        Initialize the repository with the SupplierContact model.
        """
        super().__init__(SupplierContact)

    def get_by_supplier(self, supplier_id: int) -> QuerySet:
        """
        Get contacts for a specific supplier.

        Args:
            supplier_id: The supplier ID

        Returns:
            QuerySet of contacts for the specified supplier
        """
        return self.model_class.objects.filter(supplier_id=supplier_id)

    def get_primary_contacts(self) -> QuerySet:
        """
        Get primary contacts for suppliers.

        Returns:
            QuerySet of primary contacts
        """
        return self.model_class.objects.filter(is_primary=True)
