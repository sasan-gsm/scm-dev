from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.projects.models import Project
from core.accounting.models import (
    GeneralExpense as Expense,
    BudgetItem,
    Invoice,
    Budget,
    ExpenseCategory,
    Payment,
)
from core.projects.api.serializers import ProjectListSerializer

User = get_user_model()


class ExpenseCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for ExpenseCategory model.
    """

    class Meta:
        model = ExpenseCategory
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "parent",
        ]
        read_only_fields = ["id"]


class ExpenseListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Expenses with minimal information.
    """

    project_name = serializers.CharField(source="project.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            "id",
            "description",
            "amount",
            "expense_date",
            "project_id",
            "project_name",
            # "category",
            "category_name",
            "allocation_type",
            "created_by_id",
            "created_by_name",
        ]

    def get_created_by_name(self, obj):
        """Get the full name of the user who created the expense."""
        if obj.created_by:
            return (
                f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
                or obj.created_by.username
            )
        return None


class ExpenseDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Expense information.
    """

    project = ProjectListSerializer(read_only=True)
    category = ExpenseCategorySerializer(read_only=True)
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            "id",
            "description",
            "amount",
            "expense_date",
            "project",
            "category",
            "allocation_type",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def get_created_by(self, obj):
        """Get information about the user who created the expense."""
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "username": obj.created_by.username,
                "name": f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
                or obj.created_by.username,
            }
        return None


class ExpenseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new GeneralExpense.
    """

    class Meta:
        model = Expense
        fields = [
            "description",
            "amount",
            "expense_date",
            "project",
            "allocation_type",
        ]

    def create(self, validated_data):
        """
        Create a new expense and set the created_by field.
        """
        user = self.context["request"].user
        validated_data["created_by"] = user
        return super().create(validated_data)


class BudgetItemSerializer(serializers.ModelSerializer):
    """
    Serializer for BudgetItem model.
    """

    class Meta:
        model = BudgetItem
        fields = [
            "id",
            "budget",
            "name",
            "description",
            "amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BudgetListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Budgets with minimal information.
    """

    project_name = serializers.CharField(source="project.name", read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )

    class Meta:
        model = Budget
        fields = [
            "id",
            "budget_number",
            "name",
            "project_id",
            "project_name",
            "start_date",
            "end_date",
            "status",
            "total_amount",
        ]


class BudgetDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Budget information.
    """

    project = ProjectListSerializer(read_only=True)
    items = BudgetItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )

    class Meta:
        model = Budget
        fields = [
            "id",
            "budget_number",
            "name",
            "description",
            "project",
            "start_date",
            "end_date",
            "status",
            "items",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "budget_number", "created_at", "updated_at"]


class BudgetCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Budget with items.
    """

    items = BudgetItemSerializer(many=True, required=False)

    class Meta:
        model = Budget
        fields = [
            "name",
            "description",
            "project",
            "start_date",
            "end_date",
            "status",
            "items",
        ]

    def create(self, validated_data):
        """
        Create a new budget with budget items.
        """
        items_data = validated_data.pop("items", [])
        user = self.context["request"].user
        validated_data["created_by"] = user
        budget = Budget.objects.create(**validated_data)

        for item_data in items_data:
            BudgetItem.objects.create(budget=budget, **item_data)

        return budget


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Invoice model.
    """

    project = ProjectListSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), source="project", write_only=True
    )
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "number",
            "supplier",
            "supplier_name",
            "project",
            "project_id",
            "invoice_date",
            "due_date",
            "amount",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for Payment model.
    """

    invoice_number = serializers.CharField(source="invoice.number", read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "reference",
            "invoice",
            "invoice_number",
            "amount",
            "payment_date",
            "payment_method",
            "transaction_id",
            "notes",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]

    def get_created_by_name(self, obj):
        """Get the full name of the user who created the payment."""
        if obj.created_by:
            return (
                f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
                or obj.created_by.username
            )
        return None

    def create(self, validated_data):
        """
        Create a new payment and set the created_by field.
        """
        user = self.context["request"].user
        validated_data["created_by"] = user
        return super().create(validated_data)
