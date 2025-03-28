from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Case, When, IntegerField

from core.quality.models import QualityCheck, QualityCheckItem, QualityStandard
from core.quality.services import (
    QualityCheckService,
    QualityCheckItemService,
    QualityStandardService,
)
from .serializers import (
    QualityStandardSerializer,
    QualityCheckListSerializer,
    QualityCheckDetailSerializer,
    QualityCheckCreateSerializer,
    QualityCheckUpdateSerializer,
    QualityCheckItemSerializer,
)


class QualityStandardViewSet(viewsets.ModelViewSet):
    """
    API endpoint for quality standards.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QualityStandardSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_active"]
    search_fields = ["name", "code", "description", "criteria"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        """Get the list of quality standards for this view."""
        service = QualityStandardService()
        return service.get_all()


class QualityCheckViewSet(viewsets.ModelViewSet):
    """
    API endpoint for quality checks.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["project", "material", "status", "inspector"]
    search_fields = ["check_number", "batch_number", "notes"]
    ordering_fields = ["check_date", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return QualityCheckListSerializer
        elif self.action == "create":
            return QualityCheckCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return QualityCheckUpdateSerializer
        return QualityCheckDetailSerializer

    def get_queryset(self):
        """Get the list of quality checks for this view."""
        service = QualityCheckService()
        queryset = service.get_all()

        # Annotate with item count and pass rate
        queryset = queryset.annotate(
            item_count=Count("items"),
            pass_rate=Avg(
                Case(
                    When(items__is_passed=True, then=100),
                    When(items__is_passed=False, then=0),
                    default=None,
                    output_field=IntegerField(),
                )
            ),
        )

        return queryset

    def create(self, request, *args, **kwargs):
        """Create a new quality check."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = QualityCheckService()
        try:
            quality_check = service.create(serializer.validated_data)
            return Response(
                QualityCheckDetailSerializer(quality_check).data,
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update an existing quality check."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        service = QualityCheckService()
        try:
            quality_check = service.update(instance.id, serializer.validated_data)
            if quality_check:
                return Response(QualityCheckDetailSerializer(quality_check).data)
            return Response(
                {"detail": "Quality check not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Submit a quality check for approval."""
        service = QualityCheckService()
        try:
            quality_check = service.submit(pk)
            if quality_check:
                return Response(QualityCheckDetailSerializer(quality_check).data)
            return Response(
                {"detail": "Quality check not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a quality check."""
        service = QualityCheckService()
        try:
            quality_check = service.approve(pk)
            if quality_check:
                return Response(QualityCheckDetailSerializer(quality_check).data)
            return Response(
                {"detail": "Quality check not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a quality check."""
        service = QualityCheckService()
        try:
            quality_check = service.reject(pk)
            if quality_check:
                return Response(QualityCheckDetailSerializer(quality_check).data)
            return Response(
                {"detail": "Quality check not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark a quality check as completed."""
        service = QualityCheckService()
        try:
            quality_check = service.complete(pk)
            if quality_check:
                return Response(QualityCheckDetailSerializer(quality_check).data)
            return Response(
                {"detail": "Quality check not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a quality check."""
        service = QualityCheckService()
        try:
            quality_check = service.cancel(pk)
            if quality_check:
                return Response(QualityCheckDetailSerializer(quality_check).data)
            return Response(
                {"detail": "Quality check not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class QualityCheckItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for quality check items.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QualityCheckItemSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["quality_check", "standard", "is_passed"]
    search_fields = ["notes"]
    ordering = ["id"]

    def get_queryset(self):
        """Get the list of quality check items for this view."""
        service = QualityCheckItemService()
        return service.get_all()

    def create(self, request, *args, **kwargs):
        """Create a new quality check item."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = QualityCheckItemService()
        try:
            item = service.create(serializer.validated_data)
            return Response(
                QualityCheckItemSerializer(item).data, status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update an existing quality check item."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        service = QualityCheckItemService()
        try:
            item = service.update(instance.id, serializer.validated_data)
            if item:
                return Response(QualityCheckItemSerializer(item).data)
            return Response(
                {"detail": "Quality check item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
