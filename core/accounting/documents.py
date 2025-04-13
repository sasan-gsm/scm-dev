from .models import Payment, Invoice
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl import Document, fields
from django.utils.translation import gettext_lazy as _
from django.db.models import QuerySet


@registry.register_document
class InvoiceDocument(Document):
    # ForeignKey fields as nested or keyword fields
    supplier = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.TextField(),
        }
    )

    project = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.TextField(),
        }
    )

    # Payments as nested field
    payments = fields.NestedField(
        properties={
            "id": fields.IntegerField(),
            "reference": fields.KeywordField(),
            "amount": fields.DoubleField(),
            "payment_date": fields.DateField(),
            "payment_method": fields.KeywordField(),
        }
    )

    class Index:
        name = "invoices"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Invoice
        fields = (
            "id",
            "number",
            "invoice_date",
            "due_date",
            "amount",
            "status",
            "notes",
            "created_at",  # to match TimeStampedModel
            "updated_at",
        )
        auto_refresh = True

    def get_queryset(self):
        "Override to optimize DB queries"
        return (
            super()
            .get_queryset()
            .select_related("supplier", "project")
            .prefetch_related("payments")
        )


@registry.register_document
class PaymentDocument(Document):
    # Invoice as object field
    invoice = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "number": fields.KeywordField(),
            "amount": fields.DoubleField(),
            "invoice_date": fields.DateField(),
            "status": fields.KeywordField(),
        }
    )

    # Created by user info
    created_by = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "username": fields.KeywordField(),
        }
    )

    class Index:
        name = "payments"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Payment
        fields = (
            "id",
            "reference",
            "amount",
            "payment_date",
            "payment_method",
            "transaction_id",
            "notes",
            "created_at",
            "updated_at",
        )
        auto_refresh = True

    def get_queryset(self) -> QuerySet[Payment]:
        """Optimize DB queries"""
        return (
            super()
            .get_queryset()
            .select_related(
                "invoice", "invoice__supplier", "invoice__project", "created_by"
            )
        )
