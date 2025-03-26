from .models import User, Permission
from django.contrib.auth.backends import ModelBackend
import re


class EmailPhoneUsernameAuthenticationBackend(ModelBackend):
    """
    Authentication backend that allows login with username, email, or phone number.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        # Determine the type of identifier
        if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", username):
            # Email pattern
            lookup_field = "email"
        elif re.match(r"^\+?[0-9]{10,15}$", username):
            # Phone number pattern (adjust regex as needed for your format)
            lookup_field = "phone_number"
        else:
            # Default to username
            lookup_field = "username"

        try:
            # Use the determined field for a single, targeted query
            lookup_kwargs = {lookup_field: username}
            user = User.objects.get(**lookup_kwargs)

            # Check the password
            if user.check_password(password):
                return user

        except User.DoesNotExist:
            # Run the default password hasher to mitigate timing attacks
            User().set_password(password)
            return None

        return None


class CustomPermissionBackend(ModelBackend):
    """
    Permission backend that checks department-based and custom permissions.
    """

    def has_perm(self, user_obj, perm, obj=None):
        # First check if the user has Django's built-in permission
        if super().has_perm(user_obj, perm, obj):
            return True
        # Then check our custom permission system
        try:
            # Check if the user has this custom permission through their department
            if user_obj.department:
                department_perms = Permission.objects.filter(
                    department=user_obj.department, is_basic=True, codename=perm
                )
                if department_perms.exists():
                    return True
            # Check user's custom permissions
            custom_perms = user_obj.custom_permissions.filter(codename=perm)
            return custom_perms.exists()

        except Exception:
            return False
