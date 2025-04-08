from typing import Optional, Dict, Any, List
from django.db.models import QuerySet, F, Sum
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

from core.common.services import BaseService
from .repositories import (
    PurchaseOrderRepository,
    PurchaseOrderItemRepository,
    SupplierRepository,
    SupplierContactRepository,
)
from .models import PurchaseOrder, PurchaseOrderItem, Supplier, SupplierContact
from core.inventory.services import InventoryService


class SupplierService(BaseService[Supplier]):
    """
    Service for Supplier business logic.

    This class provides business logic operations for the Supplier model.
    """

    def __init__(self):
        """
        Initialize the service with a SupplierRepository.
        """
        super().__init__(SupplierRepository())

    def get_by_code(self, code: str) -> Optional[Supplier]:
        return self.repository.get_by_code(code)

    def get_active_suppliers(self) -> QuerySet:
        """
        Get active suppliers.

        Returns:
            QuerySet of active suppliers
        """
        return self.repository.get_active_suppliers()


class SupplierContactService(BaseService[SupplierContact]):
    """
    Service for SupplierContact business logic.

    This class provides business logic operations for the SupplierContact model.
    """

    def __init__(self):
        """
        Initialize the service with a SupplierContactRepository.
        """
        super().__init__(SupplierContactRepository())

    def get_by_supplier(self, supplier_id: int) -> QuerySet:
        """
        Get contacts for a specific supplier.

        Args:
            supplier_id: The supplier ID

        Returns:
            QuerySet of contacts for the specified supplier
        """
        return self.repository.get_by_supplier(supplier_id)

    def get_primary_contact(self, supplier_id: int) -> Optional[SupplierContact]:
        """
        Get the primary contact for a supplier.

        Args:
            supplier_id: The supplier ID

        Returns:
            The primary contact if found, None otherwise
        """
        return self.repository.get_primary_contact(supplier_id)

    def get_primary_contacts(self) -> QuerySet:
        """
        Get primary contacts for all suppliers.

        Returns:
            QuerySet of primary contacts
        """
        return self.repository.model_class.objects.filter(is_primary=True)

    def set_as_primary(self, contact_id: int) -> Optional[SupplierContact]:
        """
        Set a contact as the primary contact for its supplier.

        Args:
            contact_id: The contact ID

        Returns:
            The updated contact if found, None otherwise
        """
        contact = self.get_by_id(contact_id)
        if not contact:
            return None

        with transaction.atomic():
            # Clear primary flag for all contacts of this supplier
            self.repository.model_class.objects.filter(
                supplier=contact.supplier, is_primary=True
            ).update(is_primary=False)

            # Set this contact as primary
            return self.update(contact_id, {"is_primary": True})

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating a supplier contact.

        Args:
            data: The supplier contact data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        required_fields = ["supplier", "name", "email"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # If this is the first contact for the supplier, make it primary
        if "is_primary" not in data:
            supplier_contacts = self.get_by_supplier(data["supplier"].id)
            data["is_primary"] = not supplier_contacts.exists()

        # If setting as primary, ensure no other contact is primary
        if data.get("is_primary", False):
            primary_contacts = self.get_by_supplier(data["supplier"].id).filter(
                is_primary=True
            )
            if primary_contacts.exists():
                for contact in primary_contacts:
                    contact.is_primary = False
                    contact.save()


class PurchaseOrderService(BaseService[PurchaseOrder]):
    """
    Service for PurchaseOrder business logic.

    This class provides business logic operations for the PurchaseOrder model.
    """

    def __init__(self):
        """
        Initialize the service with a PurchaseOrderRepository.
        """
        super().__init__(PurchaseOrderRepository())

    def get_by_number(self, number: str) -> Optional[PurchaseOrder]:
        """
        Get a purchase order by its number.

        Args:
            number: The purchase order number

        Returns:
            The purchase order if found, None otherwise
        """
        return self.repository.get_by_number(number)

    def get_by_supplier(self, supplier_id: int) -> QuerySet:
        """
        Get purchase orders for a specific supplier.

        Args:
            supplier_id: The supplier ID

        Returns:
            QuerySet of purchase orders for the specified supplier
        """
        return self.repository.get_by_supplier(supplier_id)

    def get_by_status(self, status: str) -> QuerySet:
        """
        Get purchase orders with a specific status.

        Args:
            status: The status

        Returns:
            QuerySet of purchase orders with the specified status
        """
        return self.repository.get_by_status(status)

    def get_by_date_range(self, start_date, end_date) -> QuerySet:
        """
        Get purchase orders created within a date range.

        Args:
            start_date: The start date
            end_date: The end date

        Returns:
            QuerySet of purchase orders within the specified date range
        """
        return self.repository.get_by_date_range(start_date, end_date)

    def get_orders_due_soon(self, days: int = 7) -> QuerySet:
        """
        Get purchase orders due within the specified number of days.

        Args:
            days: Number of days from now

        Returns:
            QuerySet of purchase orders due soon
        """
        return self.repository.get_orders_due_soon(days)

    def send_order(self, order_id: int) -> Optional[PurchaseOrder]:
        """
        Mark a purchase order as sent.

        Args:
            order_id: The purchase order ID

        Returns:
            The updated purchase order if found, None otherwise
        """
        # Get the purchase order
        order = self.get_by_id(order_id)
        if not order:
            return None

        # Ensure order is in draft status
        if order.status != "draft":
            raise ValueError(
                f"Order is not in draft status (current status: {order.status})"
            )

        # Update the order
        return self.update(order_id, {"status": "sent", "sent_date": timezone.now()})

    def confirm_order(
        self, order_id: int, confirmation_number: str = None
    ) -> Optional[PurchaseOrder]:
        """
        Mark a purchase order as confirmed.

        Args:
            order_id: The purchase order ID
            confirmation_number: The supplier's confirmation number

        Returns:
            The updated purchase order if found, None otherwise
        """
        # Get the purchase order
        order = self.get_by_id(order_id)
        if not order:
            return None

        # Ensure order is in sent status
        if order.status != "sent":
            raise ValueError(
                f"Order is not in sent status (current status: {order.status})"
            )

        # Update the order
        data = {"status": "confirmed", "confirmation_date": timezone.now()}

        if confirmation_number:
            data["confirmation_number"] = confirmation_number

        return self.update(order_id, data)

    def receive_items(
        self, order_id: int, items_data: List[Dict[str, Any]]
    ) -> Optional[PurchaseOrder]:
        """
        Receive items for a purchase order.

        Args:
            order_id: The purchase order ID
            items_data: List of items data with material_id and quantity

        Returns:
            The updated purchase order if found, None otherwise
        """
        # Get the purchase order
        order = self.get_by_id(order_id)
        if not order:
            return None

        # Ensure order is in a valid status for receiving
        valid_statuses = ["sent", "confirmed", "partially_received"]
        if order.status not in valid_statuses:
            raise ValueError(
                f"Order is not in a valid status for receiving (current status: {order.status})"
            )

        # Get order items
        item_repository = PurchaseOrderItemRepository()
        item_service = PurchaseOrderItemService()
        inventory_service = InventoryService()

        with transaction.atomic():
            all_items_received = True

            for item_data in items_data:
                material_id = item_data.get("material_id")
                quantity = item_data.get("quantity")

                if not material_id or not quantity:
                    raise ValueError(
                        "material_id and quantity are required for each item"
                    )

                # Find the order item
                order_items = item_repository.get_by_order(order_id).filter(
                    material_id=material_id
                )
                if not order_items.exists():
                    raise ValueError(
                        f"Material {material_id} is not part of this order"
                    )

                order_item = order_items.first()

                # Validate quantity
                remaining_quantity = order_item.quantity - order_item.received_quantity
                if quantity > remaining_quantity:
                    raise ValueError(
                        f"Quantity exceeds remaining quantity for material {material_id}"
                    )

                # Update order item
                new_received_quantity = order_item.received_quantity + quantity
                is_fully_received = new_received_quantity >= order_item.quantity

                item_service.update(
                    order_item.id,
                    {
                        "received_quantity": new_received_quantity,
                        "status": "fully_received"
                        if is_fully_received
                        else "partially_received",
                        "actual_delivery_date": timezone.now()
                        if is_fully_received
                        else None,
                    },
                )

                # Update inventory
                # First get or create inventory item for this material
                inventory_item = inventory_service.get_by_material(material_id).first()
                if inventory_item:
                    inventory_service.adjust_quantity(
                        inventory_item.id,
                        quantity,
                        f"Receipt from PO {order.order_number}",
                        order.created_by_id,  # Using the PO creator as the performer
                        order.project_id,
                    )
                else:
                    # Handle case where inventory item doesn't exist yet
                    # This would need proper warehouse selection logic in a real implementation
                    raise ValueError(
                        f"No inventory record exists for material {material_id}. Please create inventory record first."
                    )

                # Check if all items are fully received
                if not is_fully_received:
                    all_items_received = False

            # Update order status
            new_status = (
                "fully_received" if all_items_received else "partially_received"
            )
            return self.update(
                order_id,
                {
                    "status": new_status,
                    "receipt_date": timezone.now() if all_items_received else None,
                },
            )

    def submit_for_approval(self, order_id: int) -> Optional[PurchaseOrder]:
        """
        Submit a purchase order for approval.

        Args:
            order_id: The purchase order ID

        Returns:
            The updated purchase order if found, None otherwise
        """
        # Get the purchase order
        order = self.get_by_id(order_id)
        if not order:
            return None

        # Ensure order is in draft status
        if order.status != "draft":
            raise ValueError(
                f"Order is not in draft status (current status: {order.status})"
            )

        # Update the order
        return self.update(order_id, {"status": "pending_approval"})

    def approve(self, order_id: int) -> Optional[PurchaseOrder]:
        """
        Approve a purchase order.

        Args:
            order_id: The purchase order ID

        Returns:
            The updated purchase order if found, None otherwise
        """
        # Get the purchase order
        order = self.get_by_id(order_id)
        if not order:
            return None

        # Ensure order is in pending_approval status
        if order.status != "pending_approval":
            raise ValueError(
                f"Order is not pending approval (current status: {order.status})"
            )

        # Update the order
        return self.update(
            order_id, {"status": "approved", "approval_date": timezone.now()}
        )

    def reject(self, order_id: int, reason: str = None) -> Optional[PurchaseOrder]:
        """
        Reject a purchase order.

        Args:
            order_id: The purchase order ID
            reason: The rejection reason

        Returns:
            The updated purchase order if found, None otherwise
        """
        # Get the purchase order
        order = self.get_by_id(order_id)
        if not order:
            return None

        # Ensure order is in pending_approval status
        if order.status != "pending_approval":
            raise ValueError(
                f"Order is not pending approval (current status: {order.status})"
            )

        # Update the order
        data = {"status": "rejected", "rejection_date": timezone.now()}
        if reason:
            data["rejection_reason"] = reason

        return self.update(order_id, data)

    def receive(self, order_id: int) -> Optional[PurchaseOrder]:
        """
        Mark a purchase order as received.

        Args:
            order_id: The purchase order ID

        Returns:
            The updated purchase order if found, None otherwise
        """
        # Get the purchase order
        order = self.get_by_id(order_id)
        if not order:
            return None

        # Ensure order is in a valid status for receiving
        valid_statuses = ["approved", "sent", "confirmed", "partially_received"]
        if order.status not in valid_statuses:
            raise ValueError(
                f"Order is not in a valid status for receiving (current status: {order.status})"
            )

        # Update the order
        return self.update(
            order_id,
            {
                "status": "fully_received",
                "receipt_date": timezone.now(),
            },
        )

    def cancel(self, order_id: int, reason: str = None) -> Optional[PurchaseOrder]:
        """
        Cancel a purchase order.

        Args:
            order_id: The purchase order ID
            reason: The cancellation reason

        Returns:
            The updated purchase order if found, None otherwise
        """
        # Get the purchase order
        order = self.get_by_id(order_id)
        if not order:
            return None

        # Ensure order is in a valid status for cancellation
        valid_statuses = ["draft", "pending_approval", "approved", "sent", "confirmed"]
        if order.status not in valid_statuses:
            raise ValueError(
                f"Order cannot be cancelled in its current status: {order.status}"
            )

        # Update the order
        data = {
            "status": "cancelled",
            "cancellation_date": timezone.now(),
        }

        if reason:
            data["cancellation_reason"] = reason

        return self.update(order_id, data)

    def get_total_by_supplier(self) -> QuerySet:
        """
        Get total purchase amount by supplier.

        Returns:
            QuerySet of suppliers with their total purchase amount
        """
        return self.repository.get_total_by_supplier()

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating a purchase order.

        Args:
            data: The purchase order data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        required_fields = ["supplier", "expected_delivery_date"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Generate PO number if not provided
        if "order_number" not in data:
            # Generate a unique PO number (e.g., PO-YYYYMMDD-XXXX)
            today = timezone.now().strftime("%Y%m%d")
            last_po = (
                self.model_class.objects.filter(order_number__startswith=f"PO-{today}")
                .order_by("-order_number")
                .first()
            )

            if last_po:
                last_number = int(last_po.order_number.split("-")[-1])
                new_number = f"PO-{today}-{last_number + 1:04d}"
            else:
                new_number = f"PO-{today}-0001"

            data["order_number"] = new_number

        # Set initial status if not provided
        if "status" not in data:
            data["status"] = "draft"

        # Initialize total amount if not provided
        if "total_amount" not in data:
            data["total_amount"] = Decimal("0.00")

    def _validate_update(self, entity: PurchaseOrder, data: Dict[str, Any]) -> None:
        """
        Validate data before updating a purchase order.

        Args:
            entity: The purchase order to update
            data: The updated data

        Raises:
            ValueError: If the data is invalid
        """
        # Prevent changing supplier for non-draft orders
        if "supplier" in data and entity.status != "draft":
            raise ValueError("Cannot change supplier for non-draft orders")

        # Prevent changing order number
        if "order_number" in data and data["order_number"] != entity.order_number:
            raise ValueError("Cannot change purchase order number")


class PurchaseOrderItemService(BaseService[PurchaseOrderItem]):
    """
    Service for PurchaseOrderItem business logic.

    This class provides business logic operations for the PurchaseOrderItem model.
    """

    def __init__(self):
        """
        Initialize the service with a PurchaseOrderItemRepository.
        """
        super().__init__(PurchaseOrderItemRepository())

    def get_by_order(self, order_id: int) -> QuerySet:
        """
        Get items for a specific purchase order.

        Args:
            order_id: The purchase order ID

        Returns:
            QuerySet of items for the specified purchase order
        """
        return self.repository.get_by_order(order_id)

    def get_by_material(self, material_id: int) -> QuerySet:
        """
        Get purchase order items for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of purchase order items for the specified material
        """
        return self.repository.get_by_material(material_id)

    def get_pending_receipt_items(self) -> QuerySet:
        """
        Get items that have been ordered but not fully received.

        Returns:
            QuerySet of items pending receipt
        """
        return self.repository.get_pending_receipt_items()

    def get_most_ordered_materials(self, limit: int = 10) -> QuerySet:
        """
        Get most frequently ordered materials.

        Args:
            limit: Maximum number of materials to return

        Returns:
            QuerySet of most ordered materials
        """
        return self.repository.get_most_ordered_materials(limit)

    def get_average_price_by_material(self) -> QuerySet:
        """
        Get average price by material.

        Returns:
            QuerySet of materials with their average price
        """
        return self.repository.get_average_price_by_material()

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating a purchase order item.

        Args:
            data: The purchase order item data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        required_fields = ["purchase_order", "material", "quantity", "unit_price"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Ensure quantity is positive
        if data["quantity"] <= 0:
            raise ValueError("Quantity must be positive")

        # Ensure unit price is positive
        if data["unit_price"] <= 0:
            raise ValueError("Unit price must be positive")

        # Initialize receipt fields if not provided
        if "received_quantity" not in data:
            data["received_quantity"] = 0

        if "is_received" not in data:
            data["is_received"] = False

        # Calculate total price if not provided
        if "total_price" not in data:
            data["total_price"] = data["quantity"] * data["unit_price"]

        # Update purchase order total amount
        purchase_order = data["purchase_order"]
        purchase_order.total_amount += data["total_price"]
        purchase_order.save()

    def _after_update(self, entity: PurchaseOrderItem) -> None:
        """
        Perform actions after updating a purchase order item.

        Args:
            entity: The updated purchase order item
        """
        # Recalculate total price if quantity or unit price changed
        if entity.total_price != entity.quantity * entity.unit_price:
            old_total_price = entity.total_price
            entity.total_price = entity.quantity * entity.unit_price
            entity.save()

            # Update purchase order total amount
            purchase_order = entity.purchase_order
            purchase_order.total_amount = (
                purchase_order.total_amount - old_total_price + entity.total_price
            )
            purchase_order.save()


# The duplicate SupplierContactService class has been removed and consolidated with the one at the top of the file
