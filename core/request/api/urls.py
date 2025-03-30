from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RequestViewSet, RequestItemViewSet

app_name = "request"

router = DefaultRouter()
router.register(r"requests", RequestViewSet, basename="request")
router.register(r"request-items", RequestItemViewSet, basename="request-item")

urlpatterns = [
    path("", include(router.urls)),
]
