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
    filename = serializers.SerializerMethodField()
    object_type = serializers.SerializerMethodField()
    content_type_group = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = [
            "id",
            "file",
            "name",
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
            "name",
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

    def get_filename(self, obj):
        """Get the filename from the file field."""
        if obj.file:
            return obj.file.name.split("/")[-1]
        return None

    def get_object_type(self, obj):
        """Get the object type (model name) from the content type."""
        if obj.content_type:
            return obj.content_type.model
        return None

    def get_content_type_group(self, obj):
        """Get the content type group based on file type."""
        if obj.file_type:
            if obj.file_type.lower() in [
                "jpg",
                "jpeg",
                "png",
                "gif",
                "bmp",
                "svg",
                "webp",
            ]:
                return "image"
            elif obj.file_type.lower() in [
                "pdf",
                "doc",
                "docx",
                "xls",
                "xlsx",
                "ppt",
                "pptx",
                "txt",
                "csv",
            ]:
                return "document"
        return "other"
