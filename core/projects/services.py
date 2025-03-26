from typing import Optional, Dict, Any, List
from django.db.models import QuerySet
from django.utils import timezone
from datetime import timedelta

from core.common.services import BaseService
from .repositories import ProjectRepository
from .models import Project


class ProjectService(BaseService[Project]):
    """
    Service for Project business logic.

    This class provides business logic operations for the Project model.
    """

    def __init__(self):
        """
        Initialize the service with a ProjectRepository.
        """
        super().__init__(ProjectRepository())

    def get_by_number(self, number: str) -> Optional[Project]:
        """
        Get a project by its number.

        Args:
            number: The project number

        Returns:
            The project if found, None otherwise
        """
        return self.repository.get_by_number(number)

    def get_active_projects(self) -> QuerySet:
        """
        Get all active projects.

        Returns:
            QuerySet of active projects
        """
        return self.repository.get_active_projects()

    def get_projects_by_manager(self, manager_id: int) -> QuerySet:
        """
        Get projects managed by a specific user.

        Args:
            manager_id: The manager ID

        Returns:
            QuerySet of projects managed by the specified user
        """
        return self.repository.get_projects_by_manager(manager_id)

    def search_projects(self, query: str) -> QuerySet:
        """
        Search for projects by name, number, or description.

        Args:
            query: The search query

        Returns:
            QuerySet of matching projects
        """
        return self.repository.search(query)

    def get_projects_ending_soon(self, days: int = 30) -> QuerySet:
        """
        Get projects that are ending within the specified number of days.

        Args:
            days: Number of days from now

        Returns:
            QuerySet of projects ending soon
        """
        return self.repository.get_projects_ending_soon(days)

    def activate_project(self, project_id: int) -> Optional[Project]:
        """
        Activate a project.

        Args:
            project_id: The project ID

        Returns:
            The activated project if found, None otherwise
        """
        return self.update(project_id, {"status": "active"})

    def complete_project(self, project_id: int) -> Optional[Project]:
        """
        Mark a project as completed.

        Args:
            project_id: The project ID

        Returns:
            The completed project if found, None otherwise
        """
        return self.update(project_id, {"status": "completed"})

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating a project.

        Args:
            data: The project data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        required_fields = ["name", "number", "start_date", "weight_factor", "manager"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Ensure start_date is not in the past
        if data["start_date"] < timezone.now().date():
            raise ValueError("Start date cannot be in the past")

        # Ensure end_date is after start_date if provided
        if (
            "end_date" in data
            and data["end_date"]
            and data["end_date"] < data["start_date"]
        ):
            raise ValueError("End date must be after start date")

    def _validate_update(self, entity: Project, data: Dict[str, Any]) -> None:
        """
        Validate data before updating a project.

        Args:
            entity: The project to update
            data: The updated data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure start_date is not changed for active projects
        if (
            "start_date" in data
            and entity.status == "active"
            and data["start_date"] != entity.start_date
        ):
            raise ValueError("Cannot change start date of an active project")

        # Ensure end_date is after start_date if provided
        start_date = data.get("start_date", entity.start_date)
        end_date = data.get("end_date", entity.end_date)
        if end_date and end_date < start_date:
            raise ValueError("End date must be after start date")

    def _validate_delete(self, entity: Project) -> None:
        """
        Validate before deleting a project.

        Args:
            entity: The project to delete

        Raises:
            ValueError: If the project cannot be deleted
        """
        # Prevent deletion of active projects
        if entity.status == "active":
            raise ValueError("Cannot delete an active project")
