from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from core.request.services import RequestService, RequestItemService
from .serializers import (
    RequestListSerializer,
    RequestDetailSerializer,
    RequestCreateSerializer,
    RequestUpdateSerializer,
    RequestItemSerializer,
    RequestItemUpdateSerializer,
)


class RequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for requests.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["requester", "project", "status", "priority"]
    search_fields = ["number", "notes"]
    ordering_fields = ["request_date", "required_date", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return RequestListSerializer
        elif self.action == "create":
            return RequestCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return RequestUpdateSerializer
        return RequestDetailSerializer

    def get_queryset(self):
        """Get the list of requests for this view."""
        service = RequestService()
        return service.get_all_with_item_count()

    def create(self, request, *args, **kwargs):
        """Create a new request."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()
        return Response(
            RequestDetailSerializer(instance).data, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Update an existing request."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        service = RequestService()
        try:
            updated_request = service.update(instance.id, serializer.validated_data)
            if updated_request:
                return Response(RequestDetailSerializer(updated_request).data)
            return Response(
                {"detail": "Request not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def my_requests(self, request):
        """Get requests created by the current user."""
        service = RequestService()
        requests = service.get_by_requester(request.user.id)
        requests = requests.annotate(item_count=models.Count("items"))
        page = self.paginate_queryset(requests)

        if page is not None:
            serializer = RequestListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = RequestListSerializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def pending_approval(self, request):
        """Get requests pending approval."""
        service = RequestService()
        requests = service.get_pending_approval()
        requests = requests.annotate(item_count=models.Count("items"))
        page = self.paginate_queryset(requests)

        if page is not None:
            serializer = RequestListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = RequestListSerializer(requests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a request."""
        service = RequestService()
        try:
            approved_request = service.approve_request(pk, request.user.id)
            if approved_request:
                return Response(RequestDetailSerializer(approved_request).data)
            return Response(
                {"detail": "Request not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a request."""
        reason = request.data.get("reason", "")
        service = RequestService()
        try:
            rejected_request = service.reject_request(pk, reason)
            if rejected_request:
                return Response(RequestDetailSerializer(rejected_request).data)
            return Response(
                {"detail": "Request not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a request."""
        service = RequestService()
        try:
            cancelled_request = service.cancel_request(pk)
            if cancelled_request:
                return Response(RequestDetailSerializer(cancelled_request).data)
            return Response(
                {"detail": "Request not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def fulfill(self, request, pk=None):
        """Fulfill a request."""
        service = RequestService()
        try:
            fulfilled_request = service.fulfill_request(pk)
            if fulfilled_request:
                return Response(RequestDetailSerializer(fulfilled_request).data)
            return Response(
                {"detail": "Request not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RequestItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for request items.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RequestItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["request", "material", "status"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Get the list of request items for this view."""
        service = RequestItemService()
        return service.get_all()

    def get_serializer_class(self):
        """Return the serializer class for request item."""
        if self.action in ["update", "partial_update"]:
            return RequestItemUpdateSerializer
        return RequestItemSerializer

    def update(self, request, *args, **kwargs):
        """Update an existing request item."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        service = RequestItemService()
        try:
            updated_item = service.update(instance.id, serializer.validated_data)
            if updated_item:
                return Response(RequestItemSerializer(updated_item).data)
            return Response(
                {"detail": "Request item not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def partially_fulfill(self, request, pk=None):
        """Partially fulfill a request item."""
        quantity = request.data.get("quantity", 0)
        try:
            quantity = float(quantity)
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST
            )

        service = RequestItemService()
        try:
            fulfilled_item = service.partially_fulfill_item(pk, quantity)
            if fulfilled_item:
                return Response(RequestItemSerializer(fulfilled_item).data)
            return Response(
                {"detail": "Request item not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
