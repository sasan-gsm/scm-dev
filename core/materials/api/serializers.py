from rest_framework import serializers
from core.materials.models import Material, MaterialCategory, MaterialPriceHistory


class MaterialCategorySerializer(serializers.ModelSerializer):
    material_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = MaterialCategory
        fields = ["id", "name", "parent", "material_count", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class MaterialListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Material
        fields = [
            "id",
            "code",
            "name",
            "category",
            "category_name",
            "unit_of_measure",
            "unit_price",
            "is_active",
        ]
        read_only_fields = ["id"]


class MaterialDetailSerializer(serializers.ModelSerializer):
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
            "unit_of_measure",
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
    class Meta:
        model = Material
        fields = [
            "code",
            "name",
            "description",
            "category",
            "unit_of_measure",
            "technical_specs",
            "unit_price",
            "is_active",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        return super().create(validated_data)


class MaterialPriceHistorySerializer(serializers.ModelSerializer):
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
