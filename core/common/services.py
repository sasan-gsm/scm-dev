from typing import TypeVar, Generic, Optional, List, Dict, Any
from django.db.models import Model, QuerySet

from .repositories import BaseRepository

T = TypeVar("T", bound=Model)


class BaseService(Generic[T]):
    """
    Base service class that provides common business logic operations.

    This class works with a repository to perform data access operations
    and adds business logic on top of that.
    """

    def __init__(self, repository: BaseRepository):
        """
        Initialize the service with a repository.

        Args:
            repository: The repository to use for data access
        """
        self.repository = repository

    def get_by_id(self, id: int) -> Optional[T]:
        """
        Get an entity by its ID.

        Returns:
            The entity if found, None otherwise
        """
        return self.repository.get_by_id(id)

    def get_all(self) -> QuerySet:
        """
        Get all entities.

        Returns:
            QuerySet of all entities
        """
        return self.repository.get_all()

    def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new entity.

        Args:
            data: The entity data

        Returns:
            The created entity
        """
        # Perform any business logic before creation
        self._validate_create(data)

        # Create the entity
        entity = self.repository.create(data)

        # Perform any business logic after creation
        self._after_create(entity)

        return entity

    def update(self, id: int, data: Dict[str, Any]) -> Optional[T]:
        """
        Update an existing entity.

        Args:
            id: The entity ID
            data: The updated data

        Returns:
            The updated entity if found, None otherwise
        """
        # Get the entity
        entity = self.get_by_id(id)
        if not entity:
            return None

        # Perform any business logic before update
        self._validate_update(entity, data)

        # Update the entity
        updated_entity = self.repository.update(entity, data)

        # Perform any business logic after update
        self._after_update(updated_entity)

        return updated_entity

    def delete(self, id: int) -> bool:
        """
        Delete an entity.

        Returns:
            True if the entity was deleted, False otherwise
        """
        # Get the entity
        entity = self.get_by_id(id)
        if not entity:
            return False

        # Perform any business logic before deletion
        self._validate_delete(entity)

        # Delete the entity
        self.repository.delete(entity)

        # Perform any business logic after deletion
        self._after_delete(entity)

        return True

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating an entity.

        Args:
            data: The entity data

        Raises:
            ValueError: If the data is invalid
        """
        pass

    def _validate_update(self, entity: T, data: Dict[str, Any]) -> None:
        """
        Validate data before updating an entity.

        Args:
            entity: The entity to update
            data: The updated data

        Raises:
            ValueError: If the data is invalid
        """
        pass

    def _validate_delete(self, entity: T) -> None:
        """
        Validate before deleting an entity.

        Args:
            entity: The entity to delete

        Raises:
            ValueError: If the entity cannot be deleted
        """
        pass

    def _after_create(self, entity: T) -> None:
        """
        Perform actions after creating an entity.

        Args:
            entity: The created entity
        """
        pass

    def _after_update(self, entity: T) -> None:
        """
        Perform actions after updating an entity.

        Args:
            entity: The updated entity
        """
        pass

    def _after_delete(self, entity: T) -> None:
        """
        Perform actions after deleting an entity.

        Args:
            entity: The deleted entity
        """
        pass

    def filter(self, **kwargs) -> QuerySet:
        """
        Filter entities by the given criteria.

        Args:
            **kwargs: Filter criteria

        Returns:
            QuerySet of filtered entities
        """
        return self.repository.filter(**kwargs)

    def bulk_create(self, entities: List[T]) -> List[T]:
        """
        Create multiple entities in a single database query.

        Args:
            entities: List of entity instances to create

        Returns:
            List of created entities
        """
        return self.repository.bulk_create(entities)

    def bulk_update(self, entities: List[T], fields: List[str]) -> None:
        """
        Update multiple entities in a single database query.

        Args:
            entities: List of entity instances to update
            fields: List of field names to update
        """
        self.repository.bulk_update(entities, fields)
