from django.db.models import QuerySet, Count
from typing import Optional
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
        try:
            return self.model_class.objects.get(number=number)
        except self.model_class.DoesNotExist:
            return None

    def get_by_requester(self, requester_id: int) -> QuerySet:
        """
        Get requests created by a specific user.

        Returns:
            QuerySet of requests created by the specified user
        """
        return self.model_class.objects.filter(requester_id=requester_id)

    def get_by_project(self, project_id: int) -> QuerySet:
        """
        Get requests for a specific project.

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

        Returns:
            QuerySet of requests within the specified date range
        """
        return self.model_class.objects.filter(
            request_date__gte=start_date, request_date__lte=end_date
        )

    def get_requests_with_item_count(self) -> QuerySet:
        """
        Get requests with item count annotation.

        Returns:
            QuerySet of requests with item_count annotation
        """
        return self.model_class.objects.annotate(item_count=Count("items"))


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

        Returns:
            QuerySet of items for the specified request
        """
        return self.model_class.objects.filter(request_id=request_id)

    def get_by_material(self, material_id: int) -> QuerySet:
        """
        Get request items for a specific material.

        Returns:
            QuerySet of request items for the specified material
        """
        return self.model_class.objects.filter(material_id=material_id)

    def get_pending_items(self) -> QuerySet:
        """
        Get pending request items.

        Returns:
            QuerySet of pending request items
        """
        return self.model_class.objects.filter(status="pending")

    def get_fulfilled_items(self) -> QuerySet:
        """
        Get fulfilled request items.

        Returns:
            QuerySet of fulfilled request items
        """
        return self.model_class.objects.filter(is_fulfilled=True)
