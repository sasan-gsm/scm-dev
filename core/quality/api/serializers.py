from rest_framework import serializers
from django.db import transaction

from core.quality.models import QualityCheck, QualityCheckItem, QualityStandard
from core.projects.api.serializers import ProjectListSerializer
from core.materials.api.serializers import MaterialListSerializer


class QualityStandardSerializer(serializers.ModelSerializer):
    """
    Serializer for QualityStandard model.
    """

    class Meta:
        model = QualityStandard
        fields = [
            "id",
            "name",
            "code",
            "description",
            "criteria",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class QualityCheckItemSerializer(serializers.ModelSerializer):
    """
    Serializer for QualityCheckItem model.
    """

    standard_name = serializers.CharField(source="standard.name", read_only=True)

    class Meta:
        model = QualityCheckItem
        fields = [
            "id",
            "quality_check",
            "standard",
            "standard_name",
            "result",
            "notes",
            "is_passed",
        ]
        read_only_fields = ["id"]


class QualityCheckItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating QualityCheckItem objects.
    """

    class Meta:
        model = QualityCheckItem
        fields = ["standard", "result", "notes", "is_passed"]


class QualityCheckListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing QualityChecks with minimal information.
    """

    project_name = serializers.CharField(source="project.name", read_only=True)
    material_name = serializers.CharField(source="material.name", read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    pass_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = QualityCheck
        fields = [
            "id",
            "check_number",
            "project_id",
            "project_name",
            "material_id",
            "material_name",
            "check_date",
            "status",
            "item_count",
            "pass_rate",
        ]


class QualityCheckDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed QualityCheck information.
    """

    project = ProjectListSerializer(read_only=True)
    material = MaterialListSerializer(read_only=True)
    items = QualityCheckItemSerializer(many=True, read_only=True)

    class Meta:
        model = QualityCheck
        fields = [
            "id",
            "check_number",
            "project",
            "material",
            "check_date",
            "inspector",
            "location",
            "batch_number",
            "status",
            "notes",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "check_number", "created_at", "updated_at"]


class QualityCheckCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new QualityCheck with items.
    """

    items = QualityCheckItemCreateSerializer(many=True, required=True)

    class Meta:
        model = QualityCheck
        fields = [
            "project",
            "material",
            "check_date",
            "inspector",
            "location",
            "batch_number",
            "notes",
            "items",
        ]

    # Note: The create method is not needed here as it's handled by the QualityCheckService
    # The service layer is responsible for creating the quality check and its items


class QualityCheckUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing QualityCheck.
    """

    class Meta:
        model = QualityCheck
        fields = [
            "project",
            "material",
            "check_date",
            "inspector",
            "location",
            "batch_number",
            "notes",
            "status",
        ]

    def validate_status(self, value):
        """
        Validate status transitions.
        """
        quality_check = self.instance

        # Define allowed status transitions
        allowed_transitions = {
            "draft": ["submitted", "cancelled"],
            "submitted": ["approved", "rejected", "cancelled"],
            "approved": ["completed", "cancelled"],
            "completed": [],  # No transitions allowed from completed
            "rejected": [],  # No transitions allowed from rejected
            "cancelled": [],  # No transitions allowed from cancelled
        }

        if value != quality_check.status and value not in allowed_transitions.get(
            quality_check.status, []
        ):
            raise serializers.ValidationError(
                f"Cannot change status from '{quality_check.status}' to '{value}'."
            )

        return value
