from typing import Optional, List
from django.db.models import Q, QuerySet, Count, Sum, F
from django.utils import timezone

from core.common.repositories import BaseRepository
from .models import Request, RequestItem


class RequestRepository(BaseRepository[Request]):
    """
    Repository for Request model operations.

    Provides data access operations specific to the Request model.
    """

    def __init__(self):
        """
        Initialize the repository with the Request model.
        """
        super().__init__(Request)

    def get_by_number(self, number: str) -> Optional[Request]:
        """
        Retrieve a request by its number.

        Args:
            number: The request number

        Returns:
            The request if found, None otherwise
        """
        try:
            return self.model_class.objects.get(number=number)
        except self.model_class.DoesNotExist:
            return None

    def get_by_requester(self, requester_id: int) -> QuerySet:
        """
        Get requests created by a specific user.

        Args:
            requester_id: The requester ID

        Returns:
            QuerySet of requests created by the specified user
        """
        return self.model_class.objects.filter(requester_id=requester_id)

    def get_by_project(self, project_id: int) -> QuerySet:
        """
        Get requests for a specific project.

        Args:
            project_id: The project ID

        Returns:
            QuerySet of requests for the specified project
        """
        return self.model_class.objects.filter(project_id=project_id)

    def get_pending_approval(self) -> QuerySet:
        """
        Get requests pending approval.

        Returns:
            QuerySet of requests pending approval
        """
        return self.model_class.objects.filter(status="pending_approval")

    def get_approved_requests(self) -> QuerySet:
        """
        Get approved requests.

        Returns:
            QuerySet of approved requests
        """
        return self.model_class.objects.filter(status="approved")

    def get_requests_by_date_range(self, start_date, end_date) -> QuerySet:
        """
        Get requests created within a date range.

        Args:
            start_date: The start date
            end_date: The end date

        Returns:
            QuerySet of requests within the specified date range
        """
        return self.model_class.objects.filter(
            created_at__gte=start_date, created_at__lte=end_date
        )

    def get_requests_with_items(self) -> QuerySet:
        """
        Get requests with their items prefetched.

        Returns:
            QuerySet of requests with prefetched items
        """
        return self.model_class.objects.prefetch_related("items")


class RequestItemRepository(BaseRepository[RequestItem]):
    """
    Repository for RequestItem model operations.

    Provides data access operations specific to the RequestItem model.
    """

    def __init__(self):
        """
        Initialize the repository with the RequestItem model.
        """
        super().__init__(RequestItem)

    def get_by_request(self, request_id: int) -> QuerySet:
        """
        Get items for a specific request.

        Args:
            request_id: The request ID

        Returns:
            QuerySet of items for the specified request
        """
        return self.model_class.objects.filter(request_id=request_id)

    def get_by_material(self, material_id: int) -> QuerySet:
        """
        Get request items for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of request items for the specified material
        """
        return self.model_class.objects.filter(material_id=material_id)

    def get_pending_fulfillment_items(self) -> QuerySet:
        """
        Get items that have been approved but not fully fulfilled.

        Returns:
            QuerySet of items pending fulfillment
        """
        return self.model_class.objects.filter(
            quantity_fulfilled__lt=F("quantity"),
            request__status="approved",
            is_fulfilled=False,
        )

    def get_most_requested_materials(self, limit: int = 10) -> QuerySet:
        """
        Get most frequently requested materials.

        Args:
            limit: Maximum number of materials to return

        Returns:
            QuerySet of most requested materials
        """
        return (
            self.model_class.objects.values("material")
            .annotate(request_count=Count("id"), total_quantity=Sum("quantity"))
            .order_by("-request_count")[:limit]
        )
