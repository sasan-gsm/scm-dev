from typing import Optional, Dict, Any, List
from django.db.models import QuerySet
from django.utils import timezone

from core.common.services import BaseService
from .models import Notification, NotificationTemplate, NotificationSetting, AlertRule
from .repositories import (
    NotificationRepository,
    NotificationTemplateRepository,
    NotificationSettingRepository,
)


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

    def get_unread_count(self, user_id: int) -> int:
        """
        Get count of unread notifications for a specific user.

        Args:
            user_id: The user ID

        Returns:
            Count of unread notifications
        """
        return self.repository.get_unread_notifications(user_id).count()

    def get_by_type(self, notification_type: str) -> QuerySet:
        """
        Get notifications of a specific type.

        Args:
            notification_type: The notification type

        Returns:
            QuerySet of notifications of the specified type
        """
        return self.repository.get_by_type(notification_type)

    def get_recent(self, days: int = 7) -> QuerySet:
        """
        Get recent notifications.

        Args:
            days: Number of days to consider as recent

        Returns:
            QuerySet of recent notifications
        """
        return self.repository.get_recent(days)

    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        """
        Mark a notification as read.

        Args:
            notification_id: The notification ID

        Returns:
            The updated notification if found, None otherwise
        """
        return self.repository.mark_as_read(notification_id)

    def mark_all_as_read(self, user_id: int) -> int:
        """
        Mark all notifications for a user as read.

        Args:
            user_id: The user ID

        Returns:
            Number of notifications marked as read
        """
        return self.repository.mark_all_as_read(user_id)

    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = None,
        content_type=None,
        object_id=None,
        alert_rule=None,
    ) -> Notification:
        """
        Create a new notification.

        Args:
            user_id: The user ID
            title: The notification title
            message: The notification message
            notification_type: The notification type
            content_type: The content type for generic relation
            object_id: The object ID for generic relation
            alert_rule: The related alert rule

        Returns:
            The created notification
        """
        data = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "is_read": False,
        }

        if notification_type:
            data["notification_type"] = notification_type

        if content_type:
            data["content_type"] = content_type

        if object_id:
            data["object_id"] = object_id

        if alert_rule:
            data["alert_rule"] = alert_rule

        return self.create(data)


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

    def get_or_create_default(
        self, user_id: int, notification_type: str
    ) -> NotificationSetting:
        """
        Get or create a notification setting with default values.

        Args:
            user_id: The user ID
            notification_type: The notification type

        Returns:
            The notification setting
        """
        setting = self.get_by_type(user_id, notification_type)
        if not setting:
            setting = self.create(
                {
                    "user_id": user_id,
                    "notification_type": notification_type,
                    "email_enabled": True,
                    "push_enabled": True,
                    "in_app_enabled": True,
                }
            )
        return setting


class NotificationTemplateService(BaseService[NotificationTemplate]):
    """
    Service for NotificationTemplate business logic.
    """

    def __init__(self):
        """
        Initialize the service with a NotificationTemplateRepository.
        """
        super().__init__(NotificationTemplateRepository())

    def get_by_code(self, code: str) -> Optional[NotificationTemplate]:
        """
        Retrieve a notification template by its code.

        Args:
            code: The template code

        Returns:
            The notification template if found, None otherwise
        """
        return self.repository.get_by_code(code)

    def get_by_type(self, notification_type: str) -> QuerySet:
        """
        Get notification templates for a specific notification type.

        Args:
            notification_type: The notification type

        Returns:
            QuerySet of notification templates for the specified type
        """
        return self.repository.get_by_type(notification_type)

    def get_active_templates(self) -> QuerySet:
        """
        Get active notification templates.

        Returns:
            QuerySet of active notification templates
        """
        return self.repository.get_active_templates()

    def render_template(
        self, template_code: str, context: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Render a notification template with the given context.

        Args:
            template_code: The template code
            context: The context data for rendering

        Returns:
            Dictionary with rendered subject and body
        """
        template = self.get_by_code(template_code)
        if not template:
            raise ValueError(f"Template with code '{template_code}' not found")

        # Simple template rendering (could be enhanced with a proper template engine)
        subject = template.subject
        body = template.body

        # Replace placeholders in the template
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            subject = subject.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))

        return {"subject": subject, "body": body}


class AlertRuleService(BaseService[AlertRule]):
    """
    Service for AlertRule business logic.
    """

    def __init__(self):
        """
        Initialize the service with an AlertRuleRepository.
        """
        from .repositories import AlertRuleRepository

        super().__init__(AlertRuleRepository())

    def get_active_rules(self) -> QuerySet:
        """
        Get all active alert rules.

        Returns:
            QuerySet of active alert rules
        """
        return self.repository.get_active_rules()

    def get_by_type(self, alert_type: str) -> QuerySet:
        """
        Get alert rules of a specific type.

        Args:
            alert_type: The alert type

        Returns:
            QuerySet of alert rules of the specified type
        """
        return self.repository.get_by_type(alert_type)

    def get_by_material(self, material_id: int) -> QuerySet:
        """
        Get alert rules for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of alert rules for the specified material
        """
        return self.repository.get_by_material(material_id)

    def toggle_active_status(self, rule_id: int) -> Optional[AlertRule]:
        """
        Toggle the active status of an alert rule.

        Args:
            rule_id: The alert rule ID

        Returns:
            The updated alert rule if found, None otherwise
        """
        rule = self.get_by_id(rule_id)
        if not rule:
            return None

        return self.update(rule_id, {"is_active": not rule.is_active})

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating an alert rule.

        Args:
            data: The alert rule data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        required_fields = ["name", "alert_type", "created_by"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Validate material is provided for inventory_low alert type
        if data.get("alert_type") == "inventory_low" and "material" not in data:
            raise ValueError("Material is required for inventory low alerts")

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating an alert rule.

        Args:
            data: The alert rule data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        required_fields = ["name", "alert_type", "created_by"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Validate material is provided for inventory_low alert type
        if data.get("alert_type") == "inventory_low" and "material" not in data:
            raise ValueError("Material is required for inventory low alerts")
