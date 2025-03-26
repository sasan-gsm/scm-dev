from typing import Protocol, Optional, Dict, Any, List, TypeVar, Generic
from django.db.models import Model, QuerySet
from .models import TimeStampedModel

# Define a type variable for our models
T = TypeVar("T", bound=TimeStampedModel)


class RepositoryProtocol(Protocol):
    """
    Protocol defining the interface for repository classes.

    Any class that implements these methods will satisfy this protocol,
    without needing to explicitly inherit from it.
    """

    def get_by_id(self, id: int) -> Optional[Model]:
        """
        Retrieve an entity by its ID.

        Args:
            id: The entity ID

        Returns:
            The entity if found, None otherwise
        """
        ...

    def get_all(self) -> QuerySet:
        """
        Retrieve all entities.

        Returns:
            QuerySet of all entities
        """
        ...

    def create(self, data: Dict[str, Any]) -> Model:
        """
        Create a new entity.

        Args:
            data: The entity data

        Returns:
            The created entity
        """
        ...

    def update(self, entity: Model, data: Dict[str, Any]) -> Model:
        """
        Update an existing entity.

        Args:
            entity: The entity to update
            data: The updated data

        Returns:
            The updated entity
        """
        ...

    def delete(self, entity: Model) -> None:
        """
        Delete an entity.

        Args:
            entity: The entity to delete
        """
        ...


class BaseRepository(Generic[T]):
    """
    Base implementation of the repository pattern.

    This class provides default implementations for common operations
    and is generic over any TimeStampedModel subclass.
    """

    def __init__(self, model_class):
        """
        Initialize the repository with a model class.

        Args:
            model_class: The model class this repository works with
        """
        self.model_class = model_class

    def get_by_id(self, id: int) -> Optional[T]:
        """
        Retrieve an entity by its ID.

        Args:
            id: The entity ID

        Returns:
            The entity if found, None otherwise
        """
        try:
            return self.model_class.objects.get(id=id)
        except self.model_class.DoesNotExist:
            return None

    def get_all(self) -> QuerySet:
        """
        Retrieve all entities.

        Returns:
            QuerySet of all entities
        """
        return self.model_class.objects.all()

    def filter(self, **kwargs) -> QuerySet:
        """
        Filter entities by the given criteria.

        Args:
            **kwargs: Filter criteria

        Returns:
            QuerySet of filtered entities
        """
        return self.model_class.objects.filter(**kwargs)

    def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new entity.

        Args:
            data: The entity data

        Returns:
            The created entity
        """
        return self.model_class.objects.create(**data)

    def update(self, entity: T, data: Dict[str, Any]) -> T:
        """
        Update an existing entity.

        Args:
            entity: The entity to update
            data: The updated data

        Returns:
            The updated entity
        """
        for key, value in data.items():
            setattr(entity, key, value)
        entity.save()
        return entity

    def delete(self, entity: T) -> None:
        """
        Delete an entity.

        Args:
            entity: The entity to delete
        """
        entity.delete()

    def bulk_create(self, entities: List[T]) -> List[T]:
        """
        Create multiple entities in a single database query.

        Args:
            entities: List of entity instances to create

        Returns:
            List of created entities
        """
        return self.model_class.objects.bulk_create(entities)

    def bulk_update(self, entities: List[T], fields: List[str]) -> None:
        """
        Update multiple entities in a single database query.

        Args:
            entities: List of entity instances to update
            fields: List of field names to update
        """
        self.model_class.objects.bulk_update(entities, fields)
