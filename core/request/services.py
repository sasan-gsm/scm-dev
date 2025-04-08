from typing import Optional
from django.db.models import QuerySet
from django.db import transaction
from django.utils import timezone
from core.common.services import BaseService
from core.inventory.services import InventoryService
from .repositories import RequestRepository, RequestItemRepository
from .models import Request, RequestItem


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

    def get_all_with_item_count(self) -> QuerySet:
        """
        Get all requests with item count annotation.

        Returns:
            QuerySet of all requests with item_count annotation
        """
        return self.repository.get_requests_with_item_count()

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
            request_id, {"status": "approved", "approver_id": approver_id}
        )

    def reject_request(self, request_id: int, reason: str = None) -> Optional[Request]:
        """
        Reject a request.

        Args:
            request_id: The request ID
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
        data = {"status": "rejected"}
        if reason:
            data["notes"] = (request.notes + "\n\nRejection reason: " + reason).strip()

        return self.update(request_id, data)

    def cancel_request(self, request_id: int) -> Optional[Request]:
        """
        Cancel a request.

        Args:
            request_id: The request ID

        Returns:
            The cancelled request if found, None otherwise
        """
        # Get the request
        request = self.get_by_id(request_id)
        if not request:
            return None

        # Ensure request can be cancelled
        if request.status in ["completed", "cancelled", "rejected"]:
            raise ValueError(f"Cannot cancel request with status: {request.status}")

        # Update the request
        return self.update(request_id, {"status": "cancelled"})

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
                        "status": "fulfilled",
                    },
                )

            # Update request status
            return self.update(
                request_id, {"status": "completed", "fulfillment_date": timezone.now()}
            )


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

    def get_pending_items(self) -> QuerySet:
        """
        Get pending request items.

        Returns:
            QuerySet of pending request items
        """
        return self.repository.get_pending_items()

    def get_fulfilled_items(self) -> QuerySet:
        """
        Get fulfilled request items.

        Returns:
            QuerySet of fulfilled request items
        """
        return self.repository.get_fulfilled_items()

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

        # Ensure item is not already fulfilled
        if item.is_fulfilled:
            raise ValueError("Item is already fulfilled")

        # Ensure quantity is valid
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        if quantity > (item.quantity - item.quantity_fulfilled):
            raise ValueError("Quantity exceeds remaining quantity")

        # Update the item
        new_quantity_fulfilled = item.quantity_fulfilled + quantity
        is_fulfilled = new_quantity_fulfilled >= item.quantity
        status = "fulfilled" if is_fulfilled else "partially_fulfilled"

        return self.update(
            item_id,
            {
                "quantity_fulfilled": new_quantity_fulfilled,
                "is_fulfilled": is_fulfilled,
                "status": status,
                "fulfillment_date": timezone.now() if is_fulfilled else None,
            },
        )
