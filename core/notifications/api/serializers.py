from rest_framework import serializers
from django.contrib.auth import get_user_model

from core.notifications.models import Notification, NotificationSetting

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    """

    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "title",
            "message",
            "notification_type",
            "is_read",
            "created_at",
            "content_type",
            "object_id",
            "alert_rule",
            "read_at",
        ]
        read_only_fields = ["id", "created_at", "read_at"]


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Notifications with minimal information.
    """

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class NotificationSettingSerializer(serializers.ModelSerializer):
    """
    Serializer for NotificationSetting model.
    """

    class Meta:
        model = NotificationSetting
        fields = [
            "id",
            "user",
            "notification_type",
            "email_enabled",
            "push_enabled",
            "in_app_enabled",
        ]
        read_only_fields = ["id"]
