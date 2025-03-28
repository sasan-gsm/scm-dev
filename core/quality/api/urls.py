from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QualityStandardViewSet,
    QualityCheckViewSet,
    QualityCheckItemViewSet,
)

app_name = "quality"

router = DefaultRouter()
router.register(r"standards", QualityStandardViewSet, basename="quality-standard")
router.register(r"checks", QualityCheckViewSet, basename="quality-check")
router.register(r"check-items", QualityCheckItemViewSet, basename="quality-check-item")


urlpatterns = [
    path("", include(router.urls)),
]
