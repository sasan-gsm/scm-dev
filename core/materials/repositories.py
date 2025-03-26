from typing import Optional, List
from django.db.models import Q, QuerySet, Count, F

from core.common.repositories import BaseRepository
from .models import Material, Category


class MaterialRepository(BaseRepository[Material]):
    """
    Repository for Material model operations.

    Provides data access operations specific to the Material model.
    """

    def __init__(self):
        """
        Initialize the repository with the Material model.
        """
        super().__init__(Material)

    def get_by_code(self, code: str) -> Optional[Material]:
        """
        Retrieve a material by its code.

        Args:
            code: The material code

        Returns:
            The material if found, None otherwise
        """
        try:
            return self.model_class.objects.get(code=code)
        except self.model_class.DoesNotExist:
            return None

    def get_by_category(self, category_id: int) -> QuerySet:
        """
        Retrieve materials by category.

        Args:
            category_id: The category ID

        Returns:
            QuerySet of materials in the specified category
        """
        return self.model_class.objects.filter(category_id=category_id)

    def search(self, query: str) -> QuerySet:
        """
        Search for materials by name, code, or description.

        Args:
            query: The search query

        Returns:
            QuerySet of matching materials
        """
        return self.model_class.objects.filter(
            Q(name__icontains=query)
            | Q(code__icontains=query)
            | Q(description__icontains=query)
        )

    def get_low_inventory_materials(self) -> QuerySet:
        """
        Get materials with inventory below minimum level.

        Returns:
            QuerySet of materials with low inventory
        """
        return self.model_class.objects.filter(
            inventory__quantity__lt=F("min_inventory_level"), alert_enabled=True
        ).distinct()

    def get_materials_with_price_history(self) -> QuerySet:
        """
        Get materials with their price history.

        Returns:
            QuerySet of materials with annotated price history
        """
        return self.model_class.objects.prefetch_related("price_history")


class CategoryRepository(BaseRepository[Category]):
    """
    Repository for Category model operations.

    Provides data access operations specific to the Category model.
    """

    def __init__(self):
        """
        Initialize the repository with the Category model.
        """
        super().__init__(Category)

    def get_by_name(self, name: str) -> Optional[Category]:
        """
        Retrieve a category by its name.

        Args:
            name: The category name

        Returns:
            The category if found, None otherwise
        """
        try:
            return self.model_class.objects.get(name=name)
        except self.model_class.DoesNotExist:
            return None

    def get_with_material_count(self) -> QuerySet:
        """
        Get categories with their material count.

        Returns:
            QuerySet of categories with annotated material count
        """
        return self.model_class.objects.annotate(material_count=Count("materials"))
