from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationSettingViewSet

app_name = "notifications"

router = DefaultRouter()
router.register(r"", NotificationViewSet, basename="notification")
router.register(
    r"settings", NotificationSettingViewSet, basename="notification-setting"
)

urlpatterns = [
    path("", include(router.urls)),
]
