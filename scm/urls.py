from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version="v1",
        description="SCM API documentation",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    # path(
    #     "swagger/",
    #     schema_view.with_ui("swagger", cache_timeout=0),
    #     name="schema-swagger-ui",
    # ),
    # path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # path("accounts/", include("allauth.urls")),  # Allauth URLs
]

# if settings.DEBUG:
#     import debug_toolbar

#     urlpatterns = [
#         path("__debug__/", include(debug_toolbar.urls)),  # Add Debug Toolbar URLs
#     ] + urlpatterns
