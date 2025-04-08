from rest_framework import serializers
from django.contrib.auth import get_user_model

from core.projects.models import Project

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model, used for nested representation in Project serializer.
    """

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]
        read_only_fields = fields
        ref_name = "ProjectUserSerializer"


class ProjectListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Projects with minimal information.
    """

    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "number",
            "start_date",
            "end_date",
            "status",
            "manager_id",
            "manager_name",
            "weight_factor",
        ]

    def get_manager_name(self, obj):
        """Get the full name of the project manager."""
        if obj.manager:
            return (
                f"{obj.manager.first_name} {obj.manager.last_name}".strip()
                or obj.manager.username
            )
        return None


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Project information.
    """

    manager = UserSerializer(read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="manager",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "number",
            "description",
            "start_date",
            "end_date",
            "status",
            "manager",
            "manager_id",
            "weight_factor",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        """
        Validate that end_date is after start_date.
        """
        if "start_date" in data and "end_date" in data:
            if data["start_date"] > data["end_date"]:
                raise serializers.ValidationError(
                    {"end_date": "End date must be after start date."}
                )
        return data


class ProjectCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Project.
    """

    class Meta:
        model = Project
        fields = [
            "name",
            "number",
            "description",
            "start_date",
            "end_date",
            "status",
            "manager",
            "weight_factor",
        ]

    def validate(self, data):
        """
        Validate that end_date is after start_date.
        """
        if "start_date" in data and "end_date" in data:
            if data["start_date"] > data["end_date"]:
                raise serializers.ValidationError(
                    {"end_date": "End date must be after start date."}
                )

        # Check if project number is unique
        number = data.get("number")
        if number and Project.objects.filter(number=number).exists():
            raise serializers.ValidationError(
                {"number": "A project with this number already exists."}
            )

        return data
