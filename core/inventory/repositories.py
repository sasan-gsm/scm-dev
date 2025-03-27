from typing import Optional, List
from django.db.models import Q, QuerySet, Sum, F, Value
from django.db.models.functions import Coalesce

from core.common.repositories import BaseRepository
from .models import InventoryItem, InventoryTransaction, Warehouse, InventoryLocation


class WarehouseRepository(BaseRepository[Warehouse]):
    """
    Repository for Warehouse model operations.

    Provides data access operations specific to the Warehouse model.
    """

    def __init__(self):
        """
        Initialize the repository with the Warehouse model.
        """
        super().__init__(Warehouse)

    def get_active_warehouses(self) -> QuerySet:
        """
        Get active warehouses.

        Returns:
            QuerySet of active warehouses
        """
        return self.model_class.objects.filter(is_active=True)


class InventoryLocationRepository(BaseRepository[InventoryLocation]):
    """
    Repository for InventoryLocation model operations.

    Provides data access operations specific to the InventoryLocation model.
    """

    def __init__(self):
        """
        Initialize the repository with the InventoryLocation model.
        """
        super().__init__(InventoryLocation)

    def get_by_warehouse(self, warehouse_id: int) -> QuerySet:
        """
        Get locations in a specific warehouse.

        Returns:
            QuerySet of locations in the specified warehouse
        """
        return self.model_class.objects.filter(warehouse_id=warehouse_id)


class InventoryRepository(BaseRepository[InventoryItem]):
    """
    Repository for InventoryItem model operations.

    Provides data access operations specific to the InventoryItem model.
    """

    def __init__(self):
        """
        Initialize the repository with the InventoryItem model.
        """
        super().__init__(InventoryItem)

    def get_by_material(self, material_id: int) -> Optional[InventoryItem]:
        """
        Retrieve inventory for a specific material.

        Args:
            material_id: The material ID

        Returns:
            The inventory if found, None otherwise
        """
        try:
            return self.model_class.objects.get(material_id=material_id)
        except self.model_class.DoesNotExist:
            return None

    def get_low_inventory(self) -> QuerySet:
        """
        Get inventory items with quantity below minimum level.

        Returns:
            QuerySet of inventory items with low quantity
        """
        return self.model_class.objects.filter(
            quantity__lt=F("material__min_inventory_level")
        )

    def get_low_inventory_with_alerts(self) -> QuerySet:
        """
        Get inventory items with quantity below minimum level and alerts enabled.

        Returns:
            QuerySet of inventory items with low quantity and alerts enabled
        """
        return self.model_class.objects.filter(
            quantity__lt=F("material__min_inventory_level"),
            material__alert_enabled=True,
        )

    def get_inventory_value(self) -> float:
        """
        Calculate the total value of all inventory.

        Returns:
            Total inventory value
        """
        result = self.model_class.objects.annotate(
            item_value=F("quantity") * Coalesce(F("material__price__amount"), Value(0))
        ).aggregate(total_value=Sum("item_value"))

        return result["total_value"] or 0.0

    def get_inventory_by_location(self, location_id: int) -> QuerySet:
        """
        Get inventory items in a specific location.

        Args:
            location_id: The location ID

        Returns:
            QuerySet of inventory items in the specified location
        """
        return self.model_class.objects.filter(location_id=location_id)


class InventoryTransactionRepository(BaseRepository[InventoryTransaction]):
    """
    Repository for InventoryTransaction model operations.

    Provides data access operations specific to the InventoryTransaction model.
    """

    def __init__(self):
        """
        Initialize the repository with the InventoryTransaction model.
        """
        super().__init__(InventoryTransaction)

    def get_by_reference(self, reference_type: str, reference_id: int) -> QuerySet:
        """
        Get transactions by reference type and ID.

        Args:
            reference_type: The reference type (e.g., 'purchase_order', 'request')
            reference_id: The reference ID

        Returns:
            QuerySet of transactions with the specified reference
        """
        return self.model_class.objects.filter(
            reference_type=reference_type, reference_id=reference_id
        )

    def get_material_transactions(self, material_id: int) -> QuerySet:
        """
        Get all transactions for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of transactions for the specified material
        """
        return self.model_class.objects.filter(material_id=material_id)

    def get_project_transactions(self, project_id: int) -> QuerySet:
        """
        Get all transactions for a specific project.

        Args:
            project_id: The project ID

        Returns:
            QuerySet of transactions for the specified project
        """
        return self.model_class.objects.filter(project_id=project_id)

    def get_material_project_transactions(
        self, material_id: int, project_id: int
    ) -> QuerySet:
        """
        Get all transactions for a specific material and project.

        Args:
            material_id: The material ID
            project_id: The project ID

        Returns:
            QuerySet of transactions for the specified material and project
        """
        return self.model_class.objects.filter(
            material_id=material_id, project_id=project_id
        )

    def get_general_use_transactions(self) -> QuerySet:
        """
        Get all transactions marked as general use (not project-specific).

        Returns:
            QuerySet of general use transactions
        """
        return self.model_class.objects.filter(is_general_use=True)

    def get_transactions_by_date_range(self, start_date, end_date) -> QuerySet:
        """
        Get transactions within a date range.

        Args:
            start_date: The start date
            end_date: The end date

        Returns:
            QuerySet of transactions within the specified date range
        """
        return self.model_class.objects.filter(
            transaction_date__gte=start_date, transaction_date__lte=end_date
        )
