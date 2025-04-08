from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from core.projects.models import Project
from core.projects.services import ProjectService
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for projects.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "manager"]
    search_fields = ["name", "number", "description"]
    ordering_fields = ["name", "number", "start_date", "end_date", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Get the list of projects for this view."""
        service = ProjectService()
        return service.get_all()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return ProjectListSerializer
        elif self.action == "create":
            return ProjectCreateSerializer
        return ProjectDetailSerializer

    def create(self, request, *args, **kwargs):
        """Create a new project."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ProjectService()
        try:
            project = service.create(serializer.validated_data)
            return Response(
                ProjectDetailSerializer(project).data, status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update an existing project."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        service = ProjectService()
        try:
            project = service.update(instance.id, serializer.validated_data)
            if project:
                return Response(ProjectDetailSerializer(project).data)
            return Response(
                {"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Delete a project."""
        instance = self.get_object()
        service = ProjectService()

        try:
            service.delete(instance.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get active projects."""
        service = ProjectService()
        projects = service.get_active_projects()
        page = self.paginate_queryset(projects)

        if page is not None:
            serializer = ProjectListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def ending_soon(self, request):
        """Get projects ending soon."""
        days = request.query_params.get("days", 30)
        service = ProjectService()
        projects = service.get_projects_ending_soon(int(days))
        page = self.paginate_queryset(projects)

        if page is not None:
            serializer = ProjectListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_projects(self, request):
        """Get projects managed by the current user."""
        service = ProjectService()
        projects = service.get_projects_by_manager(request.user.id)
        page = self.paginate_queryset(projects)

        if page is not None:
            serializer = ProjectListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a project."""
        service = ProjectService()
        try:
            project = service.activate_project(pk)
            if project:
                return Response(ProjectDetailSerializer(project).data)
            return Response(
                {"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark a project as completed."""
        service = ProjectService()
        try:
            project = service.complete_project(pk)
            if project:
                return Response(ProjectDetailSerializer(project).data)
            return Response(
                {"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def put_on_hold(self, request, pk=None):
        """Put a project on hold."""
        service = ProjectService()
        try:
            project = service.put_on_hold_project(pk)
            if project:
                return Response(ProjectDetailSerializer(project).data)
            return Response(
                {"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a project."""
        service = ProjectService()
        try:
            project = service.cancel_project(pk)
            if project:
                return Response(ProjectDetailSerializer(project).data)
            return Response(
                {"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
