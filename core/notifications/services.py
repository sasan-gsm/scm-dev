from typing import Optional, Dict, Any, List
from django.db.models import QuerySet
from django.utils import timezone

from core.common.services import BaseService
from .repositories import NotificationRepository, NotificationSettingRepository
from .models import Notification, NotificationSetting


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

    def get_unread_count(self, user_id: int) -> int:
        """
        Get the count of unread notifications for a user.

        Args:
            user_id: The user ID

        Returns:
            Count of unread notifications
        """
        return self.get_unread_notifications(user_id).count()


class NotificationSettingService(BaseService[NotificationSetting]):
    """
    Service for NotificationSetting business logic.
    """

    def __init__(self):
        """
        Initialize the service with a NotificationSettingRepository.
        """
        super().__init__(NotificationSettingRepository())

    def get_user_settings(self, user_id: int) -> QuerySet:
        """
        Get notification settings for a specific user.

        Args:
            user_id: The user ID

        Returns:
            QuerySet of notification settings for the specified user
        """
        return self.repository.get_user_settings(user_id)

    def get_by_type(
        self, user_id: int, notification_type: str
    ) -> Optional[NotificationSetting]:
        """
        Get notification setting for a specific user and notification type.

        Args:
            user_id: The user ID
            notification_type: The notification type

        Returns:
            The notification setting if found, None otherwise
        """
        return self.repository.get_by_type(user_id, notification_type)

    def create_default_settings(self, user_id: int) -> List[NotificationSetting]:
        """
        Create default notification settings for a user.

        Args:
            user_id: The user ID

        Returns:
            List of created notification settings
        """
        default_types = [choice[0] for choice in NotificationSetting.NOTIFICATION_TYPES]
        settings = []

        for notification_type in default_types:
            data = {
                "user_id": user_id,
                "notification_type": notification_type,
                "email_enabled": True,
                "push_enabled": True,
                "in_app_enabled": True,
            }
            setting = self.create(data)
            settings.append(setting)

        return settings
