from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from core.request.models import Request, RequestItem
from core.projects.api.serializers import ProjectListSerializer

User = get_user_model()


class RequestItemSerializer(serializers.ModelSerializer):
    """
    Serializer for RequestItem model.
    """

    material_name = serializers.CharField(source="material.name", read_only=True)
    material_code = serializers.CharField(source="material.code", read_only=True)
    unit = serializers.CharField(source="material.unit", read_only=True)

    class Meta:
        model = RequestItem
        fields = [
            "id",
            "request",
            "material",
            "material_name",
            "material_code",
            "quantity",
            "quantity_fulfilled",
            "is_fulfilled",
            "unit",
            "notes",
            "status",
            "fulfillment_date",
        ]
        read_only_fields = [
            "id",
            "quantity_fulfilled",
            "is_fulfilled",
            "fulfillment_date",
        ]


class RequestListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Requests with minimal information.
    """

    requester_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(source="project.name", read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Request
        fields = [
            "id",
            "number",
            "requester_id",
            "requester_name",
            "project_id",
            "project_name",
            "request_date",
            "required_date",
            "status",
            "priority",
            "item_count",
        ]

    def get_requester_name(self, obj):
        """Get the full name of the requester."""
        if obj.requester:
            return (
                f"{obj.requester.first_name} {obj.requester.last_name}".strip()
                or obj.requester.username
            )
        return None


class RequestDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Request information.
    """

    requester = serializers.SerializerMethodField()
    project = ProjectListSerializer(read_only=True)
    items = RequestItemSerializer(many=True, read_only=True)

    class Meta:
        model = Request
        fields = [
            "id",
            "number",
            "requester",
            "project",
            "request_date",
            "required_date",
            "status",
            "approver",
            "priority",
            "notes",
            "fulfillment_date",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "number",
            "created_at",
            "updated_at",
            "fulfillment_date",
        ]

    def get_requester(self, obj):
        """Get information about the requester."""
        if obj.requester:
            return {
                "id": obj.requester.id,
                "username": obj.requester.username,
                "name": f"{obj.requester.first_name} {obj.requester.last_name}".strip()
                or obj.requester.username,
            }
        return None


class RequestItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating RequestItem objects.
    """

    class Meta:
        model = RequestItem
        fields = ["material", "quantity", "notes"]


class RequestCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Request with items.
    """

    items = RequestItemCreateSerializer(many=True, required=True)

    class Meta:
        model = Request
        fields = ["project", "required_date", "priority", "notes", "items"]

    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new request with request items.
        """
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        # Set the requester to the current user
        validated_data["requester"] = user
        validated_data["request_date"] = timezone.now().date()
        validated_data["status"] = "pending_approval"

        request = Request.objects.create(**validated_data)

        for item_data in items_data:
            RequestItem.objects.create(request=request, status="pending", **item_data)

        return request


class RequestUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing Request.
    """

    class Meta:
        model = Request
        fields = ["project", "required_date", "priority", "notes", "status"]

    def validate_status(self, value):
        """
        Validate status transitions.
        """
        request = self.instance
        user = self.context["request"].user

        # Define allowed status transitions
        allowed_transitions = {
            "draft": ["pending_approval", "cancelled"],
            "pending_approval": ["approved", "rejected", "cancelled"],
            "approved": ["in_progress", "cancelled"],
            "in_progress": ["completed", "cancelled"],
            "completed": [],  # No transitions allowed from completed
            "rejected": [],  # No transitions allowed from rejected
            "cancelled": [],  # No transitions allowed from cancelled
        }

        if value != request.status and value not in allowed_transitions.get(
            request.status, []
        ):
            raise serializers.ValidationError(
                f"Cannot change status from '{request.status}' to '{value}'."
            )

        # Check if user has permission to approve/reject
        if request.status == "pending_approval" and value in ["approved", "rejected"]:
            # Check if user is a manager or has approval permissions
            if not user.is_staff and not user.groups.filter(name="Approvers").exists():
                raise serializers.ValidationError(
                    "You don't have permission to approve or reject requests."
                )

        return value


class RequestItemUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing RequestItem.
    """

    class Meta:
        model = RequestItem
        fields = ["quantity", "notes", "status"]

    def validate_quantity(self, value):
        """
        Validate quantity changes.
        """
        item = self.instance

        # If item is already fulfilled, don't allow quantity changes
        if item.is_fulfilled:
            raise serializers.ValidationError(
                "Cannot change quantity of fulfilled items."
            )

        return value

    def validate_status(self, value):
        """
        Validate status transitions.
        """
        item = self.instance

        # Define allowed status transitions
        allowed_transitions = {
            "pending": ["fulfilled", "partially_fulfilled", "cancelled"],
            "partially_fulfilled": ["fulfilled", "cancelled"],
            "fulfilled": [],  # No transitions allowed from fulfilled
            "cancelled": [],  # No transitions allowed from cancelled
        }

        if value != item.status and value not in allowed_transitions.get(
            item.status, []
        ):
            raise serializers.ValidationError(
                f"Cannot change status from '{item.status}' to '{value}'."
            )

        return value
