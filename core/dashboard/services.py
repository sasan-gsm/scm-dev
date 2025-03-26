from typing import Dict, Any
from django.utils import timezone

from core.projects.services import ProjectService
from core.inventory.services import InventoryService
from core.request.services import RequestService
from core.procurement.services import PurchaseOrderService


class DashboardService:
    """
    Service for dashboard analytics.
    """

    def get_user_dashboard(self, user_id: int) -> Dict[str, Any]:
        """
        Get dashboard data for a specific user.

        Args:
            user_id: The user ID

        Returns:
            Dictionary with dashboard data
        """
        return {
            "projects": self.get_user_projects(user_id),
            "inventory": self.get_inventory_stats(),
            "requests": self.get_request_stats(user_id),
            "procurement": self.get_procurement_stats(),
        }

    def get_user_projects(self, user_id: int) -> Dict[str, Any]:
        """
        Get project statistics for a user.

        Args:
            user_id: The user ID

        Returns:
            Dictionary with project statistics
        """
        project_service = ProjectService()

        managed_projects = project_service.get_projects_by_manager(user_id)
        active_projects = managed_projects.filter(status="active")
        ending_soon = project_service.get_projects_ending_soon(30).filter(
            manager_id=user_id
        )

        return {
            "managed_count": managed_projects.count(),
            "active_count": active_projects.count(),
            "ending_soon_count": ending_soon.count(),
            "recent_projects": list(
                managed_projects.order_by("-created_at")[:5].values(
                    "id", "name", "number", "status"
                )
            ),
        }

    def get_inventory_stats(self) -> Dict[str, Any]:
        """
        Get inventory statistics.

        Returns:
            Dictionary with inventory statistics
        """
        inventory_service = InventoryService()

        low_inventory = inventory_service.get_low_inventory()

        return {
            "low_inventory_count": low_inventory.count(),
            "low_inventory_items": list(
                low_inventory[:5].values(
                    "id", "material__name", "quantity", "material__min_inventory_level"
                )
            ),
        }

    def get_request_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get request statistics for a user.

        Args:
            user_id: The user ID

        Returns:
            Dictionary with request statistics
        """
        request_service = RequestService()

        user_requests = request_service.get_by_requester(user_id)
        pending_approval = request_service.get_pending_approval()

        return {
            "my_requests_count": user_requests.count(),
            "pending_approval_count": pending_approval.count(),
            "recent_requests": list(
                user_requests.order_by("-created_at")[:5].values(
                    "id", "number", "status", "created_at"
                )
            ),
        }

    def get_procurement_stats(self) -> Dict[str, Any]:
        """
        Get procurement statistics.

        Returns:
            Dictionary with procurement statistics
        """
        purchase_order_service = PurchaseOrderService()

        orders_due_soon = purchase_order_service.get_orders_due_soon(7)

        return {
            "orders_due_soon_count": orders_due_soon.count(),
            "recent_orders": list(
                purchase_order_service.get_all()
                .order_by("-created_at")[:5]
                .values("id", "number", "status", "supplier__name")
            ),
        }
