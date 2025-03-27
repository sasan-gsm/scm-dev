from django.db import models
from django.utils.translation import gettext_lazy as _
from core.common.models import TimeStampedModel
from core.materials.models import Material
from core.projects.models import Project
from core.procurement.models import PurchaseOrderItem
from django.contrib.auth import get_user_model


User = get_user_model()


class Warehouse(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Code"))
    location = models.CharField(max_length=200, blank=True, verbose_name=_("Location"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Warehouse")
        verbose_name_plural = _("Warehouses")
        db_table = "inventory_warehouses"


class InventoryLocation(TimeStampedModel):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="locations",
        verbose_name=_("Warehouse"),
    )
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    code = models.CharField(max_length=20, verbose_name=_("Code"))

    def __str__(self):
        return f"{self.warehouse.name} - {self.name}"

    class Meta:
        unique_together = ("warehouse", "code")
        verbose_name = _("Inventory Location")
        verbose_name_plural = _("Inventory Locations")
        db_table = "inventory_locations"


class InventoryItem(TimeStampedModel):
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name="inventory_items",
        verbose_name=_("Material"),
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="inventory_items",
        verbose_name=_("Warehouse"),
    )
    location = models.ForeignKey(
        InventoryLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_items",
        verbose_name=_("Location"),
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name=_("Quantity")
    )
    min_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name=_("Minimum Quantity")
    )
    monitor_stock_level = models.BooleanField(
        default=False, verbose_name=_("Monitor Stock Level")
    )

    def __str__(self):
        return f"{self.material.name} - {self.warehouse.name}"

    class Meta:
        unique_together = ("material", "warehouse", "location")
        verbose_name = _("Inventory Item")
        verbose_name_plural = _("Inventory Items")
        db_table = "inventory_items"


class InventoryTransaction(TimeStampedModel):
    TRANSACTION_TYPES = [
        ("receipt", _("Receipt")),
        ("issue", _("Issue")),
        ("transfer", _("Transfer")),
        ("adjustment", _("Adjustment")),
    ]

    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name=_("Material"),
    )
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPES, verbose_name=_("Transaction Type")
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Quantity")
    )
    from_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="outgoing_transactions",
        null=True,
        blank=True,
        verbose_name=_("From Warehouse"),
    )
    to_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="incoming_transactions",
        null=True,
        blank=True,
        verbose_name=_("To Warehouse"),
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="inventory_transactions",
        verbose_name=_("Project"),
    )
    purchase_order_item = models.ForeignKey(
        PurchaseOrderItem,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="inventory_transactions",
        verbose_name=_("Purchase Order Item"),
    )
    performed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="inventory_transactions",
        verbose_name=_("Performed By"),
    )
    is_general_use = models.BooleanField(
        default=False, verbose_name=_("Is General Use")
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    def __str__(self):
        return f"{self.transaction_type} - {self.material.name} - {self.quantity}"

    class Meta:
        verbose_name = _("Inventory Transaction")
        verbose_name_plural = _("Inventory Transactions")
        db_table = "inventory_transactions"
