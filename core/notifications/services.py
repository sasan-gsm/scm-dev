from typing import Optional, Dict, Any, List
from django.db.models import QuerySet
from django.utils import timezone

from core.common.services import BaseService
from .repositories import NotificationRepository
from .models import Notification


class NotificationService(BaseService[Notification]):
    """
    Service for Notification business logic.
    """

    def __init__(self):
        """
        Initialize the service with a NotificationRepository.
        """
        super().__init__(NotificationRepository())

    def get_user_notifications(self, user_id: int) -> QuerySet:
        """
        Get notifications for a specific user.

        Args:
            user_id: The user ID

        Returns:
            QuerySet of notifications for the specified user
        """
        return self.repository.get_user_notifications(user_id)

    def get_unread_notifications(self, user_id: int) -> QuerySet:
        """
        Get unread notifications for a specific user.

        Args:
            user_id: The user ID

        Returns:
            QuerySet of unread notifications for the specified user
        """
        return self.repository.get_unread_notifications(user_id)

    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        """
        Mark a notification as read.

        Args:
            notification_id: The notification ID

        Returns:
            The updated notification if found, None otherwise
        """
        return self.update(
            notification_id, {"is_read": True, "read_at": timezone.now()}
        )

    def mark_all_as_read(self, user_id: int) -> int:
        """
        Mark all notifications for a user as read.

        Args:
            user_id: The user ID

        Returns:
            Number of notifications marked as read
        """
        return self.repository.mark_all_as_read(user_id)
