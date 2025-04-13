from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers
from core.accounting.documents import InvoiceDocument, PaymentDocument


class InvoiceDocumentSerializer(DocumentSerializer):
    """
    Serializer for the InvoiceDocument.

    Maps Elasticsearch document fields to a format suitable for API responses.
    """

    # Nested fields
    supplier = serializers.DictField(read_only=True)
    project = serializers.DictField(read_only=True)
    payments = serializers.ListField(read_only=True)

    class Meta:
        """
        Meta options.
        """

        document = InvoiceDocument
        fields = [
            "id",
            "number",
            "invoice_date",
            "due_date",
            "amount",
            "status",
            "notes",
            "created_at",
            "updated_at",
            "supplier",
            "project",
            "payments",
        ]


class PaymentDocumentSerializer(DocumentSerializer):
    """
    Serializer for the PaymentDocument.

    Maps Elasticsearch document fields to a format suitable for API responses.
    """

    # Nested fields
    invoice = serializers.DictField(read_only=True)
    created_by = serializers.DictField(read_only=True)

    class Meta:
        """
        Meta options.
        """

        document = PaymentDocument
        fields = [
            "id",
            "reference",
            "amount",
            "payment_date",
            "payment_method",
            "transaction_id",
            "notes",
            "created_at",
            "updated_at",
            "invoice",
            "created_by",
        ]
