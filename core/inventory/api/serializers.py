from rest_framework import serializers
from django.db import transaction

from core.inventory.models import (
    InventoryItem,
    InventoryTransaction,
    Warehouse,
    InventoryLocation,
)
from core.materials.api.serializers import MaterialListSerializer
from core.projects.api.serializers import ProjectListSerializer


class WarehouseSerializer(serializers.ModelSerializer):
    """
    Serializer for Warehouse model.
    """

    class Meta:
        model = Warehouse
        fields = [
            "id",
            "name",
            "code",
            "location",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WarehouseDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Warehouse information.
    """

    inventory_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Warehouse
        fields = [
            "id",
            "name",
            "code",
            "location",
            "is_active",
            "inventory_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "inventory_count"]


class InventoryLocationSerializer(serializers.ModelSerializer):
    """
    Serializer for InventoryLocation model.
    """

    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = InventoryLocation
        fields = [
            "id",
            "name",
            "code",
            "warehouse",
            "warehouse_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InventoryLocationDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed InventoryLocation information.
    """

    warehouse = WarehouseSerializer(read_only=True)
    inventory_items_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = InventoryLocation
        fields = [
            "id",
            "name",
            "code",
            "warehouse",
            "inventory_items_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "inventory_items_count"]


class InventoryItemListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing InventoryItem objects with minimal information.
    """

    material_name = serializers.CharField(source="material.name", read_only=True)
    material_code = serializers.CharField(source="material.code", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)
    unit = serializers.CharField(source="material.unit", read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "material",
            "material_name",
            "material_code",
            "warehouse",
            "warehouse_name",
            "location",
            "location_name",
            "quantity",
            "min_quantity",
            "unit",
            "monitor_stock_level",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class InventoryItemDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed InventoryItem information.
    """

    material = MaterialListSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)
    location = InventoryLocationSerializer(read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "material",
            "warehouse",
            "location",
            "quantity",
            "min_quantity",
            "monitor_stock_level",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InventoryItemDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed InventoryItem information.
    """

    material = MaterialListSerializer(read_only=True)
    warehouse = WarehouseSerializer(read_only=True)
    location = InventoryLocationSerializer(read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "material",
            "warehouse",
            "location",
            "quantity",
            "min_quantity",
            "monitor_stock_level",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InventoryItemCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating InventoryItem objects.
    """

    class Meta:
        model = InventoryItem
        fields = [
            "material",
            "warehouse",
            "location",
            "quantity",
            "min_quantity",
            "monitor_stock_level",
        ]

    def validate(self, data):
        """
        Validate inventory item data.
        """
        # Ensure location belongs to the selected warehouse if provided
        warehouse = data.get("warehouse")
        location = data.get("location")

        if warehouse and location and location.warehouse_id != warehouse.id:
            raise serializers.ValidationError(
                {"location": "Location must belong to the selected warehouse."}
            )

        return data


class InventoryTransactionListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing InventoryTransaction objects with minimal information.
    """

    material_name = serializers.CharField(source="material.name", read_only=True)
    material_code = serializers.CharField(source="material.code", read_only=True)
    from_warehouse_name = serializers.CharField(
        source="from_warehouse.name", read_only=True
    )
    to_warehouse_name = serializers.CharField(
        source="to_warehouse.name", read_only=True
    )
    performed_by_name = serializers.CharField(
        source="performed_by.get_full_name", read_only=True
    )

    class Meta:
        model = InventoryTransaction
        fields = [
            "id",
            "material",
            "material_name",
            "material_code",
            "transaction_type",
            "quantity",
            "from_warehouse",
            "from_warehouse_name",
            "to_warehouse",
            "to_warehouse_name",
            "performed_by",
            "performed_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryTransactionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating InventoryTransaction objects.
    """

    class Meta:
        model = InventoryTransaction
        fields = [
            "material",
            "transaction_type",
            "quantity",
            "from_warehouse",
            "to_warehouse",
            "project",
            "purchase_order_item",
            "is_general_use",
            "notes",
        ]

    def validate(self, data):
        """
        Validate transaction data.
        """
        transaction_type = data.get("transaction_type")
        from_warehouse = data.get("from_warehouse")
        to_warehouse = data.get("to_warehouse")

        # Validate warehouse requirements based on transaction type
        if transaction_type == "receipt" and not to_warehouse:
            raise serializers.ValidationError(
                {"to_warehouse": "To warehouse is required for receipt transactions."}
            )
        elif transaction_type == "issue" and not from_warehouse:
            raise serializers.ValidationError(
                {"from_warehouse": "From warehouse is required for issue transactions."}
            )
        elif transaction_type == "transfer":
            if not from_warehouse:
                raise serializers.ValidationError(
                    {
                        "from_warehouse": "From warehouse is required for transfer transactions."
                    }
                )
            if not to_warehouse:
                raise serializers.ValidationError(
                    {
                        "to_warehouse": "To warehouse is required for transfer transactions."
                    }
                )
            if from_warehouse == to_warehouse:
                raise serializers.ValidationError(
                    "From and To warehouses cannot be the same for transfers."
                )

        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new inventory transaction and update inventory levels.
        """
        # Set the performed_by field to the current user
        validated_data["performed_by"] = self.context["request"].user
        return super().create(validated_data)


class InventoryTransactionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed InventoryTransaction information.
    """

    material = MaterialListSerializer(read_only=True)
    from_warehouse = WarehouseSerializer(read_only=True)
    to_warehouse = WarehouseSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    performed_by_name = serializers.CharField(
        source="performed_by.get_full_name", read_only=True
    )

    class Meta:
        model = InventoryTransaction
        fields = [
            "id",
            "material",
            "transaction_type",
            "quantity",
            "from_warehouse",
            "to_warehouse",
            "project",
            "purchase_order_item",
            "performed_by",
            "performed_by_name",
            "is_general_use",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
