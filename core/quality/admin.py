from django.contrib import admin
from .models import QualityStandard, QualityCheck, QualityCheckItem


class QualityCheckItemInline(admin.TabularInline):
    model = QualityCheckItem
    extra = 1


@admin.register(QualityStandard)
class QualityStandardAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "code", "description", "criteria"]
    ordering = ["name"]


@admin.register(QualityCheck)
class QualityCheckAdmin(admin.ModelAdmin):
    list_display = [
        "check_number",
        "project",
        "material",
        "check_date",
        "inspector",
        "status",
        "created_at",
    ]
    list_filter = ["status", "check_date", "project", "inspector"]
    search_fields = ["check_number", "batch_number", "notes"]
    ordering = ["-created_at"]
    inlines = [QualityCheckItemInline]


@admin.register(QualityCheckItem)
class QualityCheckItemAdmin(admin.ModelAdmin):
    list_display = ["quality_check", "standard", "result", "is_passed", "created_at"]
    list_filter = ["is_passed", "standard"]
    search_fields = ["result", "notes"]
    ordering = ["quality_check", "standard"]
