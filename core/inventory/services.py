from typing import Optional, Dict, Any, List, Union
from django.db.models import QuerySet, F, Sum
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

from core.common.services import BaseService
from .models import InventoryItem, InventoryTransaction, Warehouse, InventoryLocation
from .repositories import (
    InventoryRepository,
    InventoryTransactionRepository,
    WarehouseRepository,
    InventoryLocationRepository,
)


class WarehouseService(BaseService):
    """
    Service for Warehouse business logic.
    """

    def __init__(self):
        """
        Initialize the service with a WarehouseRepository.
        """
        super().__init__(WarehouseRepository())

    def get_all(self) -> QuerySet:
        """
        Get all warehouses.

        Returns:
            QuerySet of Warehouse objects
        """
        return self.repository.get_all()

    def get_by_id(self, id: int) -> Optional[Warehouse]:
        """
        Get warehouse by ID.

        Args:
            id: The warehouse ID

        Returns:
            Warehouse object or None
        """
        return self.repository.get_by_id(id)

    def create(self, data: Dict[str, Any]) -> Warehouse:
        """
        Create a new warehouse.

        Args:
            data: Dictionary with warehouse data

        Returns:
            Created Warehouse object
        """
        return self.repository.create(data)

    def update(self, id: int, data: Dict[str, Any]) -> Optional[Warehouse]:
        """
        Update an existing warehouse.

        Args:
            id: The warehouse ID
            data: Dictionary with updated warehouse data

        Returns:
            Updated Warehouse object or None
        """
        return self.repository.update(id, data)

    def delete(self, id: int) -> bool:
        """
        Delete a warehouse.

        Args:
            id: The warehouse ID

        Returns:
            True if deleted, False otherwise
        """
        # Check if warehouse has inventory items
        if InventoryItem.objects.filter(warehouse_id=id).exists():
            raise ValueError("Cannot delete warehouse with inventory items.")

        return self.repository.delete(id)


class InventoryLocationService(BaseService):
    """
    Service for InventoryLocation business logic.
    """

    def __init__(self):
        """
        Initialize the service with an InventoryLocationRepository.
        """
        super().__init__(InventoryLocationRepository())

    def get_all(self) -> QuerySet:
        """
        Get all inventory locations.

        Returns:
            QuerySet of InventoryLocation objects
        """
        return self.repository.get_all()

    def get_by_id(self, id: int) -> Optional[InventoryLocation]:
        """
        Get inventory location by ID.

        Args:
            id: The inventory location ID

        Returns:
            InventoryLocation object or None
        """
        return self.repository.get_by_id(id)

    def get_by_warehouse(self, warehouse_id: int) -> QuerySet:
        """
        Get locations in a specific warehouse.

        Args:
            warehouse_id: The warehouse ID

        Returns:
            QuerySet of InventoryLocation objects
        """
        return self.repository.get_by_warehouse(warehouse_id)

    def create(self, data: Dict[str, Any]) -> InventoryLocation:
        """
        Create a new inventory location.

        Args:
            data: Dictionary with inventory location data

        Returns:
            Created InventoryLocation object
        """
        return self.repository.create(data)

    def update(self, id: int, data: Dict[str, Any]) -> Optional[InventoryLocation]:
        """
        Update an existing inventory location.

        Args:
            id: The inventory location ID
            data: Dictionary with updated inventory location data

        Returns:
            Updated InventoryLocation object or None
        """
        return self.repository.update(id, data)

    def delete(self, id: int) -> bool:
        """
        Delete an inventory location.

        Args:
            id: The inventory location ID

        Returns:
            True if deleted, False otherwise
        """
        # Check if location has inventory items
        if InventoryItem.objects.filter(location_id=id).exists():
            raise ValueError("Cannot delete location with inventory items.")

        return self.repository.delete(id)


class InventoryService(BaseService):
    """
    Service for Inventory business logic.
    """

    def __init__(self):
        """
        Initialize the service with an InventoryRepository.
        """
        super().__init__(InventoryRepository())

    def get_all(self) -> QuerySet:
        """
        Get all inventory items.

        Returns:
            QuerySet of InventoryItem objects
        """
        return self.repository.get_all()

    def get_by_id(self, id: int) -> Optional[InventoryItem]:
        """
        Get inventory item by ID.

        Args:
            id: The inventory item ID

        Returns:
            InventoryItem object or None
        """
        return self.repository.get_by_id(id)

    def get_by_material(self, material_id: int) -> QuerySet:
        """
        Get inventory items for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of InventoryItem objects
        """
        return self.repository.get_by_material(material_id)

    def get_by_warehouse(self, warehouse_id: int) -> QuerySet:
        """
        Get inventory items in a specific warehouse.

        Args:
            warehouse_id: The warehouse ID

        Returns:
            QuerySet of InventoryItem objects
        """
        return self.repository.get_by_warehouse(warehouse_id)

    def get_by_location(self, location_id: int) -> QuerySet:
        """
        Get inventory items in a specific location.

        Args:
            location_id: The location ID

        Returns:
            QuerySet of InventoryItem objects
        """
        return self.repository.get_by_location(location_id)

    def get_low_inventory(self) -> QuerySet:
        """
        Get inventory items with quantity below minimum level.

        Returns:
            QuerySet of InventoryItem objects
        """
        return self.repository.get_low_inventory()

    def create(self, data: Dict[str, Any]) -> InventoryItem:
        """
        Create a new inventory item.

        Args:
            data: Dictionary with inventory item data

        Returns:
            Created InventoryItem object
        """
        return self.repository.create(data)

    def update(self, id: int, data: Dict[str, Any]) -> Optional[InventoryItem]:
        """
        Update an existing inventory item.

        Args:
            id: The inventory item ID
            data: Dictionary with updated inventory item data

        Returns:
            Updated InventoryItem object or None
        """
        return self.repository.update(id, data)

    def delete(self, id: int) -> bool:
        """
        Delete an inventory item.

        Args:
            id: The inventory item ID

        Returns:
            True if deleted, False otherwise
        """
        return self.repository.delete(id)

    def adjust_quantity(
        self,
        id: int,
        quantity_change: Decimal,
        reason: str,
        performed_by_id: int,
        project_id: Optional[int] = None,
    ) -> Optional[InventoryItem]:
        """
        Adjust the quantity of an inventory item and create a transaction.

        Args:
            id: The inventory item ID
            quantity_change: The amount to adjust (positive for increase, negative for decrease)
            reason: The reason for the adjustment
            performed_by_id: The ID of the user performing the adjustment
            project_id: Optional project ID

        Returns:
            Updated InventoryItem object or None
        """
        with transaction.atomic():
            inventory_item = self.get_by_id(id)
            if not inventory_item:
                return None

            # Check if we have enough quantity for a decrease
            if quantity_change < 0 and (inventory_item.quantity + quantity_change) < 0:
                raise ValueError("Cannot reduce quantity below zero.")

            # Update the inventory item
            inventory_item.quantity += quantity_change
            inventory_item.save()

            # Create a transaction record
            transaction_type = "adjustment"
            InventoryTransaction.objects.create(
                material=inventory_item.material,
                transaction_type=transaction_type,
                quantity=abs(quantity_change),
                from_warehouse=inventory_item.warehouse
                if quantity_change < 0
                else None,
                to_warehouse=inventory_item.warehouse if quantity_change > 0 else None,
                project_id=project_id,
                performed_by_id=performed_by_id,
                notes=reason,
            )

            return inventory_item


class InventoryTransactionService(BaseService):
    """
    Service for InventoryTransaction business logic.
    """

    def __init__(self):
        """
        Initialize the service with an InventoryTransactionRepository.
        """
        super().__init__(InventoryTransactionRepository())

    def get_all(self) -> QuerySet:
        """
        Get all inventory transactions.

        Returns:
            QuerySet of InventoryTransaction objects
        """
        return self.repository.get_all()

    def get_by_id(self, id: int) -> Optional[InventoryTransaction]:
        """
        Get inventory transaction by ID.

        Args:
            id: The inventory transaction ID

        Returns:
            InventoryTransaction object or None
        """
        return self.repository.get_by_id(id)

    def get_material_transactions(self, material_id: int) -> QuerySet:
        """
        Get transactions for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of InventoryTransaction objects
        """
        return self.repository.get_by_material(material_id)

    def get_project_transactions(self, project_id: int) -> QuerySet:
        """
        Get transactions for a specific project.

        Args:
            project_id: The project ID

        Returns:
            QuerySet of InventoryTransaction objects
        """
        return self.repository.get_project_transactions(project_id)

    @transaction.atomic
    def create(self, data: Dict[str, Any]) -> InventoryTransaction:
        """
        Create a new inventory transaction and update inventory levels.

        Args:
            data: Dictionary with transaction data

        Returns:
            Created InventoryTransaction object
        """
        transaction_type = data.get("transaction_type")
        material_id = data.get("material_id")
        quantity = data.get("quantity")
        from_warehouse_id = data.get("from_warehouse_id")
        to_warehouse_id = data.get("to_warehouse_id")

        # Create the transaction
        inventory_transaction = self.repository.create(data)

        # Update inventory levels based on transaction type
        if transaction_type == "receipt":
            # Find or create inventory item in the destination warehouse
            inventory_item, created = InventoryItem.objects.get_or_create(
                material_id=material_id,
                warehouse_id=to_warehouse_id,
                defaults={"quantity": 0},
            )
            inventory_item.quantity += quantity
            inventory_item.save()

        elif transaction_type == "issue":
            # Find inventory item in the source warehouse
            try:
                inventory_item = InventoryItem.objects.get(
                    material_id=material_id, warehouse_id=from_warehouse_id
                )

                # Check if we have enough quantity
                if inventory_item.quantity < quantity:
                    raise ValueError(
                        f"Not enough quantity in warehouse. Available: {inventory_item.quantity}"
                    )

                inventory_item.quantity -= quantity
                inventory_item.save()

            except InventoryItem.DoesNotExist:
                raise ValueError("Material not found in the source warehouse.")

        elif transaction_type == "transfer":
            # Find inventory item in the source warehouse
            try:
                source_item = InventoryItem.objects.get(
                    material_id=material_id, warehouse_id=from_warehouse_id
                )

                # Check if we have enough quantity
                if source_item.quantity < quantity:
                    raise ValueError(
                        f"Not enough quantity in source warehouse. Available: {source_item.quantity}"
                    )

                # Reduce quantity in source warehouse
                source_item.quantity -= quantity
                source_item.save()

                # Find or create inventory item in the destination warehouse
                dest_item, created = InventoryItem.objects.get_or_create(
                    material_id=material_id,
                    warehouse_id=to_warehouse_id,
                    defaults={"quantity": 0},
                )

                # Increase quantity in destination warehouse
                dest_item.quantity += quantity
                dest_item.save()

            except InventoryItem.DoesNotExist:
                dest_item.quantity += quantity
                dest_item.save()

            except InventoryItem.DoesNotExist:
                raise ValueError("Material not found in the source warehouse.")

        return inventory_transaction

    def delete(self, id: int) -> bool:
        """
        Delete an inventory transaction.

        Args:
            id: The inventory transaction ID

        Returns:
            True if deleted, False otherwise
        """
        # Note: In a real application, you might want to reverse the inventory
        # changes caused by this transaction before deleting it
        return self.repository.delete(id)
