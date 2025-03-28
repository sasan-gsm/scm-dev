from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from core.procurement.services import (
    SupplierService,
    SupplierContactService,
    PurchaseOrderService,
    PurchaseOrderItemService,
)
from .serializers import (
    SupplierListSerializer,
    SupplierDetailSerializer,
    SupplierContactSerializer,
    PurchaseOrderListSerializer,
    PurchaseOrderDetailSerializer,
    PurchaseOrderCreateSerializer,
    PurchaseOrderUpdateSerializer,
    PurchaseOrderItemSerializer,
)


class SupplierViewSet(viewsets.ModelViewSet):
    """
    API endpoint for suppliers.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_active"]
    search_fields = ["name", "code", "contact_person", "email", "phone"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        """Return the serializer class for supplier."""
        if self.action == "list":
            return SupplierListSerializer
        return SupplierDetailSerializer

    def get_queryset(self):
        """Get the list of suppliers for this view."""
        service = SupplierService()
        return service.get_all()

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get active suppliers."""
        service = SupplierService()
        suppliers = service.get_active_suppliers()
        page = self.paginate_queryset(suppliers)

        if page is not None:
            serializer = SupplierListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SupplierListSerializer(suppliers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def contacts(self, request, pk=None):
        """Get contacts for a specific supplier."""
        service = SupplierContactService()
        contacts = service.get_by_supplier(pk)

        serializer = SupplierContactSerializer(contacts, many=True)
        return Response(serializer.data)


class SupplierContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint for supplier contacts.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SupplierContactSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["supplier", "is_primary"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        """Get the list of supplier contacts for this view."""
        service = SupplierContactService()
        return service.get_all()

    @action(detail=True, methods=["post"])
    def set_primary(self, request, pk=None):
        """Set a contact as the primary contact for its supplier."""
        service = SupplierContactService()
        try:
            contact = service.set_as_primary(pk)
            if contact:
                return Response(SupplierContactSerializer(contact).data)
            return Response(
                {"detail": "Contact not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for purchase orders.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["supplier", "project", "status"]
    search_fields = ["order_number", "notes"]
    ordering_fields = ["order_date", "expected_delivery_date", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return the serializer class for purchase order."""
        if self.action == "list":
            return PurchaseOrderListSerializer
        elif self.action == "create":
            return PurchaseOrderCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return PurchaseOrderUpdateSerializer
        return PurchaseOrderDetailSerializer

    def get_queryset(self):
        """Get the list of purchase orders for this view."""
        service = PurchaseOrderService()
        queryset = service.get_all()

        # Annotate with item count and total amount
        return queryset.annotate(
            item_count=models.Count("items"),
            total_amount=models.Sum(models.F("items__total_price")),
        )

    def create(self, request, *args, **kwargs):
        """Create a new purchase order."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()
        return Response(
            PurchaseOrderDetailSerializer(instance).data, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Update an existing purchase order."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        service = PurchaseOrderService()
        try:
            updated_order = service.update(instance.id, serializer.validated_data)
            if updated_order:
                return Response(PurchaseOrderDetailSerializer(updated_order).data)
            return Response(
                {"detail": "Purchase order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Submit a purchase order for approval."""
        service = PurchaseOrderService()
        try:
            submitted_order = service.submit_for_approval(pk)
            if submitted_order:
                return Response(PurchaseOrderDetailSerializer(submitted_order).data)
            return Response(
                {"detail": "Purchase order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a purchase order."""
        service = PurchaseOrderService()
        try:
            approved_order = service.approve(pk)
            if approved_order:
                return Response(PurchaseOrderDetailSerializer(approved_order).data)
            return Response(
                {"detail": "Purchase order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a purchase order."""
        service = PurchaseOrderService()
        try:
            rejected_order = service.reject(pk)
            if rejected_order:
                return Response(PurchaseOrderDetailSerializer(rejected_order).data)
            return Response(
                {"detail": "Purchase order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a purchase order."""
        service = PurchaseOrderService()
        try:
            cancelled_order = service.cancel(pk)
            if cancelled_order:
                return Response(PurchaseOrderDetailSerializer(cancelled_order).data)
            return Response(
                {"detail": "Purchase order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def receive(self, request, pk=None):
        """Mark a purchase order as received."""
        service = PurchaseOrderService()
        try:
            received_order = service.receive(pk)
            if received_order:
                return Response(PurchaseOrderDetailSerializer(received_order).data)
            return Response(
                {"detail": "Purchase order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def pending_approval(self, request):
        """Get purchase orders pending approval."""
        service = PurchaseOrderService()
        orders = service.get_pending_approval()
        orders = orders.annotate(
            item_count=models.Count("items"),
            total_amount=models.Sum(models.F("items__total_price")),
        )

        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = PurchaseOrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PurchaseOrderListSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def due_soon(self, request):
        """Get purchase orders due soon."""
        days = request.query_params.get("days", 7)
        try:
            days = int(days)
        except ValueError:
            days = 7

        service = PurchaseOrderService()
        orders = service.get_due_soon(days)
        orders = orders.annotate(
            item_count=models.Count("items"),
            total_amount=models.Sum(models.F("items__total_price")),
        )

        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = PurchaseOrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PurchaseOrderListSerializer(orders, many=True)
        return Response(serializer.data)


class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for purchase order items.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PurchaseOrderItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["purchase_order", "material", "status"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Get the list of purchase order items for this view."""
        service = PurchaseOrderItemService()
        return service.get_all()

    @action(detail=True, methods=["post"])
    def receive(self, request, pk=None):
        """Mark a purchase order item as received."""
        service = PurchaseOrderItemService()
        try:
            received_item = service.receive_item(pk)
            if received_item:
                return Response(PurchaseOrderItemSerializer(received_item).data)
            return Response(
                {"detail": "Purchase order item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
