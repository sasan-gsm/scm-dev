from typing import Optional, List, Dict, Any
from django.db.models import QuerySet
from django.contrib.contenttypes.models import ContentType

from core.common.services import BaseService
from .repositories import AttachmentRepository
from .models import Attachment


class AttachmentService(BaseService[Attachment]):
    """
    Service for Attachment business logic.

    This class provides business logic operations for the Attachment model.
    """

    def __init__(self):
        """
        Initialize the service with an AttachmentRepository.
        """
        super().__init__(AttachmentRepository())

    def get_by_object(self, object_type: str, object_id: int) -> QuerySet:
        """
        Get attachments for a specific object.

        Args:
            object_type: The object type (model name)
            object_id: The object ID

        Returns:
            QuerySet of attachments for the specified object
        """
        try:
            content_type = ContentType.objects.get(model=object_type.lower())
            return self.repository.model_class.objects.filter(
                content_type=content_type, object_id=object_id
            )
        except ContentType.DoesNotExist:
            return self.repository.model_class.objects.none()

    def get_by_content_type(self, content_type_id: int) -> QuerySet:
        """
        Get attachments for a specific content type.

        Args:
            content_type_id: The content type ID

        Returns:
            QuerySet of attachments for the specified content type
        """
        return self.repository.get_by_content_type(content_type_id)

    def get_by_file_type(self, file_type: str) -> QuerySet:
        """
        Get attachments with a specific file type.

        Args:
            file_type: The file type (extension)

        Returns:
            QuerySet of attachments with the specified file type
        """
        return self.repository.get_by_file_type(file_type)

    def get_by_content_type_group(self, group: str) -> QuerySet:
        """
        Get attachments by content type group (e.g., 'image', 'document').

        Args:
            group: The content type group

        Returns:
            QuerySet of attachments in the specified group
        """
        if group == "image":
            # Common image file extensions
            image_types = ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp"]
            query = self.repository.model_class.objects.none()
            for ext in image_types:
                query = query | self.get_by_file_type(ext)
            return query
        elif group == "document":
            # Common document file extensions
            doc_types = [
                "pdf",
                "doc",
                "docx",
                "xls",
                "xlsx",
                "ppt",
                "pptx",
                "txt",
                "csv",
            ]
            query = self.repository.model_class.objects.none()
            for ext in doc_types:
                query = query | self.get_by_file_type(ext)
            return query
        return self.repository.model_class.objects.none()

    def get_by_uploader(self, uploader_id: int) -> QuerySet:
        """
        Get attachments uploaded by a specific user.

        Args:
            uploader_id: The uploader ID

        Returns:
            QuerySet of attachments uploaded by the specified user
        """
        return self.repository.get_by_uploader(uploader_id)

    def search_attachments(self, query: str) -> QuerySet:
        """
        Search for attachments by name or description.

        Args:
            query: The search query

        Returns:
            QuerySet of matching attachments
        """
        return self.repository.search(query)
