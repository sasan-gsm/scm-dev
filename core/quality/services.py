from typing import Optional, Dict, Any, List
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from core.common.services import BaseService
from .repositories import (
    QualityCheckRepository,
    QualityIssueRepository,
    QualityParameterRepository,
)
from .models import QualityCheck, QualityIssue, QualityParameter


class QualityCheckService(BaseService[QualityCheck]):
    """
    Service for QualityCheck business logic.

    This class provides business logic operations for the QualityCheck model.
    """

    def __init__(self):
        """
        Initialize the service with a QualityCheckRepository.
        """
        super().__init__(QualityCheckRepository())

    def get_by_number(self, number: str) -> Optional[QualityCheck]:
        """
        Get a quality check by its number.

        Args:
            number: The quality check number

        Returns:
            The quality check if found, None otherwise
        """
        return self.repository.get_by_number(number)

    def get_by_material(self, material_id: int) -> QuerySet:
        """
        Get quality checks for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of quality checks for the specified material
        """
        return self.repository.get_by_material(material_id)

    def get_by_purchase_order(self, purchase_order_id: int) -> QuerySet:
        """
        Get quality checks for a specific purchase order.

        Args:
            purchase_order_id: The purchase order ID

        Returns:
            QuerySet of quality checks for the specified purchase order
        """
        return self.repository.get_by_purchase_order(purchase_order_id)

    def get_by_status(self, status: str) -> QuerySet:
        """
        Get quality checks with a specific status.

        Args:
            status: The status

        Returns:
            QuerySet of quality checks with the specified status
        """
        return self.repository.get_by_status(status)

    def get_by_date_range(self, start_date, end_date) -> QuerySet:
        """
        Get quality checks created within a date range.

        Args:
            start_date: The start date
            end_date: The end date

        Returns:
            QuerySet of quality checks within the specified date range
        """
        return self.repository.get_by_date_range(start_date, end_date)

    def get_pending_checks(self) -> QuerySet:
        """
        Get pending quality checks.

        Returns:
            QuerySet of pending quality checks
        """
        return self.repository.get_pending_checks()

    def get_failed_checks(self) -> QuerySet:
        """
        Get failed quality checks.

        Returns:
            QuerySet of failed quality checks
        """
        return self.repository.get_failed_checks()

    def get_checks_by_inspector(self, inspector_id: int) -> QuerySet:
        """
        Get quality checks performed by a specific inspector.

        Args:
            inspector_id: The inspector ID

        Returns:
            QuerySet of quality checks performed by the specified inspector
        """
        return self.repository.get_checks_by_inspector(inspector_id)

    def approve_check(self, check_id: int, notes: str = None) -> Optional[QualityCheck]:
        """
        Approve a quality check.

        Args:
            check_id: The quality check ID
            notes: Optional notes about the approval

        Returns:
            The updated quality check if found, None otherwise

        Raises:
            ValueError: If the check cannot be approved
        """
        check = self.get_by_id(check_id)
        if not check:
            return None

        if check.status != "pending":
            raise ValueError(f"Cannot approve check with status '{check.status}'")

        data = {
            "status": "approved",
            "result_date": timezone.now(),
        }

        if notes:
            data["notes"] = notes

        return self.update(check_id, data)

    def reject_check(self, check_id: int, reason: str) -> Optional[QualityCheck]:
        """
        Reject a quality check.

        Args:
            check_id: The quality check ID
            reason: The reason for rejection

        Returns:
            The updated quality check if found, None otherwise

        Raises:
            ValueError: If the check cannot be rejected
        """
        check = self.get_by_id(check_id)
        if not check:
            return None

        if check.status != "pending":
            raise ValueError(f"Cannot reject check with status '{check.status}'")

        if not reason:
            raise ValueError("Rejection reason is required")

        return self.update(
            check_id,
            {"status": "failed", "result_date": timezone.now(), "notes": reason},
        )

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating a quality check.

        Args:
            data: The quality check data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        required_fields = ["material", "inspector"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Generate check number if not provided
        if "number" not in data:
            # Generate a unique check number (e.g., QC-YYYYMMDD-XXXX)
            today = timezone.now().strftime("%Y%m%d")
            last_check = (
                self.model_class.objects.filter(number__startswith=f"QC-{today}")
                .order_by("-number")
                .first()
            )

            if last_check:
                last_number = int(last_check.number.split("-")[-1])
                new_number = f"QC-{today}-{last_number + 1:04d}"
            else:
                new_number = f"QC-{today}-0001"

            data["number"] = new_number

        # Set initial status if not provided
        if "status" not in data:
            data["status"] = "pending"

        # Set check date if not provided
        if "check_date" not in data:
            data["check_date"] = timezone.now()


class QualityIssueService(BaseService[QualityIssue]):
    """
    Service for QualityIssue business logic.

    This class provides business logic operations for the QualityIssue model.
    """

    def __init__(self):
        """
        Initialize the service with a QualityIssueRepository.
        """
        super().__init__(QualityIssueRepository())

    def get_by_check(self, check_id: int) -> QuerySet:
        """
        Get quality issues for a specific quality check.

        Args:
            check_id: The quality check ID

        Returns:
            QuerySet of quality issues for the specified quality check
        """
        return self.repository.get_by_check(check_id)

    def get_by_material(self, material_id: int) -> QuerySet:
        """
        Get quality issues for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of quality issues for the specified material
        """
        return self.repository.get_by_material(material_id)

    def get_by_supplier(self, supplier_id: int) -> QuerySet:
        """
        Get quality issues for a specific supplier.

        Args:
            supplier_id: The supplier ID

        Returns:
            QuerySet of quality issues for the specified supplier
        """
        return self.repository.get_by_supplier(supplier_id)

    def get_by_severity(self, severity: str) -> QuerySet:
        """
        Get quality issues with a specific severity.

        Args:
            severity: The severity level

        Returns:
            QuerySet of quality issues with the specified severity
        """
        return self.repository.get_by_severity(severity)

    def get_by_status(self, status: str) -> QuerySet:
        """
        Get quality issues with a specific status.

        Args:
            status: The status

        Returns:
            QuerySet of quality issues with the specified status
        """
        return self.repository.get_by_status(status)

    def get_open_issues(self) -> QuerySet:
        """
        Get open quality issues.

        Returns:
            QuerySet of open quality issues
        """
        return self.repository.get_open_issues()

    def get_issues_by_parameter(self, parameter_id: int) -> QuerySet:
        """
        Get quality issues for a specific quality parameter.

        Args:
            parameter_id: The quality parameter ID

        Returns:
            QuerySet of quality issues for the specified parameter
        """
        return self.repository.get_issues_by_parameter(parameter_id)

    def get_most_common_issues(self, limit: int = 10) -> QuerySet:
        """
        Get most common quality issues by parameter.

        Args:
            limit: Maximum number of issues to return

        Returns:
            QuerySet of most common quality issues
        """
        return self.repository.get_most_common_issues(limit)

    def resolve_issue(self, issue_id: int, resolution: str) -> Optional[QualityIssue]:
        """
        Resolve a quality issue.

        Args:
            issue_id: The quality issue ID
            resolution: The resolution description

        Returns:
            The updated quality issue if found, None otherwise

        Raises:
            ValueError: If the issue cannot be resolved
        """
        issue = self.get_by_id(issue_id)
        if not issue:
            return None

        if issue.status == "resolved":
            raise ValueError("Issue is already resolved")

        if not resolution:
            raise ValueError("Resolution description is required")

        return self.update(
            issue_id,
            {
                "status": "resolved",
                "resolution": resolution,
                "resolved_date": timezone.now(),
            },
        )

    def escalate_issue(self, issue_id: int, reason: str) -> Optional[QualityIssue]:
        """
        Escalate a quality issue.

        Args:
            issue_id: The quality issue ID
            reason: The reason for escalation

        Returns:
            The updated quality issue if found, None otherwise

        Raises:
            ValueError: If the issue cannot be escalated
        """
        issue = self.get_by_id(issue_id)
        if not issue:
            return None

        if issue.status == "resolved":
            raise ValueError("Cannot escalate a resolved issue")

        if not reason:
            raise ValueError("Escalation reason is required")

        # Update severity based on current severity
        new_severity = "high"
        if issue.severity == "low":
            new_severity = "medium"
        elif issue.severity == "medium":
            new_severity = "high"
        elif issue.severity == "high":
            new_severity = "critical"

        return self.update(
            issue_id,
            {
                "severity": new_severity,
                "status": "in_progress",
                "notes": f"{issue.notes}\n\nEscalated: {reason}"
                if issue.notes
                else f"Escalated: {reason}",
            },
        )

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating a quality issue.

        Args:
            data: The quality issue data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        required_fields = ["quality_check", "parameter", "description"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Set default severity if not provided
        if "severity" not in data:
            data["severity"] = "medium"

        # Set default status if not provided
        if "status" not in data:
            data["status"] = "open"

        # Set created date if not provided
        if "created_date" not in data:
            data["created_date"] = timezone.now()

        # Update the quality check status to failed if it's not already
        quality_check = data["quality_check"]
        if quality_check.status != "failed":
            quality_check.status = "failed"
            quality_check.save()


class QualityParameterService(BaseService[QualityParameter]):
    """
    Service for QualityParameter business logic.

    This class provides business logic operations for the QualityParameter model.
    """

    def __init__(self):
        """
        Initialize the service with a QualityParameterRepository.
        """
        super().__init__(QualityParameterRepository())
        self.model_class = QualityParameter

    def get_by_name(self, name: str) -> Optional[QualityParameter]:
        """
        Get a quality parameter by its name.

        Args:
            name: The parameter name

        Returns:
            The quality parameter if found, None otherwise
        """
        return self.repository.get_by_name(name)

    def get_by_material_type(self, material_type: str) -> QuerySet:
        """
        Get quality parameters for a specific material type.

        Args:
            material_type: The material type

        Returns:
            QuerySet of quality parameters for the specified material type
        """
        return self.repository.get_by_material_type(material_type)

    def get_active_parameters(self) -> QuerySet:
        """
        Get active quality parameters.

        Returns:
            QuerySet of active quality parameters
        """
        return self.repository.get_active_parameters()

    def get_parameters_with_issues(self) -> QuerySet:
        """
        Get quality parameters that have associated issues.

        Returns:
            QuerySet of quality parameters with issues
        """
        return self.repository.get_parameters_with_issues()

    def deactivate(self, parameter_id: int) -> Optional[QualityParameter]:
        """
        Deactivate a quality parameter.

        Args:
            parameter_id: The parameter ID

        Returns:
            The updated parameter if found, None otherwise
        """
        return self.update(parameter_id, {"is_active": False})

    def activate(self, parameter_id: int) -> Optional[QualityParameter]:
        """
        Activate a quality parameter.

        Args:
            parameter_id: The parameter ID

        Returns:
            The updated parameter if found, None otherwise
        """
        return self.update(parameter_id, {"is_active": True})

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating a quality parameter.

        Args:
            data: The quality parameter data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        required_fields = ["name", "material_type"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Check if parameter with same name already exists
        if self.get_by_name(data["name"]):
            raise ValueError(f"Parameter with name '{data['name']}' already exists")

        # Set is_active to True if not provided
        if "is_active" not in data:
            data["is_active"] = True
