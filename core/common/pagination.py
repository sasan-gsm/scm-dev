from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from django.db.models import QuerySet
from typing import Optional, List, Dict, Any, Union


class CursorPaginationWithCount(CursorPagination):
    """
    Extends CursorPagination to include a count of total items.

    This is particularly useful for the inventory transaction listing
    which can contain thousands of records.
    """

    page_size: int = 100
    page_size_query_param: str = "page_size"
    max_page_size: int = 1000
    ordering: str = "-created_at"  # Default ordering
    count: Optional[int] = None

    def paginate_queryset(
        self, queryset: Union[QuerySet, List], request: Any, view: Optional[Any] = None
    ) -> Optional[List]:
        """
        Paginate a queryset and calculate the total count.

        Args:
            queryset: The queryset to paginate
            request: The request object
            view: The view that called this paginator

        Returns:
            A list of paginated items or None if pagination is not needed
        """
        # Get the paginated result from the parent class
        result = super().paginate_queryset(queryset, request, view)

        # If we have a result, add a count
        if result and isinstance(queryset, QuerySet):
            self.count = queryset.count()
        return result

    def get_paginated_response(self, data: List[Dict[str, Any]]) -> Response:
        """
        Return a paginated response with count information.

        Args:
            data: The serialized data to include in the response

        Returns:
            Response object with pagination metadata and results
        """
        # Get the standard response from parent
        response = super().get_paginated_response(data)

        # Add the count to the response
        response.data["count"] = getattr(self, "count", None)
        return response
