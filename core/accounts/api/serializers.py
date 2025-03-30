from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from core.accounts.models import Department, Permission

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "last_login",
            "custom_permissions",
            "department",
            "position",
            "is_manager",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new User.
    """

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "is_active",
            "custom_permissions",
            "department",
            "position",
            "is_manager",
        ]

    def validate(self, attrs):
        """
        Validate that the passwords match.
        """
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        """
        Create and return a new user.
        """
        # Remove password2 from validated data
        validated_data.pop("password2")
        # Extract custom_permissions if present
        custom_permissions = validated_data.pop("custom_permissions", [])

        # Create user instance with create_user to properly hash password
        user = User.objects.create_user(**validated_data)

        # Set custom permissions
        if custom_permissions:
            user.custom_permissions.set(custom_permissions)

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing User.
    """

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "is_active",
            "department",
            "position",
            "is_manager",
            "custom_permissions",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password.
    """

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        Validate that the new passwords match.
        """
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """
        Validate user credentials.
        """
        user = authenticate(username=attrs["username"], password=attrs["password"])

        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs["user"] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
            "department",
            "position",
            "is_manager",
        ]
        read_only_fields = ["id", "username", "date_joined", "last_login"]


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Department model.
    """

    class Meta:
        model = Department
        fields = ["id", "name", "code", "manager", "parent"]


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Permission model.
    """

    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "description", "is_basic", "department"]
