from django.db import models
from django.utils.translation import gettext_lazy as _
from core.common.models import TimeStampedModel
from core.materials.models import Material
from core.request.models import RequestItem
from django.contrib.auth import get_user_model


User = get_user_model()


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Code"))
    contact_person = models.CharField(
        max_length=100, blank=True, verbose_name=_("Contact Person")
    )
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=50, blank=True, verbose_name=_("Phone"))
    address = models.TextField(blank=True, verbose_name=_("Address"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")
        db_table = "suppliers"
        ordering = ["name"]


class SupplierContact(TimeStampedModel):
    """
    Contact information for suppliers.
    """

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name=_("Supplier"),
    )
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    position = models.CharField(max_length=255, blank=True, verbose_name=_("Position"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=50, blank=True, verbose_name=_("Phone"))
    is_primary = models.BooleanField(
        default=False, verbose_name=_("Is Primary Contact")
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    def __str__(self):
        return f"{self.name} - {self.supplier.name}"

    class Meta:
        verbose_name = _("Supplier Contact")
        verbose_name_plural = _("Supplier Contacts")
        db_table = "supplier_contact"


class PurchaseOrder(TimeStampedModel):
    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("sent", _("Sent to Supplier")),
        ("confirmed", _("Confirmed by Supplier")),
        ("partially_received", _("Partially Received")),
        ("fully_received", _("Fully Received")),
        ("cancelled", _("Cancelled")),
    ]

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchase_orders",
        verbose_name=_("Supplier"),
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.PROTECT,
        related_name="purchase_orders",
        null=True,
        blank=True,
        verbose_name=_("Project"),
    )
    order_number = models.CharField(
        max_length=50, unique=True, verbose_name=_("Order Number")
    )
    order_date = models.DateField(verbose_name=_("Order Date"))
    expected_delivery_date = models.DateField(
        null=True, blank=True, verbose_name=_("Expected Delivery Date")
    )
    delivery_address = models.TextField(blank=True, verbose_name=_("Delivery Address"))
    shipping_method = models.CharField(
        max_length=100, blank=True, verbose_name=_("Shipping Method")
    )
    payment_terms = models.CharField(
        max_length=100, blank=True, verbose_name=_("Payment Terms")
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name=_("Status")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_purchase_orders",
        verbose_name=_("Created By"),
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name=_("Total Amount")
    )

    def __str__(self):
        return f"PO-{self.order_number}"

    class Meta:
        verbose_name = _("Purchase Order")
        verbose_name_plural = _("Purchase Orders")
        db_table = "purchase_orders"


class PurchaseOrderItem(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("ordered", _("Ordered")),
        ("partially_received", _("Partially Received")),
        ("fully_received", _("Fully Received")),
        ("cancelled", _("Cancelled")),
    ]

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Purchase Order"),
    )
    request_item = models.ForeignKey(
        RequestItem,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="purchase_order_items",
        verbose_name=_("Request Item"),
    )
    material = models.ForeignKey(
        Material, on_delete=models.PROTECT, verbose_name=_("Material")
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Quantity")
    )
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Unit Price"), default=0
    )
    total_price = models.DecimalField(
        max_digits=14, decimal_places=2, verbose_name=_("Total Price"), default=0
    )
    received_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name=_("Received Quantity")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
    )
    expected_delivery_date = models.DateField(
        null=True, blank=True, verbose_name=_("Expected Delivery Date")
    )
    actual_delivery_date = models.DateField(
        null=True, blank=True, verbose_name=_("Actual Delivery Date")
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    def __str__(self):
        return f"{self.material.name} - {self.quantity}"

    class Meta:
        verbose_name = _("Purchase Order Item")
        verbose_name_plural = _("Purchase Order Items")
        db_table = "purchase_order_items"
