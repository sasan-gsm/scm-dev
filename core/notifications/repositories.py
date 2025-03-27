from typing import Optional, List
from django.db.models import Q, QuerySet
from django.utils import timezone

from core.common.repositories import BaseRepository
from .models import Notification, NotificationTemplate, NotificationSetting


class NotificationRepository(BaseRepository[Notification]):
    """
    Repository for Notification model operations.

    Provides data access operations specific to the Notification model.
    """

    def __init__(self):
        """
        Initialize the repository with the Notification model.
        """
        super().__init__(Notification)

    def get_user_notifications(self, user_id: int) -> QuerySet:
        """
        Get notifications for a specific user.

        Args:
            user_id: The user ID

        Returns:
            QuerySet of notifications for the specified user
        """
        return self.model_class.objects.filter(user_id=user_id)

    def get_unread_notifications(self, user_id: int) -> QuerySet:
        """
        Get unread notifications for a specific user.

        Args:
            user_id: The user ID

        Returns:
            QuerySet of unread notifications for the specified user
        """
        return self.model_class.objects.filter(user_id=user_id, is_read=False)

    def get_by_type(self, notification_type: str) -> QuerySet:
        """
        Get notifications of a specific type.

        Args:
            notification_type: The notification type

        Returns:
            QuerySet of notifications of the specified type
        """
        return self.model_class.objects.filter(notification_type=notification_type)

    def get_recent(self, days: int = 7) -> QuerySet:
        """
        Get recent notifications.

        Args:
            days: Number of days to consider as recent

        Returns:
            QuerySet of recent notifications
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return self.model_class.objects.filter(created_at__gte=cutoff_date)

    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        """
        Mark a notification as read.

        Args:
            notification_id: The notification ID

        Returns:
            The updated notification if found, None otherwise
        """
        notification = self.get_by_id(notification_id)
        if notification:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            return notification
        return None

    def mark_all_as_read(self, user_id: int) -> int:
        """
        Mark all notifications for a user as read.

        Args:
            user_id: The user ID

        Returns:
            Number of notifications marked as read
        """
        unread_notifications = self.get_unread_notifications(user_id)
        count = unread_notifications.count()
        unread_notifications.update(is_read=True, read_at=timezone.now())
        return count


class NotificationTemplateRepository(BaseRepository[NotificationTemplate]):
    """
    Repository for NotificationTemplate model operations.

    Provides data access operations specific to the NotificationTemplate model.
    """

    def __init__(self):
        """
        Initialize the repository with the NotificationTemplate model.
        """
        super().__init__(NotificationTemplate)

    def get_by_code(self, code: str) -> Optional[NotificationTemplate]:
        """
        Retrieve a notification template by its code.

        Args:
            code: The template code

        Returns:
            The notification template if found, None otherwise
        """
        try:
            return self.model_class.objects.get(code=code)
        except self.model_class.DoesNotExist:
            return None

    def get_by_type(self, notification_type: str) -> QuerySet:
        """
        Get notification templates for a specific notification type.

        Args:
            notification_type: The notification type

        Returns:
            QuerySet of notification templates for the specified type
        """
        return self.model_class.objects.filter(notification_type=notification_type)

    def get_active_templates(self) -> QuerySet:
        """
        Get active notification templates.

        Returns:
            QuerySet of active notification templates
        """
        return self.model_class.objects.filter(is_active=True)


class NotificationSettingRepository(BaseRepository[NotificationSetting]):
    """
    Repository for NotificationSetting model operations.

    Provides data access operations specific to the NotificationSetting model.
    """

    def __init__(self):
        """
        Initialize the repository with the NotificationSetting model.
        """
        super().__init__(NotificationSetting)

    def get_user_settings(self, user_id: int) -> QuerySet:
        """
        Get notification settings for a specific user.

        Args:
            user_id: The user ID

        Returns:
            QuerySet of notification settings for the specified user
        """
        return self.model_class.objects.filter(user_id=user_id)

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
        try:
            return self.model_class.objects.get(
                user_id=user_id, notification_type=notification_type
            )
        except self.model_class.DoesNotExist:
            return None
