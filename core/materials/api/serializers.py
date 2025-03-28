from rest_framework import serializers
from core.materials.models import Material, MaterialCategory, MaterialPriceHistory


class MaterialCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for MaterialCategory model.
    """

    material_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = MaterialCategory
        fields = ["id", "name", "parent", "material_count", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class MaterialListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Material objects with minimal information.
    """

    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Material
        fields = [
            "id",
            "code",
            "name",
            "category",
            "category_name",
            "unit",
            "unit_price",
            "is_active",
        ]
        read_only_fields = ["id"]


class MaterialDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Material information.
    """

    category = MaterialCategorySerializer(read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )
    price_history = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = [
            "id",
            "code",
            "name",
            "description",
            "category",
            "unit",
            "technical_specs",
            "unit_price",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "price_history",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
        ]

    def get_price_history(self, obj):
        """Get the price history for the material."""
        history = obj.price_history.all()[:5]  # Get the 5 most recent price changes
        return [
            {
                "price": item.price,
                "effective_date": item.effective_date,
                "recorded_by": item.recorded_by.get_full_name(),
            }
            for item in history
        ]


class MaterialCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Material objects.
    """

    class Meta:
        model = Material
        fields = [
            "code",
            "name",
            "description",
            "category",
            "unit",
            "technical_specs",
            "unit_price",
            "is_active",
        ]

    def create(self, validated_data):
        """Create a new material with the current user as created_by."""
        user = self.context["request"].user
        validated_data["created_by"] = user
        return super().create(validated_data)


class MaterialPriceHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for MaterialPriceHistory model.
    """

    recorded_by_name = serializers.CharField(
        source="recorded_by.get_full_name", read_only=True
    )

    class Meta:
        model = MaterialPriceHistory
        fields = [
            "id",
            "material",
            "price",
            "effective_date",
            "recorded_by",
            "recorded_by_name",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "recorded_by", "recorded_by_name"]
