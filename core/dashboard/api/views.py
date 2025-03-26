from rest_framework import views, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from core.dashboard.services import DashboardService
from .serializers import (
    DashboardSerializer,
    ProjectStatSerializer,
    InventoryStatSerializer,
    RequestStatSerializer,
    ProcurementStatSerializer,
)


class UserDashboardView(views.APIView):
    """
    API endpoint for user dashboard data.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get dashboard data for the authenticated user.
        """
        service = DashboardService()
        dashboard_data = service.get_user_dashboard(request.user.id)
        serializer = DashboardSerializer(dashboard_data)
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def project_stats(request):
    """
    Get project statistics for the authenticated user.
    """
    service = DashboardService()
    stats = service.get_user_projects(request.user.id)
    serializer = ProjectStatSerializer(stats)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def inventory_stats(request):
    """
    Get inventory statistics.
    """
    service = DashboardService()
    stats = service.get_inventory_stats()
    serializer = InventoryStatSerializer(stats)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def request_stats(request):
    """
    Get request statistics for the authenticated user.
    """
    service = DashboardService()
    stats = service.get_request_stats(request.user.id)
    serializer = RequestStatSerializer(stats)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def procurement_stats(request):
    """
    Get procurement statistics.
    """
    service = DashboardService()
    stats = service.get_procurement_stats()
    serializer = ProcurementStatSerializer(stats)
    return Response(serializer.data)


# Create your views here.
