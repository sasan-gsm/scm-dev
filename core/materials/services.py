from typing import Optional, List, Dict, Any, Union
from django.db.models import QuerySet
from django.utils import timezone
from decimal import Decimal

from core.common.services import BaseService
from .repositories import (
    MaterialRepository,
    MaterialCategoryRepository,
    MaterialPriceHistoryRepository,
)
from .models import Material, MaterialCategory, MaterialPriceHistory


class MaterialService(BaseService[Material]):
    """
    Service for Material business logic.

    This class provides business logic operations for the Material model.
    """

    def __init__(self):
        """
        Initialize the service with a MaterialRepository.
        """
        super().__init__(MaterialRepository())

    def get_by_code(self, code: str) -> Optional[Material]:
        """
        Get a material by its code.

        Args:
            code: The material code

        Returns:
            The material if found, None otherwise
        """
        return self.repository.get_by_code(code)

    def get_by_category(self, category_id: int) -> QuerySet:
        """
        Get materials by category.

        Args:
            category_id: The category ID

        Returns:
            QuerySet of materials in the specified category
        """
        return self.repository.get_by_category(category_id)

    def search_materials(self, query: str) -> QuerySet:
        """
        Search for materials by name, code, or description.

        Args:
            query: The search query

        Returns:
            QuerySet of matching materials
        """
        return self.repository.search(query)

    def get_low_inventory_materials(self) -> QuerySet:
        """
        Get materials with inventory below minimum level.

        Returns:
            QuerySet of materials with low inventory
        """
        return self.repository.get_low_inventory_materials()

    def update_price(
        self,
        material_id: int,
        price: Decimal,
        effective_date=None,
        user_id: int = None,
        notes: str = "",
    ) -> Optional[Material]:
        """
        Update the price of a material and record the price history.

        Args:
            material_id: The material ID
            price: The new price
            effective_date: The effective date of the price change
            user_id: The ID of the user making the change
            notes: Optional notes about the price change

        Returns:
            The updated material if found, None otherwise
        """
        # Get the material
        material = self.get_by_id(material_id)
        if not material:
            return None

        # Set effective date to today if not provided
        if not effective_date:
            effective_date = timezone.now().date()

        # Update the material's current price
        material.unit_price = price
        material.save()

        # Create price history record using the price history service
        price_history_service = MaterialPriceHistoryService()
        price_history_service.create(
            {
                "material": material,
                "price": price,
                "effective_date": effective_date,
                "recorded_by_id": user_id,
                "notes": notes,
            }
        )

        return material

    def get_materials_with_price_history(self) -> QuerySet:
        """
        Get materials with their price history.

        Returns:
            QuerySet of materials with prefetched price history
        """
        return self.repository.get_materials_with_price_history()


class MaterialCategoryService(BaseService[MaterialCategory]):
    """
    Service for MaterialCategory business logic.

    This class provides business logic operations for the MaterialCategory model.
    """

    def __init__(self):
        """
        Initialize the service with a MaterialCategoryRepository.
        """
        super().__init__(MaterialCategoryRepository())

    def get_by_name(self, name: str) -> Optional[MaterialCategory]:
        """
        Get a category by its name.

        Args:
            name: The category name

        Returns:
            The category if found, None otherwise
        """
        return self.repository.get_by_name(name)

    def get_with_material_count(self) -> QuerySet:
        """
        Get categories with their material count.

        Returns:
            QuerySet of categories with annotated material count
        """
        return self.repository.get_with_material_count()

    def get_root_categories(self) -> QuerySet:
        """
        Get root categories (categories without parents).

        Returns:
            QuerySet of root categories
        """
        return self.repository.get_root_categories()

    def get_subcategories(self, parent_id: int) -> QuerySet:
        """
        Get subcategories of a specific category.

        Args:
            parent_id: The parent category ID

        Returns:
            QuerySet of subcategories
        """
        return self.repository.get_subcategories(parent_id)


class MaterialPriceHistoryService(BaseService[MaterialPriceHistory]):
    """
    Service for MaterialPriceHistory business logic.

    This class provides business logic operations for the MaterialPriceHistory model.
    """

    def __init__(self):
        """
        Initialize the service with a MaterialPriceHistoryRepository.
        """
        super().__init__(MaterialPriceHistoryRepository())

    def get_by_material(self, material_id: int) -> QuerySet:
        """
        Get price history for a specific material.

        Args:
            material_id: The material ID

        Returns:
            QuerySet of price history records for the specified material
        """
        return self.repository.get_by_material(material_id)

    def get_latest_price(self, material_id: int) -> Optional[MaterialPriceHistory]:
        """
        Get the latest price for a specific material.

        Args:
            material_id: The material ID

        Returns:
            The latest price history record for the specified material, or None if not found
        """
        return self.repository.get_latest_price(material_id)

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
        return self.repository.get_by_date_range(material_id, start_date, end_date)
