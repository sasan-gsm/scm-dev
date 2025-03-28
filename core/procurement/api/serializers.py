from rest_framework import serializers
from django.db import transaction
from django.utils import timezone

from core.procurement.models import (
    Supplier,
    SupplierContact,
    PurchaseOrder,
    PurchaseOrderItem,
)
from core.projects.api.serializers import ProjectListSerializer
from core.materials.api.serializers import MaterialListSerializer


class SupplierContactSerializer(serializers.ModelSerializer):
    """
    Serializer for SupplierContact model.
    """

    class Meta:
        model = SupplierContact
        fields = [
            "id",
            "supplier",
            "name",
            "position",
            "email",
            "phone",
            "is_primary",
            "notes",
        ]
        read_only_fields = ["id"]


class SupplierListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Suppliers with minimal information.
    """

    class Meta:
        model = Supplier
        fields = ["id", "name", "code", "contact_person", "email", "phone", "is_active"]


class SupplierDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Supplier information.
    """

    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "code",
            "contact_person",
            "email",
            "phone",
            "address",
            "website",
            "tax_id",
            "payment_terms",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for PurchaseOrderItem model.
    """

    material_name = serializers.CharField(source="material.name", read_only=True)
    material_code = serializers.CharField(source="material.code", read_only=True)
    unit = serializers.CharField(source="material.unit", read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = [
            "id",
            "purchase_order",
            "material",
            "material_name",
            "material_code",
            "quantity",
            "unit",
            "unit_price",
            "total_price",
            "status",
            "expected_delivery_date",
            "actual_delivery_date",
            "notes",
        ]
        read_only_fields = ["id", "total_price"]

    def validate(self, data):
        """
        Calculate total price based on quantity and unit price.
        """
        if "quantity" in data and "unit_price" in data:
            data["total_price"] = data["quantity"] * data["unit_price"]
        return data


class PurchaseOrderItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating PurchaseOrderItem objects.
    """

    class Meta:
        model = PurchaseOrderItem
        fields = [
            "material",
            "quantity",
            "unit_price",
            "expected_delivery_date",
            "notes",
        ]

    def validate(self, data):
        """
        Calculate total price based on quantity and unit price.
        """
        if "quantity" in data and "unit_price" in data:
            data["total_price"] = data["quantity"] * data["unit_price"]
        return data


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing PurchaseOrders with minimal information.
    """

    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "order_number",
            "supplier_id",
            "supplier_name",
            "project_id",
            "project_name",
            "order_date",
            "expected_delivery_date",
            "status",
            "item_count",
            "total_amount",
        ]


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed PurchaseOrder information.
    """

    supplier = SupplierDetailSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "order_number",
            "supplier",
            "project",
            "order_date",
            "expected_delivery_date",
            "delivery_address",
            "shipping_method",
            "payment_terms",
            "status",
            "notes",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "order_number", "created_at", "updated_at"]


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new PurchaseOrder with items.
    """

    items = PurchaseOrderItemCreateSerializer(many=True, required=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "supplier",
            "project",
            "expected_delivery_date",
            "delivery_address",
            "shipping_method",
            "payment_terms",
            "notes",
            "items",
        ]

    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new purchase order with items.
        """
        items_data = validated_data.pop("items")

        # Set the order date to today
        validated_data["order_date"] = timezone.now().date()
        validated_data["status"] = "draft"

        purchase_order = PurchaseOrder.objects.create(**validated_data)

        for item_data in items_data:
            PurchaseOrderItem.objects.create(
                purchase_order=purchase_order, status="pending", **item_data
            )

        return purchase_order


class PurchaseOrderUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing PurchaseOrder.
    """

    class Meta:
        model = PurchaseOrder
        fields = [
            "supplier",
            "project",
            "expected_delivery_date",
            "delivery_address",
            "shipping_method",
            "payment_terms",
            "notes",
            "status",
        ]

    def validate_status(self, value):
        """
        Validate status transitions.
        """
        purchase_order = self.instance

        # Define allowed status transitions
        allowed_transitions = {
            "draft": ["submitted", "cancelled"],
            "submitted": ["approved", "rejected", "cancelled"],
            "approved": ["in_progress", "cancelled"],
            "in_progress": ["partially_received", "received", "cancelled"],
            "partially_received": ["received", "cancelled"],
            "received": ["completed"],
            "completed": [],  # No transitions allowed from completed
            "rejected": [],  # No transitions allowed from rejected
            "cancelled": [],  # No transitions allowed from cancelled
        }

        if value != purchase_order.status and value not in allowed_transitions.get(
            purchase_order.status, []
        ):
            raise serializers.ValidationError(
                f"Cannot change status from '{purchase_order.status}' to '{value}'."
            )

        return value
