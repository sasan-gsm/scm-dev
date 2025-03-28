from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"materials", views.MaterialViewSet, basename="material")
router.register(
    r"categories", views.MaterialCategoryViewSet, basename="material-category"
)

app_name = "materials"

urlpatterns = [
    path("", include(router.urls)),
]
