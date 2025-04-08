from typing import Optional, Dict, Any
from django.db.models import QuerySet
from django.db import transaction
from core.common.services import BaseService
from .repositories import (
    QualityStandardRepository,
    QualityCheckRepository,
    QualityCheckItemRepository,
)
from .models import QualityStandard, QualityCheck, QualityCheckItem


class QualityStandardService(BaseService[QualityStandard]):
    """
    Service for QualityStandard business logic.
    """

    def __init__(self):
        """
        Initialize the service with a QualityStandardRepository.
        """
        super().__init__(QualityStandardRepository())

    def get_by_code(self, code: str) -> Optional[QualityStandard]:
        """
        Get a quality standard by its code.

        Args:
            code: The quality standard code

        Returns:
            The quality standard if found, None otherwise
        """
        return self.repository.get_by_code(code)

    def get_active_standards(self) -> QuerySet:
        """
        Get active quality standards.

        Returns:
            QuerySet of active quality standards
        """
        return self.repository.get_active_standards()


class QualityCheckService(BaseService[QualityCheck]):
    """
    Service for QualityCheck business logic.
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

    def get_by_project(self, project_id: int) -> QuerySet:
        """
        Get quality checks for a specific project.

        Args:
            project_id: The project ID

        Returns:
            QuerySet of quality checks for the specified project
        """
        return self.repository.get_by_project(project_id)

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

    def get_submitted_checks(self) -> QuerySet:
        """
        Get submitted quality checks that are pending approval.

        Returns:
            QuerySet of quality checks with submitted status
        """
        return self.repository.get_submitted_checks()

    def get_by_inspector(self, inspector_id: int) -> QuerySet:
        """
        Get quality checks performed by a specific inspector.

        Args:
            inspector_id: The inspector ID

        Returns:
            QuerySet of quality checks performed by the specified inspector
        """
        return self.repository.get_by_inspector(inspector_id)

    def get_by_batch_number(self, batch_number: str) -> QuerySet:
        """
        Get quality checks with a specific batch number.

        Args:
            batch_number: The batch number

        Returns:
            QuerySet of quality checks with the specified batch number
        """
        return self.repository.get_by_batch_number(batch_number)

    def create(self, data: Dict[str, Any]) -> QualityCheck:
        """
        Create a new quality check with items.

        Args:
            data: The quality check data

        Returns:
            The created quality check
        """
        items_data = data.pop("items", [])

        # Generate a unique check number
        from django.utils import timezone

        prefix = "QC"
        date_str = timezone.now().strftime("%Y%m%d")

        # Get the latest check number with the same prefix and date
        latest_check = (
            QualityCheck.objects.filter(check_number__startswith=f"{prefix}-{date_str}")
            .order_by("-check_number")
            .first()
        )

        if latest_check:
            # Extract the sequence number and increment it
            try:
                seq_num = int(latest_check.check_number.split("-")[-1])
                next_seq_num = seq_num + 1
            except (ValueError, IndexError):
                next_seq_num = 1
        else:
            next_seq_num = 1

        # Create the new check number
        check_number = f"{prefix}-{date_str}-{next_seq_num:04d}"

        # Set the check number and status
        data["check_number"] = check_number
        data["status"] = "draft"

        with transaction.atomic():
            # Create the quality check
            quality_check = self.repository.create(data)

            # Create the quality check items
            item_service = QualityCheckItemService()
            for item_data in items_data:
                item_data["quality_check"] = quality_check
                item_service.create(item_data)

            return quality_check

    def submit_quality_check(self, quality_check_id: int) -> Optional[QualityCheck]:
        """
        Submit a quality check for approval.

        Args:
            quality_check_id: The quality check ID

        Returns:
            The updated quality check if found, None otherwise
        """
        quality_check = self.get_by_id(quality_check_id)
        if not quality_check:
            return None

        if quality_check.status != "draft":
            raise ValueError(
                f"Cannot submit quality check with status: {quality_check.status}"
            )

        return self.update(quality_check_id, {"status": "submitted"})

    def approve_quality_check(self, quality_check_id: int) -> Optional[QualityCheck]:
        """
        Approve a quality check.

        Args:
            quality_check_id: The quality check ID

        Returns:
            The approved quality check if found, None otherwise
        """
        quality_check = self.get_by_id(quality_check_id)
        if not quality_check:
            return None

        if quality_check.status != "submitted":
            raise ValueError(
                f"Cannot approve quality check with status: {quality_check.status}"
            )

        return self.update(quality_check_id, {"status": "approved"})

    def reject_quality_check(self, quality_check_id: int) -> Optional[QualityCheck]:
        """
        Reject a quality check.

        Args:
            quality_check_id: The quality check ID

        Returns:
            The rejected quality check if found, None otherwise
        """
        quality_check = self.get_by_id(quality_check_id)
        if not quality_check:
            return None

        if quality_check.status != "submitted":
            raise ValueError(
                f"Cannot reject quality check with status: {quality_check.status}"
            )

        return self.update(quality_check_id, {"status": "rejected"})

    def complete_quality_check(self, quality_check_id: int) -> Optional[QualityCheck]:
        """
        Complete a quality check.

        Args:
            quality_check_id: The quality check ID

        Returns:
            The completed quality check if found, None otherwise
        """
        quality_check = self.get_by_id(quality_check_id)
        if not quality_check:
            return None

        if quality_check.status != "approved":
            raise ValueError(
                f"Cannot complete quality check with status: {quality_check.status}"
            )

        return self.update(quality_check_id, {"status": "completed"})

    def cancel_quality_check(self, quality_check_id: int) -> Optional[QualityCheck]:
        """
        Cancel a quality check.

        Args:
            quality_check_id: The quality check ID

        Returns:
            The cancelled quality check if found, None otherwise
        """
        quality_check = self.get_by_id(quality_check_id)
        if not quality_check:
            return None

        if quality_check.status in ["completed", "cancelled"]:
            raise ValueError(
                f"Cannot cancel quality check with status: {quality_check.status}"
            )

        return self.update(quality_check_id, {"status": "cancelled"})


class QualityCheckItemService(BaseService[QualityCheckItem]):
    """
    Service for QualityCheckItem business logic.
    """

    def __init__(self):
        """
        Initialize the service with a QualityCheckItemRepository.
        """
        super().__init__(QualityCheckItemRepository())

    def get_by_quality_check(self, quality_check_id: int) -> QuerySet:
        """
        Get items for a specific quality check.

        Args:
            quality_check_id: The quality check ID

        Returns:
            QuerySet of items for the specified quality check
        """
        return self.repository.get_by_quality_check(quality_check_id)

    def get_by_standard(self, standard_id: int) -> QuerySet:
        """
        Get quality check items for a specific standard.

        Args:
            standard_id: The standard ID

        Returns:
            QuerySet of quality check items for the specified standard
        """
        return self.repository.get_by_standard(standard_id)

    def get_passed_items(self) -> QuerySet:
        """
        Get passed quality check items.

        Returns:
            QuerySet of passed quality check items
        """
        return self.repository.get_passed_items()

    def get_failed_items(self) -> QuerySet:
        """
        Get failed quality check items.

        Returns:
            QuerySet of failed quality check items
        """
        return self.repository.get_failed_items()

    def update_result(
        self, item_id: int, result: str, is_passed: bool
    ) -> Optional[QualityCheckItem]:
        """
        Update the result of a quality check item.

        Args:
            item_id: The quality check item ID
            result: The result
            is_passed: Whether the item passed the check

        Returns:
            The updated quality check item if found, None otherwise
        """
        item = self.get_by_id(item_id)
        if not item:
            return None

        return self.update(item_id, {"result": result, "is_passed": is_passed})
