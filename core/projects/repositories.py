from typing import Optional, List
from django.db.models import Q, QuerySet

from core.common.repositories import BaseRepository
from .models import Project


class ProjectRepository(BaseRepository[Project]):
    """
    Repository for Project model operations.

    Provides data access operations specific to the Project model.
    """

    def __init__(self):
        """
        Initialize the repository with the Project model.
        """
        super().__init__(Project)

    def get_by_number(self, number: str) -> Optional[Project]:
        """
        Retrieve a project by its number.

        Args:
            number: The project number

        Returns:
            The project if found, None otherwise
        """
        try:
            return self.model_class.objects.get(number=number)
        except self.model_class.DoesNotExist:
            return None

    def get_active_projects(self) -> QuerySet:
        """
        Retrieve all active projects.

        Returns:
            QuerySet of active projects
        """
        return self.model_class.objects.filter(status="active")

    def get_projects_by_manager(self, manager_id: int) -> QuerySet:
        """
        Retrieve all projects managed by a specific user.

        Args:
            manager_id: The ID of the manager

        Returns:
            QuerySet of projects managed by the specified user
        """
        return self.model_class.objects.filter(manager_id=manager_id)

    def search(self, query: str) -> QuerySet:
        """
        Search for projects by name, number, or description.

        Args:
            query: The search query

        Returns:
            QuerySet of matching projects
        """
        return self.model_class.objects.filter(
            Q(name__icontains=query)
            | Q(number__icontains=query)
            | Q(description__icontains=query)
        )

    def get_projects_ending_soon(self, days: int = 30) -> QuerySet:
        """
        Get projects that are ending within the specified number of days.

        Args:
            days: Number of days from now

        Returns:
            QuerySet of projects ending soon
        """
        from django.utils import timezone
        from datetime import timedelta

        end_date = timezone.now().date() + timedelta(days=days)
        return self.model_class.objects.filter(end_date__lte=end_date, status="active")
