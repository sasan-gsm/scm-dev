from typing import Optional, List
from django.db.models import QuerySet
from core.common.repositories import BaseRepository
from .models import QualityCheck, QualityCheckItem, QualityStandard


class QualityStandardRepository(BaseRepository[QualityStandard]):
    """
    Repository for QualityStandard model operations.
    """

    def __init__(self):
        """
        Initialize the repository with the QualityStandard model.
        """
        super().__init__(QualityStandard)

    def get_by_code(self, code: str) -> Optional[QualityStandard]:
        """
        Retrieve a quality standard by its code.

        Args:
            code: The quality standard code

        Returns:
            The quality standard if found, None otherwise
        """
        try:
            return self.model_class.objects.get(code=code)
        except self.model_class.DoesNotExist:
            return None

    def get_active_standards(self) -> QuerySet:
        """
        Get active quality standards.

        Returns:
            QuerySet of active quality standards
        """
        return self.model_class.objects.filter(is_active=True)


class QualityCheckRepository(BaseRepository[QualityCheck]):
    """
    Repository for QualityCheck model operations.
    """

    def __init__(self):
        """
        Initialize the repository with the QualityCheck model.
        """
        super().__init__(QualityCheck)

    def get_by_number(self, number: str) -> Optional[QualityCheck]:
        """
        Retrieve a quality check by its number.

        Args:
            number: The quality check number

        Returns:
            The quality check if found, None otherwise
        """
        try:
            return self.model_class.objects.get(check_number=number)
        except self.model_class.DoesNotExist:
            return None

    def get_by_material(self, material_id: int) -> QuerySet:
        """
        Get quality checks for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of quality checks for the specified material
        """
        return self.model_class.objects.filter(material_id=material_id)

    def get_by_project(self, project_id: int) -> QuerySet:
        """
        Get quality checks for a specific project.

        Args:
            project_id: The project ID

        Returns:
            QuerySet of quality checks for the specified project
        """
        return self.model_class.objects.filter(project_id=project_id)

    def get_by_status(self, status: str) -> QuerySet:
        """
        Get quality checks with a specific status.

        Args:
            status: The status

        Returns:
            QuerySet of quality checks with the specified status
        """
        return self.model_class.objects.filter(status=status)

    def get_by_date_range(self, start_date, end_date) -> QuerySet:
        """
        Get quality checks created within a date range.

        Args:
            start_date: The start date
            end_date: The end date

        Returns:
            QuerySet of quality checks within the specified date range
        """
        return self.model_class.objects.filter(
            check_date__gte=start_date, check_date__lte=end_date
        )

    def get_pending_checks(self) -> QuerySet:
        """
        Get pending quality checks.

        Returns:
            QuerySet of pending quality checks
        """
        return self.model_class.objects.filter(status="pending")

    def get_by_inspector(self, inspector_id: int) -> QuerySet:
        """
        Get quality checks performed by a specific inspector.

        Args:
            inspector_id: The inspector ID

        Returns:
            QuerySet of quality checks performed by the specified inspector
        """
        return self.model_class.objects.filter(inspector_id=inspector_id)


class QualityCheckItemRepository(BaseRepository[QualityCheckItem]):
    """
    Repository for QualityCheckItem model operations.
    """

    def __init__(self):
        """
        Initialize the repository with the QualityCheckItem model.
        """
        super().__init__(QualityCheckItem)

    def get_by_quality_check(self, quality_check_id: int) -> QuerySet:
        """
        Get items for a specific quality check.

        Args:
            quality_check_id: The quality check ID

        Returns:
            QuerySet of items for the specified quality check
        """
        return self.model_class.objects.filter(quality_check_id=quality_check_id)

    def get_by_standard(self, standard_id: int) -> QuerySet:
        """
        Get quality check items for a specific standard.

        Args:
            standard_id: The standard ID

        Returns:
            QuerySet of quality check items for the specified standard
        """
        return self.model_class.objects.filter(standard_id=standard_id)

    def get_passed_items(self) -> QuerySet:
        """
        Get passed quality check items.

        Returns:
            QuerySet of passed quality check items
        """
        return self.model_class.objects.filter(is_passed=True)

    def get_failed_items(self) -> QuerySet:
        """
        Get failed quality check items.

        Returns:
            QuerySet of failed quality check items
        """
        return self.model_class.objects.filter(is_passed=False)
