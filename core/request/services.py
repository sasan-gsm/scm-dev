from typing import Optional, Dict, Any, List
from django.db.models import QuerySet, F
from django.utils import timezone
from django.db import transaction

from core.common.services import BaseService
from .repositories import RequestRepository, RequestItemRepository
from .models import Request, RequestItem
from core.inventory.services import InventoryService


class RequestService(BaseService[Request]):
    """
    Service for Request business logic.

    This class provides business logic operations for the Request model.
    """

    def __init__(self):
        """
        Initialize the service with a RequestRepository.
        """
        super().__init__(RequestRepository())

    def get_by_number(self, number: str) -> Optional[Request]:
        """
        Get a request by its number.

        Args:
            number: The request number

        Returns:
            The request if found, None otherwise
        """
        return self.repository.get_by_number(number)

    def get_by_requester(self, requester_id: int) -> QuerySet:
        """
        Get requests created by a specific user.

        Args:
            requester_id: The requester ID

        Returns:
            QuerySet of requests created by the specified user
        """
        return self.repository.get_by_requester(requester_id)

    def get_by_project(self, project_id: int) -> QuerySet:
        """
        Get requests for a specific project.

        Args:
            project_id: The project ID

        Returns:
            QuerySet of requests for the specified project
        """
        return self.repository.get_by_project(project_id)

    def get_pending_approval(self) -> QuerySet:
        """
        Get requests pending approval.

        Returns:
            QuerySet of requests pending approval
        """
        return self.repository.get_pending_approval()

    def get_approved_requests(self) -> QuerySet:
        """
        Get approved requests.

        Returns:
            QuerySet of approved requests
        """
        return self.repository.get_approved_requests()

    def get_requests_by_date_range(self, start_date, end_date) -> QuerySet:
        """
        Get requests created within a date range.

        Args:
            start_date: The start date
            end_date: The end date

        Returns:
            QuerySet of requests within the specified date range
        """
        return self.repository.get_requests_by_date_range(start_date, end_date)

    def approve_request(self, request_id: int, approver_id: int) -> Optional[Request]:
        """
        Approve a request.

        Args:
            request_id: The request ID
            approver_id: The approver ID

        Returns:
            The approved request if found, None otherwise
        """
        # Get the request
        request = self.get_by_id(request_id)
        if not request:
            return None

        # Ensure request is pending approval
        if request.status != "pending_approval":
            raise ValueError(
                f"Request is not pending approval (current status: {request.status})"
            )

        # Update the request
        return self.update(
            request_id,
            {
                "status": "approved",
                "approver_id": approver_id,
                "approval_date": timezone.now(),
            },
        )

    def reject_request(
        self, request_id: int, approver_id: int, reason: str
    ) -> Optional[Request]:
        """
        Reject a request.

        Args:
            request_id: The request ID
            approver_id: The approver ID
            reason: The rejection reason

        Returns:
            The rejected request if found, None otherwise
        """
        # Get the request
        request = self.get_by_id(request_id)
        if not request:
            return None

        # Ensure request is pending approval
        if request.status != "pending_approval":
            raise ValueError(
                f"Request is not pending approval (current status: {request.status})"
            )

        # Update the request
        return self.update(
            request_id,
            {
                "status": "rejected",
                "approver_id": approver_id,
                "approval_date": timezone.now(),
                "rejection_reason": reason,
            },
        )

    def fulfill_request(self, request_id: int) -> Optional[Request]:
        """
        Fulfill a request by updating inventory.

        Args:
            request_id: The request ID

        Returns:
            The fulfilled request if found, None otherwise
        """
        # Get the request
        request = self.get_by_id(request_id)
        if not request:
            return None

        # Ensure request is approved
        if request.status != "approved":
            raise ValueError(
                f"Request is not approved (current status: {request.status})"
            )

        # Get request items
        item_repository = RequestItemRepository()
        items = item_repository.get_by_request(request_id)

        # Fulfill each item
        inventory_service = InventoryService()
        item_service = RequestItemService()

        with transaction.atomic():
            for item in items:
                if item.is_fulfilled:
                    continue

                # Get inventory for this material
                inventory = inventory_service.get_by_material(item.material_id)
                if not inventory:
                    raise ValueError(
                        f"No inventory found for material {item.material_id}"
                    )

                # Ensure sufficient quantity
                remaining_quantity = item.quantity - item.quantity_fulfilled
                if inventory.quantity < remaining_quantity:
                    raise ValueError(
                        f"Insufficient inventory for material {item.material_id}"
                    )

                # Update inventory
                inventory_service.adjust_quantity(
                    inventory.id,
                    -remaining_quantity,
                    f"Fulfillment of request {request.number}",
                    "request",
                    request_id,
                )

                # Update request item
                item_service.update(
                    item.id,
                    {
                        "quantity_fulfilled": item.quantity,
                        "is_fulfilled": True,
                        "fulfillment_date": timezone.now(),
                    },
                )

            # Update request status
            return self.update(
                request_id, {"status": "fulfilled", "fulfillment_date": timezone.now()}
            )

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating a request.

        Args:
            data: The request data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        required_fields = ["requester", "project", "purpose"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Generate request number if not provided
        if "number" not in data:
            # Generate a unique request number (e.g., REQ-YYYYMMDD-XXXX)
            today = timezone.now().strftime("%Y%m%d")
            last_request = (
                self.model_class.objects.filter(number__startswith=f"REQ-{today}")
                .order_by("-number")
                .first()
            )

            if last_request:
                last_number = int(last_request.number.split("-")[-1])
                new_number = f"REQ-{today}-{last_number + 1:04d}"
            else:
                new_number = f"REQ-{today}-0001"

            data["number"] = new_number

        # Set initial status if not provided
        if "status" not in data:
            data["status"] = "draft"


class RequestItemService(BaseService[RequestItem]):
    """
    Service for RequestItem business logic.

    This class provides business logic operations for the RequestItem model.
    """

    def __init__(self):
        """
        Initialize the service with a RequestItemRepository.
        """
        super().__init__(RequestItemRepository())

    def get_by_request(self, request_id: int) -> QuerySet:
        """
        Get items for a specific request.

        Args:
            request_id: The request ID

        Returns:
            QuerySet of items for the specified request
        """
        return self.repository.get_by_request(request_id)

    def get_by_material(self, material_id: int) -> QuerySet:
        """
        Get request items for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of request items for the specified material
        """
        return self.repository.get_by_material(material_id)

    def get_pending_fulfillment_items(self) -> QuerySet:
        """
        Get items that have been approved but not fully fulfilled.

        Returns:
            QuerySet of items pending fulfillment
        """
        return self.repository.get_pending_fulfillment_items()

    def get_most_requested_materials(self, limit: int = 10) -> QuerySet:
        """
        Get most frequently requested materials.

        Args:
            limit: Maximum number of materials to return

        Returns:
            QuerySet of most requested materials
        """
        return self.repository.get_most_requested_materials(limit)

    def partially_fulfill_item(
        self, item_id: int, quantity: float
    ) -> Optional[RequestItem]:
        """
        Partially fulfill a request item.

        Args:
            item_id: The request item ID
            quantity: The quantity to fulfill

        Returns:
            The updated request item if found, None otherwise
        """
        # Get the request item
        item = self.get_by_id(item_id)
        if not item:
            return None

        # Ensure request is approved
        if item.request.status != "approved":
            raise ValueError(
                f"Request is not approved (current status: {item.request.status})"
            )

        # Ensure item is not already fulfilled
        if item.is_fulfilled:
            raise ValueError("Item is already fulfilled")

        # Ensure quantity is valid
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        remaining_quantity = item.quantity - item.quantity_fulfilled
        if quantity > remaining_quantity:
            raise ValueError(
                f"Quantity exceeds remaining quantity ({remaining_quantity})"
            )

        # Get inventory for this material
        inventory_service = InventoryService()
        inventory = inventory_service.get_by_material(item.material_id)
        if not inventory:
            raise ValueError(f"No inventory found for material {item.material_id}")

        # Ensure sufficient quantity
        if inventory.quantity < quantity:
            raise ValueError(f"Insufficient inventory for material {item.material_id}")

        # Update inventory
        with transaction.atomic():
            inventory_service.adjust_quantity(
                inventory.id,
                -quantity,
                f"Partial fulfillment of request {item.request.number}",
                "request",
                item.request_id,
            )

            # Update request item
            new_fulfilled_quantity = item.quantity_fulfilled + quantity
            is_fully_fulfilled = new_fulfilled_quantity >= item.quantity

            return self.update(
                item_id,
                {
                    "quantity_fulfilled": new_fulfilled_quantity,
                    "is_fulfilled": is_fully_fulfilled,
                    "fulfillment_date": timezone.now() if is_fully_fulfilled else None,
                },
            )

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating a request item.

        Args:
            data: The request item data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        required_fields = ["request", "material", "quantity"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Ensure quantity is positive
        if data["quantity"] <= 0:
            raise ValueError("Quantity must be positive")

        # Initialize fulfillment fields if not provided
        if "quantity_fulfilled" not in data:
            data["quantity_fulfilled"] = 0

        if "is_fulfilled" not in data:
            data["is_fulfilled"] = False
