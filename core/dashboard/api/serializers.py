from rest_framework import serializers


class ProjectStatSerializer(serializers.Serializer):
    """
    Serializer for project statistics.
    """

    managed_count = serializers.IntegerField()
    active_count = serializers.IntegerField()
    ending_soon_count = serializers.IntegerField()
    recent_projects = serializers.ListField(child=serializers.DictField())


class InventoryStatSerializer(serializers.Serializer):
    """
    Serializer for inventory statistics.
    """

    low_inventory_count = serializers.IntegerField()
    low_inventory_items = serializers.ListField(child=serializers.DictField())


class RequestStatSerializer(serializers.Serializer):
    """
    Serializer for request statistics.
    """

    my_requests_count = serializers.IntegerField()
    pending_approval_count = serializers.IntegerField()
    recent_requests = serializers.ListField(child=serializers.DictField())


class ProcurementStatSerializer(serializers.Serializer):
    """
    Serializer for procurement statistics.
    """

    orders_due_soon_count = serializers.IntegerField()
    recent_orders = serializers.ListField(child=serializers.DictField())


class DashboardSerializer(serializers.Serializer):
    """
    Serializer for the complete dashboard.
    """

    projects = ProjectStatSerializer()
    inventory = InventoryStatSerializer()
    requests = RequestStatSerializer()
    procurement = ProcurementStatSerializer()
