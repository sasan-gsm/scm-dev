from typing import Optional, List
from django.db.models import Q, QuerySet, Count, F

from core.common.repositories import BaseRepository
from .models import Material, MaterialCategory, MaterialPriceHistory


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
            inventory_items__quantity__lt=F("inventory_items__min_quantity"),
            inventory_items__monitor_stock_level=True,
        ).distinct()

    def get_materials_with_price_history(self) -> QuerySet:
        """
        Get materials with their price history.

        Returns:
            QuerySet of materials with annotated price history
        """
        return self.model_class.objects.prefetch_related("price_history")


class MaterialCategoryRepository(BaseRepository[MaterialCategory]):
    """
    Repository for MaterialCategory model operations.

    Provides data access operations specific to the MaterialCategory model.
    """

    def __init__(self):
        """
        Initialize the repository with the MaterialCategory model.
        """
        super().__init__(MaterialCategory)

    def get_by_name(self, name: str) -> Optional[MaterialCategory]:
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

    def get_root_categories(self) -> QuerySet:
        """
        Get root categories (categories without parents).

        Returns:
            QuerySet of root categories
        """
        return self.model_class.objects.filter(parent__isnull=True)

    def get_subcategories(self, parent_id: int) -> QuerySet:
        """
        Get subcategories of a specific category.

        Args:
            parent_id: The parent category ID

        Returns:
            QuerySet of subcategories
        """
        return self.model_class.objects.filter(parent_id=parent_id)


class MaterialPriceHistoryRepository(BaseRepository[MaterialPriceHistory]):
    """
    Repository for MaterialPriceHistory model operations.

    Provides data access operations specific to the MaterialPriceHistory model.
    """

    def __init__(self):
        """
        Initialize the repository with the MaterialPriceHistory model.
        """
        super().__init__(MaterialPriceHistory)

    def get_by_material(self, material_id: int) -> QuerySet:
        """
        Get price history for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of price history records for the specified material
        """
        return self.model_class.objects.filter(material_id=material_id)

    def get_latest_price(self, material_id: int) -> Optional[MaterialPriceHistory]:
        """
        Get the latest price for a specific material.

        Args:
            material_id: The material ID

        Returns:
            The latest price history record for the specified material, or None if not found
        """
        try:
            return self.model_class.objects.filter(material_id=material_id).latest(
                "effective_date"
            )
        except self.model_class.DoesNotExist:
            return None

    def get_by_date_range(self, material_id: int, start_date, end_date) -> QuerySet:
        """
        Get price history for a specific material within a date range.

        Args:
            material_id: The material ID
            start_date: The start date
            end_date: The end date

        Returns:
            QuerySet of price history records within the specified date range
        """
        return self.model_class.objects.filter(
            material_id=material_id,
            effective_date__gte=start_date,
            effective_date__lte=end_date,
        )
