from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from core.materials.services import MaterialService, MaterialCategoryService
from .serializers import (
    MaterialListSerializer,
    MaterialDetailSerializer,
    MaterialCreateUpdateSerializer,
    MaterialCategorySerializer,
)


class MaterialViewSet(viewsets.ModelViewSet):
    """
    API endpoint for materials.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {"category": ["exact"], "is_active": ["exact"]}
    search_fields = ["name", "code", "description"]
    ordering_fields = ["name", "code", "unit_price", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "list":
            return MaterialListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return MaterialCreateUpdateSerializer
        return MaterialDetailSerializer

    def get_queryset(self):
        service = MaterialService()
        return service.get_all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = MaterialService()
        try:
            material = service.create(serializer.validated_data)
            return Response(
                MaterialDetailSerializer(material).data, status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        service = MaterialService()
        try:
            material = service.update(instance.id, serializer.validated_data)
            if material:
                return Response(MaterialDetailSerializer(material).data)
            return Response(
                {"detail": "Material not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def low_inventory(self, request):
        """Get materials with low inventory levels."""
        service = MaterialService()
        materials = service.get_low_inventory_materials()
        page = self.paginate_queryset(materials)

        if page is not None:
            serializer = MaterialListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MaterialListSerializer(materials, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_category(self, request):
        """Get materials by category."""
        category_id = request.query_params.get("category_id")
        if not category_id:
            return Response(
                {"detail": "Category ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = MaterialService()
        materials = service.get_by_category(category_id)
        page = self.paginate_queryset(materials)

        if page is not None:
            serializer = MaterialListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MaterialListSerializer(materials, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def update_price(self, request, pk=None):
        """Update the price of a material."""
        price = request.data.get("price")
        effective_date = request.data.get("effective_date")
        notes = request.data.get("notes", "")

        if not price:
            return Response(
                {"detail": "Price is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            price = float(price)
        except ValueError:
            return Response(
                {"detail": "Price must be a valid number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if effective_date:
            try:
                effective_date = timezone.datetime.strptime(
                    effective_date, "%Y-%m-%d"
                ).date()
            except ValueError:
                return Response(
                    {"detail": "Effective date must be in YYYY-MM-DD format."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        service = MaterialService()
        material = service.update_price(
            pk, price, effective_date, request.user.id, notes
        )

        if not material:
            return Response(
                {"detail": "Material not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(MaterialDetailSerializer(material).data)


class MaterialCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for material categories.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MaterialCategorySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["parent"]
    search_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]

    def get_queryset(self):
        """Get the list of material categories for this view."""
        service = MaterialCategoryService()
        return service.get_all()

    @action(detail=False, methods=["get"])
    def root_categories(self, request):
        """Get root categories (categories without parents)."""
        service = MaterialCategoryService()
        categories = service.get_root_categories()
        serializer = MaterialCategorySerializer(categories, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def subcategories(self, request, pk=None):
        """Get subcategories of a category."""
        service = MaterialCategoryService()
        categories = service.get_subcategories(pk)
        serializer = MaterialCategorySerializer(categories, many=True)
        return Response(serializer.data)
