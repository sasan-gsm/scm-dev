from typing import Dict, Any, List, Optional
from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_RANGE,
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
    LOOKUP_QUERY_EXCLUDE,
)
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    IdsFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    SearchFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import BaseDocumentViewSet
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination

from rest_framework.permissions import IsAuthenticated
from core.accounting.documents import InvoiceDocument, PaymentDocument
from .es_serializers import InvoiceDocumentSerializer, PaymentDocumentSerializer


class InvoiceDocumentViewSet(BaseDocumentViewSet):
    """
    A viewset for InvoiceDocument.

    Provides search, filtering, and ordering capabilities for Invoice documents.
    """

    document = InvoiceDocument
    serializer_class = InvoiceDocumentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    lookup_field = "id"

    filter_backends = [
        FilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]

    # Define search fields
    search_fields = (
        "number",
        "notes",
        "supplier.name",
        "project.name",
    )

    # Define filtering fields
    filter_fields = {
        "id": {
            "field": "id",
            "lookups": [
                LOOKUP_FILTER_TERMS,
                LOOKUP_QUERY_IN,
            ],
        },
        "number": {
            "field": "number",
            "lookups": [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
            ],
        },
        "status": {
            "field": "status",
            "lookups": [
                LOOKUP_FILTER_TERMS,
                LOOKUP_QUERY_IN,
            ],
        },
        "invoice_date": {
            "field": "invoice_date",
            "lookups": [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        "due_date": {
            "field": "due_date",
            "lookups": [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        "amount": {
            "field": "amount",
            "lookups": [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        "supplier_id": {
            "field": "supplier.id",
            "lookups": [
                LOOKUP_FILTER_TERMS,
                LOOKUP_QUERY_IN,
            ],
        },
        "project_id": {
            "field": "project.id",
            "lookups": [
                LOOKUP_FILTER_TERMS,
                LOOKUP_QUERY_IN,
            ],
        },
    }

    # Define ordering fields
    ordering_fields = {
        "id": "id",
        "number": "number",
        "invoice_date": "invoice_date",
        "due_date": "due_date",
        "amount": "amount",
        "created_at": "created_at",
    }

    # Define default ordering
    ordering = ("invoice_date",)


class PaymentDocumentViewSet(BaseDocumentViewSet):
    """
    A viewset for PaymentDocument.

    Provides search, filtering, and ordering capabilities for Payment documents.
    """

    document = PaymentDocument
    serializer_class = PaymentDocumentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
    lookup_field = "id"

    filter_backends = [
        FilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]

    # Define search fields
    search_fields = (
        "reference",
        "transaction_id",
        "notes",
        "invoice.number",
    )

    # Define filtering fields
    filter_fields = {
        "id": {
            "field": "id",
            "lookups": [
                LOOKUP_FILTER_TERMS,
                LOOKUP_QUERY_IN,
            ],
        },
        "reference": {
            "field": "reference",
            "lookups": [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
            ],
        },
        "payment_method": {
            "field": "payment_method",
            "lookups": [
                LOOKUP_FILTER_TERMS,
                LOOKUP_QUERY_IN,
            ],
        },
        "payment_date": {
            "field": "payment_date",
            "lookups": [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        "amount": {
            "field": "amount",
            "lookups": [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        "invoice_id": {
            "field": "invoice.id",
            "lookups": [
                LOOKUP_FILTER_TERMS,
                LOOKUP_QUERY_IN,
            ],
        },
        "created_by_id": {
            "field": "created_by.id",
            "lookups": [
                LOOKUP_FILTER_TERMS,
                LOOKUP_QUERY_IN,
            ],
        },
    }

    # Define ordering fields
    ordering_fields = {
        "id": "id",
        "reference": "reference",
        "payment_date": "payment_date",
        "amount": "amount",
        "created_at": "created_at",
    }

    # Define default ordering
    ordering = ("payment_date",)
