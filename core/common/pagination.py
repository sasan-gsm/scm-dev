from rest_framework.pagination import CursorPagination
from django.db.models import QuerySet


class CursorPaginationWithCount(CursorPagination):
    """
    Extends CursorPagination to include a count of total items.
    """

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000
    ordering = "-created_at"  # Default ordering

    def paginate_queryset(self, queryset, request, view=None):
        # Get the paginated result from the parent class
        result = super().paginate_queryset(queryset, request, view)

        # If we have a result, add a count
        if result is not None and isinstance(queryset, QuerySet):
            self.count = queryset.count()
        return result

    def get_paginated_response(self, data):
        # Get the standard response from parent
        response = super().get_paginated_response(data)

        # Add the count to the response
        response.data["count"] = getattr(self, "count", None)
        return response
