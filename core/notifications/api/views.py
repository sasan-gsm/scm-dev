from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from core.notifications.models import Notification, NotificationSetting
from core.notifications.services import NotificationService, NotificationSettingService
from .serializers import (
    NotificationSerializer,
    NotificationListSerializer,
    NotificationSettingSerializer,
)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for notifications.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["notification_type", "is_read"]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return NotificationListSerializer
        return NotificationSerializer

    def get_queryset(self):
        """Get the list of notifications for the current user."""
        service = NotificationService()
        return service.get_user_notifications(self.request.user.id)

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        """Mark a notification as read."""
        service = NotificationService()
        try:
            notification = service.mark_as_read(pk)
            if notification:
                return Response(NotificationSerializer(notification).data)
            return Response(
                {"detail": "Notification not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        """Mark all notifications as read."""
        service = NotificationService()
        service.mark_all_as_read(request.user.id)
        return Response({"status": "All notifications marked as read"})

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Get the count of unread notifications."""
        service = NotificationService()
        count = service.get_unread_count(request.user.id)
        return Response({"unread_count": count})


class NotificationSettingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for notification settings.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSettingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["notification_type"]

    def get_queryset(self):
        """Get the list of notification settings for the current user."""
        service = NotificationSettingService()
        return service.get_user_settings(self.request.user.id)

    def create(self, request, *args, **kwargs):
        """Create a new notification setting."""
        # Ensure the user is set to the current user
        data = request.data.copy()
        data["user"] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        service = NotificationSettingService()
        try:
            setting = service.create(serializer.validated_data)
            return Response(
                NotificationSettingSerializer(setting).data,
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update an existing notification setting."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Ensure the user is set to the current user
        data = request.data.copy()
        data["user"] = request.user.id

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)

        service = NotificationSettingService()
        try:
            setting = service.update(instance.id, serializer.validated_data)
            if setting:
                return Response(NotificationSettingSerializer(setting).data)
            return Response(
                {"detail": "Notification setting not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
