from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from core.common.views import health_check

# Get permission classes from settings or use default
swagger_permission_classes = getattr(
    settings, "SWAGGER_PERMISSION_CLASSES", [permissions.IsAuthenticated]
)

# Convert string permission classes to actual classes
if isinstance(swagger_permission_classes, list) and all(
    isinstance(item, str) for item in swagger_permission_classes
):
    from django.utils.module_loading import import_string

    swagger_permission_classes = [
        import_string(cls) for cls in swagger_permission_classes
    ]

# Check if Swagger is enabled (default to True if not specified)
swagger_enabled = getattr(settings, "SWAGGER_SETTINGS", {}).get("ENABLED", True)

if swagger_enabled:
    schema_view = get_schema_view(
        openapi.Info(
            title="SCM API",
            default_version="v1",
            description="Supply Chain Management API documentation",
            terms_of_service="https://www.example.com/terms/",
            contact=openapi.Contact(email="contact@example.com"),
            license=openapi.License(name="MIT License"),
        ),
        public=True,
        permission_classes=swagger_permission_classes,
    )

    swagger_patterns = [
        path(
            "swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
        ),
    ]
else:
    swagger_patterns = []

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("health/", health_check, name="health_check"),
    # API endpoints
    path("api/projects/", include("core.projects.api.urls", namespace="projects")),
    path("api/inventory/", include("core.inventory.api.urls", namespace="inventory")),
    path(
        "api/accounting/", include("core.accounting.api.urls", namespace="accounting")
    ),
    path("api/request/", include("core.request.api.urls", namespace="request")),
    path(
        "api/procurement/",
        include("core.procurement.api.urls", namespace="procurement"),
    ),
    path("api/quality/", include("core.quality.api.urls", namespace="quality")),
    path("api/materials/", include("core.materials.api.urls", namespace="materials")),
    path("api/accounts/", include("core.accounts.api.urls", namespace="accounts")),
    path(
        "api/notifications/",
        include("core.notifications.api.urls", namespace="notifications"),
    ),
    path(
        "api/attachments/",
        include("core.attachments.api.urls", namespace="attachments"),
    ),
    path("api/dashboard/", include("core.dashboard.api.urls", namespace="dashboard")),
] + swagger_patterns

# Debug toolbar only in development
# if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
#     import debug_toolbar

#     urlpatterns = [
#         path("__debug__/", include(debug_toolbar.urls)),
#     ] + urlpatterns
