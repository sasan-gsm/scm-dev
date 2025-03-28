from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from core.attachments.models import Attachment
from core.attachments.services import AttachmentService
from .serializers import AttachmentSerializer


class AttachmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for attachments.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AttachmentSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["object_type", "object_id", "content_type_group"]
    search_fields = ["filename", "description"]
    ordering_fields = ["created_at", "file_size"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Get the list of attachments for this view."""
        service = AttachmentService()
        return service.get_all()

    def perform_create(self, serializer):
        """Set the uploaded_by field to the current user."""
        serializer.save(uploaded_by=self.request.user)

    @action(detail=False, methods=["get"])
    def by_object(self, request):
        """Get attachments for a specific object."""
        object_type = request.query_params.get("object_type")
        object_id = request.query_params.get("object_id")

        if not object_type or not object_id:
            return Response(
                {"detail": "Both object_type and object_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = AttachmentService()
        attachments = service.get_by_object(object_type, object_id)
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def images(self, request):
        """Get image attachments."""
        service = AttachmentService()
        attachments = service.get_by_content_type_group("image")
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def documents(self, request):
        """Get document attachments."""
        service = AttachmentService()
        attachments = service.get_by_content_type_group("document")
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data)
