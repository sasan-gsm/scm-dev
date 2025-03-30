from typing import Optional
from django.db.models import Q, QuerySet
from django.contrib.auth import get_user_model
from core.common.repositories import BaseRepository
from .models import UserProfile, Role, Permission

User = get_user_model()


class UserRepository(BaseRepository[User]):
    """
    Repository for User model operations.

    Provides data access operations specific to the User model.
    """

    def __init__(self):
        """
        Initialize the repository with the User model.
        """
        super().__init__(User)

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by username.

        Args:
            username: The username

        Returns:
            The user if found, None otherwise
        """
        try:
            return self.model_class.objects.get(username=username)
        except self.model_class.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email.

        Args:
            email: The email address

        Returns:
            The user if found, None otherwise
        """
        try:
            return self.model_class.objects.get(email=email)
        except self.model_class.DoesNotExist:
            return None

    def get_active_users(self) -> QuerySet:
        """
        Get active users.

        Returns:
            QuerySet of active users
        """
        return self.model_class.objects.filter(is_active=True)

    def get_staff_users(self) -> QuerySet:
        """
        Get staff users.

        Returns:
            QuerySet of staff users
        """
        return self.model_class.objects.filter(is_staff=True)

    def search(self, query: str) -> QuerySet:
        """
        Search for users by username, first name, last name, or email.

        Args:
            query: The search query

        Returns:
            QuerySet of matching users
        """
        return self.model_class.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )


class UserProfileRepository(BaseRepository[UserProfile]):
    """
    Repository for UserProfile model operations.

    Provides data access operations specific to the UserProfile model.
    """

    def __init__(self):
        """
        Initialize the repository with the UserProfile model.
        """
        super().__init__(UserProfile)

    def get_by_user(self, user_id: int) -> Optional[UserProfile]:
        """
        Retrieve a user profile by user ID.

        Args:
            user_id: The user ID

        Returns:
            The user profile if found, None otherwise
        """
        try:
            return self.model_class.objects.get(user_id=user_id)
        except self.model_class.DoesNotExist:
            return None

    def get_by_department(self, department: str) -> QuerySet:
        """
        Get user profiles by department.

        Args:
            department: The department name

        Returns:
            QuerySet of user profiles in the specified department
        """
        return self.model_class.objects.filter(department=department)


class RoleRepository(BaseRepository[Role]):
    """
    Repository for Role model operations.

    Provides data access operations specific to the Role model.
    """

    def __init__(self):
        """
        Initialize the repository with the Role model.
        """
        super().__init__(Role)

    def get_by_name(self, name: str) -> Optional[Role]:
        """
        Retrieve a role by name.

        Args:
            name: The role name

        Returns:
            The role if found, None otherwise
        """
        try:
            return self.model_class.objects.get(name=name)
        except self.model_class.DoesNotExist:
            return None

    def get_by_user(self, user_id: int) -> QuerySet:
        """
        Get roles assigned to a specific user.

        Args:
            user_id: The user ID

        Returns:
            QuerySet of roles assigned to the specified user
        """
        return self.model_class.objects.filter(users__id=user_id)


class PermissionRepository(BaseRepository[Permission]):
    """
    Repository for Permission model operations.

    Provides data access operations specific to the Permission model.
    """

    def __init__(self):
        """
        Initialize the repository with the Permission model.
        """
        super().__init__(Permission)

    def get_by_codename(self, codename: str) -> Optional[Permission]:
        """
        Retrieve a permission by codename.

        Args:
            codename: The permission codename

        Returns:
            The permission if found, None otherwise
        """
        try:
            return self.model_class.objects.get(codename=codename)
        except self.model_class.DoesNotExist:
            return None

    def get_by_role(self, role_id: int) -> QuerySet:
        """
        Get permissions assigned to a specific role.

        Args:
            role_id: The role ID

        Returns:
            QuerySet of permissions assigned to the specified role
        """
        return self.model_class.objects.filter(roles__id=role_id)

    def get_by_user(self, user_id: int) -> QuerySet:
        """
        Get permissions assigned to a specific user through their roles.

        Args:
            user_id: The user ID

        Returns:
            QuerySet of permissions assigned to the specified user
        """
        return self.model_class.objects.filter(roles__users__id=user_id).distinct()
