from typing import Optional, Dict, Any, List
from django.db.models import QuerySet, F
from django.utils import timezone
from django.db import transaction

from core.common.services import BaseService
from .repositories import InventoryRepository, InventoryTransactionRepository
from .models import Inventory, InventoryTransaction


class InventoryService(BaseService[Inventory]):
    """
    Service for Inventory business logic.

    This class provides business logic operations for the Inventory model.
    """

    def __init__(self):
        """
        Initialize the service with an InventoryRepository.
        """
        super().__init__(InventoryRepository())

    def get_by_material(self, material_id: int) -> Optional[Inventory]:
        """
        Get inventory for a specific material.

        Args:
            material_id: The material ID

        Returns:
            The inventory if found, None otherwise
        """
        return self.repository.get_by_material(material_id)

    def get_low_inventory(self) -> QuerySet:
        """
        Get inventory items with quantity below minimum level.

        Returns:
            QuerySet of inventory items with low quantity
        """
        return self.repository.get_low_inventory()

    def get_low_inventory_with_alerts(self) -> QuerySet:
        """
        Get inventory items with quantity below minimum level and alerts enabled.

        Returns:
            QuerySet of inventory items with low quantity and alerts enabled
        """
        return self.repository.get_low_inventory_with_alerts()

    def get_inventory_value(self) -> float:
        """
        Calculate the total value of all inventory.

        Returns:
            Total inventory value
        """
        return self.repository.get_inventory_value()

    def get_inventory_by_location(self, location_id: int) -> QuerySet:
        """
        Get inventory items in a specific location.

        Args:
            location_id: The location ID

        Returns:
            QuerySet of inventory items in the specified location
        """
        return self.repository.get_inventory_by_location(location_id)

    @transaction.atomic
    def adjust_quantity(
        self,
        inventory_id: int,
        quantity_change: float,
        reason: str,
        reference_type: str = None,
        reference_id: int = None,
        project_id: int = None,
    ) -> Optional[Inventory]:
        """
        Adjust the quantity of an inventory item and record the transaction.
        This operation is atomic to ensure data consistency.

        Args:
            inventory_id: The inventory ID
            quantity_change: The quantity change (positive for increase, negative for decrease)
            reason: The reason for the adjustment
            reference_type: The reference type (e.g., 'purchase_order', 'request')
            reference_id: The reference ID
            project_id: Optional project ID to associate with this transaction

        Returns:
            The updated inventory if found, None otherwise
        """
        # Get the inventory
        inventory = self.get_by_id(inventory_id)
        if not inventory:
            return None

        # Calculate new quantity
        new_quantity = inventory.quantity + quantity_change

        # Update the inventory
        updated_inventory = self.update(inventory_id, {"quantity": new_quantity})

        # Record the transaction
        transaction_service = InventoryTransactionService()
        transaction_data = {
            "inventory": inventory,
            "material": inventory.material,
            "quantity": quantity_change,
            "transaction_type": "adjustment",
            "reason": reason,
            "reference_type": reference_type,
            "reference_id": reference_id,
            "transaction_date": timezone.now(),
        }

        # Add project if specified
        if project_id:
            transaction_data["project_id"] = project_id

        transaction_service.create(transaction_data)

        # Check if this adjustment puts inventory below threshold and alerts are enabled
        if (
            new_quantity < inventory.material.min_inventory_level
            and inventory.material.alert_enabled
        ):
            self._trigger_low_inventory_alert(inventory)

        return updated_inventory

    @transaction.atomic
    def transfer_inventory(
        self,
        inventory_id: int,
        destination_location_id: int,
        quantity: float,
        reason: str,
        project_id: int = None,
    ) -> Optional[Inventory]:
        """
        Transfer inventory from one location to another.
        This operation is atomic to ensure data consistency.

        Args:
            inventory_id: The source inventory ID
            destination_location_id: The destination location ID
            quantity: The quantity to transfer
            reason: The reason for the transfer
            project_id: Optional project ID to associate with this transfer

        Returns:
            The updated source inventory if found, None otherwise
        """
        # Get the source inventory
        source_inventory = self.get_by_id(inventory_id)
        if not source_inventory:
            return None

        # Ensure sufficient quantity
        if source_inventory.quantity < quantity:
            raise ValueError("Insufficient quantity for transfer")

        # Get or create destination inventory
        destination_inventory = self.repository.filter(
            material=source_inventory.material, location_id=destination_location_id
        ).first()

        if not destination_inventory:
            destination_inventory = self.create(
                {
                    "material": source_inventory.material,
                    "location_id": destination_location_id,
                    "quantity": 0,
                }
            )

        # Update source inventory
        source_inventory = self.adjust_quantity(
            inventory_id,
            -quantity,
            f"Transfer to location {destination_location_id}: {reason}",
            project_id=project_id,
        )

        # Update destination inventory
        self.adjust_quantity(
            destination_inventory.id,
            quantity,
            f"Transfer from location {source_inventory.location_id}: {reason}",
            project_id=project_id,
        )

        return source_inventory

    @transaction.atomic
    def assign_to_project(
        self,
        inventory_id: int,
        project_id: int,
        quantity: float,
        reason: str,
    ) -> Optional[Inventory]:
        """
        Assign inventory to a specific project without changing its location.
        This is useful when materials are allocated to projects but remain in the warehouse.

        Args:
            inventory_id: The inventory ID
            project_id: The project ID
            quantity: The quantity to assign
            reason: The reason for the assignment

        Returns:
            The updated inventory if found, None otherwise
        """
        # Get the inventory
        inventory = self.get_by_id(inventory_id)
        if not inventory:
            return None

        # Ensure sufficient quantity
        if inventory.quantity < quantity:
            raise ValueError("Insufficient quantity for project assignment")

        # Record the transaction without changing inventory location
        transaction_service = InventoryTransactionService()
        transaction_service.create(
            {
                "inventory": inventory,
                "material": inventory.material,
                "quantity": -quantity,  # Negative because it's being allocated
                "transaction_type": "issue",
                "reason": f"Assigned to project {project_id}: {reason}",
                "project_id": project_id,
                "transaction_date": timezone.now(),
            }
        )

        # Update the inventory quantity
        updated_inventory = self.update(
            inventory_id, {"quantity": inventory.quantity - quantity}
        )

        return updated_inventory

    @transaction.atomic
    def record_warehouse_output(
        self,
        inventory_id: int,
        quantity: float,
        reason: str,
        project_id: int = None,
        is_general_use: bool = False,
    ) -> Optional[Inventory]:
        """
        Record material output from warehouse, optionally assigning to a project.

        Args:
            inventory_id: The inventory ID
            quantity: The quantity to output
            reason: The reason for the output
            project_id: Optional project ID to associate with this output
            is_general_use: Whether this output is for general use (not project-specific)

        Returns:
            The updated inventory if found, None otherwise
        """
        # Get the inventory
        inventory = self.get_by_id(inventory_id)
        if not inventory:
            return None

        # Ensure sufficient quantity
        if inventory.quantity < quantity:
            raise ValueError("Insufficient quantity for warehouse output")

        # Record the transaction
        transaction_service = InventoryTransactionService()
        transaction_data = {
            "inventory": inventory,
            "material": inventory.material,
            "quantity": -quantity,  # Negative because it's leaving inventory
            "transaction_type": "issue",
            "reason": reason,
            "transaction_date": timezone.now(),
            "is_general_use": is_general_use,
        }

        # Add project if specified
        if project_id:
            transaction_data["project_id"] = project_id

        transaction_service.create(transaction_data)

        # Update the inventory quantity
        updated_inventory = self.update(
            inventory_id, {"quantity": inventory.quantity - quantity}
        )

        # Check if this output puts inventory below threshold and alerts are enabled
        if (
            updated_inventory.quantity < inventory.material.min_inventory_level
            and inventory.material.alert_enabled
        ):
            self._trigger_low_inventory_alert(updated_inventory)

        return updated_inventory

    def _trigger_low_inventory_alert(self, inventory: Inventory) -> None:
        """
        Trigger an alert for low inventory levels.

        Args:
            inventory: The inventory item with low quantity
        """
        # This is a placeholder for your notification system
        # You would implement the actual alert mechanism here
        # For example, sending an email, creating a notification, etc.
        pass

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating an inventory item.

        Args:
            data: The inventory data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        required_fields = ["material", "location_id", "quantity"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Ensure quantity is not negative
        if data["quantity"] < 0:
            raise ValueError("Quantity cannot be negative")

        # Check if inventory already exists for this material and location
        existing = self.repository.filter(
            material=data["material"], location_id=data["location_id"]
        ).first()

        if existing:
            raise ValueError(
                f"Inventory already exists for material {data['material'].id} at location {data['location_id']}"
            )

    def _validate_update(self, entity: Inventory, data: Dict[str, Any]) -> None:
        """
        Validate data before updating an inventory item.

        Args:
            entity: The inventory to update
            data: The updated data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure quantity is not negative
        if "quantity" in data and data["quantity"] < 0:
            raise ValueError("Quantity cannot be negative")

        # If changing material or location, ensure no duplicate
        if ("material" in data and data["material"] != entity.material) or (
            "location_id" in data and data["location_id"] != entity.location_id
        ):
            material = data.get("material", entity.material)
            location_id = data.get("location_id", entity.location_id)

            existing = (
                self.repository.filter(material=material, location_id=location_id)
                .exclude(id=entity.id)
                .first()
            )

            if existing:
                raise ValueError(
                    f"Inventory already exists for material {material.id} at location {location_id}"
                )


class InventoryTransactionService(BaseService[InventoryTransaction]):
    """
    Service for InventoryTransaction business logic.

    This class provides business logic operations for the InventoryTransaction model.
    """

    def __init__(self):
        """
        Initialize the service with an InventoryTransactionRepository.
        """
        super().__init__(InventoryTransactionRepository())

    def get_by_reference(self, reference_type: str, reference_id: int) -> QuerySet:
        """
        Get transactions by reference type and ID.

        Args:
            reference_type: The reference type (e.g., 'purchase_order', 'request')
            reference_id: The reference ID

        Returns:
            QuerySet of transactions with the specified reference
        """
        return self.repository.get_by_reference(reference_type, reference_id)

    def get_material_transactions(self, material_id: int) -> QuerySet:
        """
        Get all transactions for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of transactions for the specified material
        """
        return self.repository.get_material_transactions(material_id)

    def get_project_transactions(self, project_id: int) -> QuerySet:
        """
        Get all transactions for a specific project.

        Args:
            project_id: The project ID

        Returns:
            QuerySet of transactions for the specified project
        """
        return self.repository.get_project_transactions(project_id)

    def get_transactions_by_date_range(self, start_date, end_date) -> QuerySet:
        """
        Get transactions within a date range.

        Args:
            start_date: The start date
            end_date: The end date

        Returns:
            QuerySet of transactions within the specified date range
        """
        return self.repository.get_transactions_by_date_range(start_date, end_date)

    def get_material_project_usage(self, material_id: int, project_id: int) -> float:
        """
        Get the total usage of a material in a specific project.

        Args:
            material_id: The material ID
            project_id: The project ID

        Returns:
            Total quantity of the material used in the project
        """
        transactions = self.repository.get_material_project_transactions(
            material_id, project_id
        )
        total_usage = sum(t.quantity for t in transactions if t.quantity < 0)
        return abs(total_usage)

    def get_general_use_transactions(self) -> QuerySet:
        """
        Get all transactions marked as general use (not project-specific).

        Returns:
            QuerySet of general use transactions
        """
        return self.repository.get_general_use_transactions()

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating a transaction.

        Args:
            data: The transaction data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        required_fields = ["inventory", "material", "quantity", "transaction_type"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Ensure transaction date is not in the future
        if "transaction_date" in data and data["transaction_date"] > timezone.now():
            raise ValueError("Transaction date cannot be in the future")
