from typing import Optional, Dict, Any, List
from django.db.models import QuerySet
from django.utils import timezone

from core.common.services import BaseService
from .repositories import MaterialRepository, CategoryRepository
from .models import Material, Category


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
        self, material_id: int, price: float, effective_date=None
    ) -> Optional[Material]:
        """
        Update the price of a material and record the price history.

        Args:
            material_id: The material ID
            price: The new price
            effective_date: The effective date of the price change

        Returns:
            The updated material if found, None otherwise
        """
        # Get the material
        material = self.get_by_id(material_id)
        if not material:
            return None

        # Set effective date to now if not provided
        if not effective_date:
            effective_date = timezone.now().date()

        # Update the material price
        updated_material = self.update(material_id, {"price": price})

        # Record the price history
        from core.accounting.models import PriceHistory

        PriceHistory.objects.create(
            material=material, price=price, effective_date=effective_date
        )

        return updated_material

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating a material.

        Args:
            data: The material data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        required_fields = ["name", "code", "category"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Ensure code is unique
        if self.repository.get_by_code(data["code"]):
            raise ValueError(f"Material with code {data['code']} already exists")

        # Ensure min_inventory_level is not negative
        if "min_inventory_level" in data and data["min_inventory_level"] < 0:
            raise ValueError("Minimum inventory level cannot be negative")

    def _validate_update(self, entity: Material, data: Dict[str, Any]) -> None:
        """
        Validate data before updating a material.

        Args:
            entity: The material to update
            data: The updated data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure code is unique if changed
        if "code" in data and data["code"] != entity.code:
            if self.repository.get_by_code(data["code"]):
                raise ValueError(f"Material with code {data['code']} already exists")

        # Ensure min_inventory_level is not negative
        if "min_inventory_level" in data and data["min_inventory_level"] < 0:
            raise ValueError("Minimum inventory level cannot be negative")


class CategoryService(BaseService[Category]):
    """
    Service for Category business logic.

    This class provides business logic operations for the Category model.
    """

    def __init__(self):
        """
        Initialize the service with a CategoryRepository.
        """
        super().__init__(CategoryRepository())

    def get_by_name(self, name: str) -> Optional[Category]:
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

    def _validate_create(self, data: Dict[str, Any]) -> None:
        """
        Validate data before creating a category.

        Args:
            data: The category data

        Raises:
            ValueError: If the data is invalid
        """
        # Ensure required fields are present
        if "name" not in data:
            raise ValueError("Missing required field: name")

        # Ensure name is unique
        if self.repository.get_by_name(data["name"]):
            raise ValueError(f"Category with name {data['name']} already exists")
