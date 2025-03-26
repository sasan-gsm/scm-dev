from typing import Optional, List
from django.db.models import Q, QuerySet, Count, Avg
from django.utils import timezone

from core.common.repositories import BaseRepository
from .models import QualityCheck, QualityIssue, QualityParameter


class QualityCheckRepository(BaseRepository[QualityCheck]):
    """
    Repository for QualityCheck model operations.

    Provides data access operations specific to the QualityCheck model.
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
            return self.model_class.objects.get(number=number)
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

    def get_by_purchase_order(self, purchase_order_id: int) -> QuerySet:
        """
        Get quality checks for a specific purchase order.

        Args:
            purchase_order_id: The purchase order ID

        Returns:
            QuerySet of quality checks for the specified purchase order
        """
        return self.model_class.objects.filter(purchase_order_id=purchase_order_id)

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

    def get_failed_checks(self) -> QuerySet:
        """
        Get failed quality checks.

        Returns:
            QuerySet of failed quality checks
        """
        return self.model_class.objects.filter(status="failed")

    def get_checks_by_inspector(self, inspector_id: int) -> QuerySet:
        """
        Get quality checks performed by a specific inspector.

        Args:
            inspector_id: The inspector ID

        Returns:
            QuerySet of quality checks performed by the specified inspector
        """
        return self.model_class.objects.filter(inspector_id=inspector_id)


class QualityIssueRepository(BaseRepository[QualityIssue]):
    """
    Repository for QualityIssue model operations.

    Provides data access operations specific to the QualityIssue model.
    """

    def __init__(self):
        """
        Initialize the repository with the QualityIssue model.
        """
        super().__init__(QualityIssue)

    def get_by_check(self, check_id: int) -> QuerySet:
        """
        Get quality issues for a specific quality check.

        Args:
            check_id: The quality check ID

        Returns:
            QuerySet of quality issues for the specified quality check
        """
        return self.model_class.objects.filter(quality_check_id=check_id)

    def get_by_material(self, material_id: int) -> QuerySet:
        """
        Get quality issues for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of quality issues for the specified material
        """
        return self.model_class.objects.filter(quality_check__material_id=material_id)

    def get_by_supplier(self, supplier_id: int) -> QuerySet:
        """
        Get quality issues for a specific supplier.

        Args:
            supplier_id: The supplier ID

        Returns:
            QuerySet of quality issues for the specified supplier
        """
        return self.model_class.objects.filter(
            quality_check__purchase_order__supplier_id=supplier_id
        )

    def get_by_severity(self, severity: str) -> QuerySet:
        """
        Get quality issues with a specific severity.

        Args:
            severity: The severity level

        Returns:
            QuerySet of quality issues with the specified severity
        """
        return self.model_class.objects.filter(severity=severity)

    def get_by_status(self, status: str) -> QuerySet:
        """
        Get quality issues with a specific status.

        Args:
            status: The status

        Returns:
            QuerySet of quality issues with the specified status
        """
        return self.model_class.objects.filter(status=status)

    def get_open_issues(self) -> QuerySet:
        """
        Get open quality issues.

        Returns:
            QuerySet of open quality issues
        """
        return self.model_class.objects.filter(status__in=["open", "in_progress"])

    def get_issues_by_parameter(self, parameter_id: int) -> QuerySet:
        """
        Get quality issues for a specific quality parameter.

        Args:
            parameter_id: The quality parameter ID

        Returns:
            QuerySet of quality issues for the specified parameter
        """
        return self.model_class.objects.filter(parameter_id=parameter_id)

    def get_most_common_issues(self, limit: int = 10) -> QuerySet:
        """
        Get most common quality issues by parameter.

        Args:
            limit: Maximum number of issues to return

        Returns:
            QuerySet of most common quality issues
        """
        return (
            self.model_class.objects.values("parameter", "parameter__name")
            .annotate(issue_count=Count("id"))
            .order_by("-issue_count")[:limit]
        )


class QualityParameterRepository(BaseRepository[QualityParameter]):
    """
    Repository for QualityParameter model operations.

    Provides data access operations specific to the QualityParameter model.
    """

    def __init__(self):
        """
        Initialize the repository with the QualityParameter model.
        """
        super().__init__(QualityParameter)

    def get_by_name(self, name: str) -> Optional[QualityParameter]:
        """
        Retrieve a quality parameter by its name.

        Args:
            name: The parameter name

        Returns:
            The quality parameter if found, None otherwise
        """
        try:
            return self.model_class.objects.get(name=name)
        except self.model_class.DoesNotExist:
            return None

    def get_by_material_type(self, material_type: str) -> QuerySet:
        """
        Get quality parameters for a specific material type.

        Args:
            material_type: The material type

        Returns:
            QuerySet of quality parameters for the specified material type
        """
        return self.model_class.objects.filter(material_type=material_type)

    def get_active_parameters(self) -> QuerySet:
        """
        Get active quality parameters.

        Returns:
            QuerySet of active quality parameters
        """
        return self.model_class.objects.filter(is_active=True)

    def get_parameters_with_issues(self) -> QuerySet:
        """
        Get quality parameters that have associated issues.

        Returns:
            QuerySet of quality parameters with issues
        """
        return self.model_class.objects.annotate(
            issue_count=Count("qualityissue")
        ).filter(issue_count__gt=0)
