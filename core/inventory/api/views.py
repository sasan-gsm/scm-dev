from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction

# Import models
from core.inventory.models import (
    InventoryItem,
    InventoryTransaction,
    Warehouse,
    InventoryLocation,
)

# Import Material from materials app
from core.materials.models import Material

# Import services
from core.inventory.services import (
    InventoryService,
    InventoryTransactionService,
    WarehouseService,
    InventoryLocationService,
)

# Import MaterialService from materials app
from core.materials.services import MaterialService

# Import project service
from core.projects.services import ProjectService

# Import serializers
from .serializers import (
    InventoryItemListSerializer,
    InventoryItemDetailSerializer,
    InventoryItemCreateUpdateSerializer,
    InventoryTransactionListSerializer,
    InventoryTransactionCreateSerializer,
    InventoryTransactionDetailSerializer,
    WarehouseSerializer,
    WarehouseDetailSerializer,
    InventoryLocationSerializer,
    InventoryLocationDetailSerializer,
)

# Import MaterialSerializer from materials app
from core.materials.api.serializers import MaterialListSerializer
from core.projects.api.serializers import ProjectListSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for warehouses.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_active"]
    search_fields = ["name", "code", "location"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action in ["retrieve", "update", "partial_update"]:
            return WarehouseDetailSerializer
        return WarehouseSerializer

    def get_queryset(self):
        """Get the list of warehouses for this view."""
        service = WarehouseService()
        return service.get_all()

    def create(self, request, *args, **kwargs):
        """Create a new warehouse."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = WarehouseService()
        try:
            warehouse = service.create(serializer.validated_data)
            return Response(
                self.get_serializer(warehouse).data, status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update an existing warehouse."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        service = WarehouseService()
        try:
            warehouse = service.update(instance.id, serializer.validated_data)
            if warehouse:
                return Response(self.get_serializer(warehouse).data)
            return Response(
                {"detail": "Warehouse not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Delete a warehouse."""
        instance = self.get_object()
        service = WarehouseService()

        try:
            result = service.delete(instance.id)
            if result:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"detail": "Warehouse not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class InventoryLocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for inventory locations.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["warehouse"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code"]
    ordering = ["name"]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action in ["retrieve", "update", "partial_update"]:
            return InventoryLocationDetailSerializer
        return InventoryLocationSerializer

    def get_queryset(self):
        """Get the list of inventory locations for this view."""
        service = InventoryLocationService()
        return service.get_all()

    def create(self, request, *args, **kwargs):
        """Create a new inventory location."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = InventoryLocationService()
        try:
            location = service.create(serializer.validated_data)
            return Response(
                self.get_serializer(location).data, status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update an existing inventory location."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        service = InventoryLocationService()
        try:
            location = service.update(instance.id, serializer.validated_data)
            if location:
                return Response(self.get_serializer(location).data)
            return Response(
                {"detail": "Location not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Delete an inventory location."""
        instance = self.get_object()
        service = InventoryLocationService()

        try:
            result = service.delete(instance.id)
            if result:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"detail": "Location not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for inventory items.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["material", "warehouse", "location"]
    search_fields = [
        "material__name",
        "material__code",
        "warehouse__name",
        "location__name",
    ]
    ordering_fields = ["quantity", "created_at", "updated_at"]
    ordering = ["-updated_at"]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return InventoryItemListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return InventoryItemCreateUpdateSerializer
        return InventoryItemDetailSerializer

    def get_queryset(self):
        """Get the list of inventory items for this view."""
        service = InventoryService()
        return service.get_all()

    def create(self, request, *args, **kwargs):
        """Create a new inventory item."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = InventoryService()
        try:
            item = service.create(serializer.validated_data)
            return Response(
                InventoryItemDetailSerializer(item).data, status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update an existing inventory item."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        service = InventoryService()
        try:
            item = service.update(instance.id, serializer.validated_data)
            if item:
                return Response(InventoryItemDetailSerializer(item).data)
            return Response(
                {"detail": "Inventory item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Delete an inventory item."""
        instance = self.get_object()
        service = InventoryService()

        try:
            result = service.delete(instance.id)
            if result:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"detail": "Inventory item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def low_inventory(self, request):
        """Get inventory items with low stock."""
        service = InventoryService()
        inventory = service.get_low_inventory()
        page = self.paginate_queryset(inventory)

        if page is not None:
            serializer = InventoryItemListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = InventoryItemListSerializer(inventory, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_material(self, request):
        """Get inventory items for a specific material."""
        material_id = request.query_params.get("material_id")
        if not material_id:
            return Response(
                {"detail": "Material ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = InventoryService()
        inventory = service.get_by_material(material_id)
        serializer = InventoryItemListSerializer(inventory, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_warehouse(self, request):
        """Get inventory items for a specific warehouse."""
        warehouse_id = request.query_params.get("warehouse_id")
        if not warehouse_id:
            return Response(
                {"detail": "Warehouse ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = InventoryService()
        inventory = service.get_by_warehouse(warehouse_id)
        serializer = InventoryItemListSerializer(inventory, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_location(self, request):
        """Get inventory items for a specific location."""
        location_id = request.query_params.get("location_id")
        if not location_id:
            return Response(
                {"detail": "Location ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = InventoryService()
        inventory = service.get_by_location(location_id)
        serializer = InventoryItemListSerializer(inventory, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def adjust_quantity(self, request, pk=None):
        """Adjust the quantity of an inventory item."""
        quantity_change = request.data.get("quantity_change")
        reason = request.data.get("reason")
        project_id = request.data.get("project_id")

        if quantity_change is None:
            return Response(
                {"detail": "Quantity change is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not reason:
            return Response(
                {"detail": "Reason is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantity_change = float(quantity_change)
        except ValueError:
            return Response(
                {"detail": "Quantity change must be a valid number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = InventoryService()
        try:
            item = service.adjust_quantity(
                pk, quantity_change, reason, request.user.id, project_id
            )
            if item:
                return Response(InventoryItemDetailSerializer(item).data)
            return Response(
                {"detail": "Inventory item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for inventory transactions.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "material",
        "transaction_type",
        "project",
        "from_warehouse",
        "to_warehouse",
    ]
    search_fields = ["notes"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return InventoryTransactionListSerializer
        elif self.action == "create":
            return InventoryTransactionCreateSerializer
        return InventoryTransactionDetailSerializer

    def get_queryset(self):
        """Get the list of inventory transactions for this view."""
        service = InventoryTransactionService()
        return service.get_all()

    def create(self, request, *args, **kwargs):
        """Create a new inventory transaction."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Add the user who performed the transaction
        validated_data = serializer.validated_data.copy()
        validated_data["performed_by_id"] = request.user.id

        service = InventoryTransactionService()
        try:
            transaction = service.create(validated_data)
            return Response(
                InventoryTransactionDetailSerializer(transaction).data,
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update is not allowed for transactions."""
        return Response(
            {"detail": "Inventory transactions cannot be updated."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, *args, **kwargs):
        """Delete an inventory transaction."""
        instance = self.get_object()
        service = InventoryTransactionService()

        try:
            result = service.delete(instance.id)
            if result:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"detail": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def by_project(self, request):
        """Get transactions for a specific project."""
        project_id = request.query_params.get("project_id")
        if not project_id:
            return Response(
                {"detail": "Project ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = InventoryTransactionService()
        transactions = service.get_project_transactions(project_id)
        page = self.paginate_queryset(transactions)

        if page is not None:
            serializer = InventoryTransactionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = InventoryTransactionListSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_material(self, request):
        """Get transactions for a specific material."""
        material_id = request.query_params.get("material_id")
        if not material_id:
            return Response(
                {"detail": "Material ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = InventoryTransactionService()
        transactions = service.get_material_transactions(material_id)
        page = self.paginate_queryset(transactions)

        if page is not None:
            serializer = InventoryTransactionListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = InventoryTransactionListSerializer(transactions, many=True)
        return Response(serializer.data)
