from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.UserDashboardView.as_view(), name="user-dashboard"),
    path("projects/", views.project_stats, name="project-stats"),
    path("inventory/", views.inventory_stats, name="inventory-stats"),
    path("requests/", views.request_stats, name="request-stats"),
    path("procurement/", views.procurement_stats, name="procurement-stats"),
]
