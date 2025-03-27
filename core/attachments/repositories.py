from typing import Optional, List
from django.db.models import Q, QuerySet
from django.contrib.contenttypes.models import ContentType

from core.common.repositories import BaseRepository
from .models import Attachment


class AttachmentRepository(BaseRepository[Attachment]):
    """
    Repository for Attachment model operations.

    Provides data access operations specific to the Attachment model.
    """

    def __init__(self):
        """
        Initialize the repository with the Attachment model.
        """
        super().__init__(Attachment)

    def get_by_object(self, obj) -> QuerySet:
        """
        Get attachments for a specific object.

        Args:
            obj: The object to get attachments for

        Returns:
            QuerySet of attachments for the specified object
        """
        content_type = ContentType.objects.get_for_model(obj)
        return self.model_class.objects.filter(
            content_type=content_type, object_id=obj.id
        )

    def get_by_content_type(self, content_type_id: int) -> QuerySet:
        """
        Get attachments for a specific content type.

        Args:
            content_type_id: The content type ID

        Returns:
            QuerySet of attachments for the specified content type
        """
        return self.model_class.objects.filter(content_type_id=content_type_id)

    def get_by_file_type(self, file_type: str) -> QuerySet:
        """
        Get attachments with a specific file type.

        Args:
            file_type: The file type (extension)

        Returns:
            QuerySet of attachments with the specified file type
        """
        return self.model_class.objects.filter(file_type__iexact=file_type)

    def get_by_uploader(self, uploader_id: int) -> QuerySet:
        """
        Get attachments uploaded by a specific user.

        Args:
            uploader_id: The uploader ID

        Returns:
            QuerySet of attachments uploaded by the specified user
        """
        return self.model_class.objects.filter(uploaded_by_id=uploader_id)

    def search(self, query: str) -> QuerySet:
        """
        Search for attachments by name or description.

        Args:
            query: The search query

        Returns:
            QuerySet of matching attachments
        """
        return self.model_class.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
