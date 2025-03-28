from rest_framework import serializers
from django.contrib.auth import get_user_model

from core.attachments.models import Attachment

User = get_user_model()


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Attachment model.
    """

    uploaded_by_name = serializers.SerializerMethodField()
    file_size_display = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = [
            "id",
            "file",
            "filename",
            "content_type",
            "file_size",
            "file_size_display",
            "content_type_group",
            "object_type",
            "object_id",
            "description",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "filename",
            "content_type",
            "file_size",
            "content_type_group",
            "created_at",
            "updated_at",
        ]

    def get_uploaded_by_name(self, obj):
        """Get the name of the user who uploaded the file."""
        if obj.uploaded_by:
            return (
                f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}".strip()
                or obj.uploaded_by.username
            )
        return None

    def get_file_size_display(self, obj):
        """Get a human-readable file size."""
        size = obj.file_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
