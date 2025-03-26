from django.db import models
from django.utils.translation import gettext_lazy as _
from core.common.models import TimeStampedModel
from django.contrib.auth import get_user_model


User = get_user_model()


class MaterialCategory(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name=_("Parent Category"),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Material Category")
        verbose_name_plural = _("Material Categories")
        db_table = "material_categories"


class Material(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Code"))
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    category = models.ForeignKey(
        MaterialCategory,
        on_delete=models.PROTECT,
        related_name="materials",
        verbose_name=_("Category"),
    )
    unit_of_measure = models.CharField(max_length=50, verbose_name=_("Unit of Measure"))
    technical_specs = models.JSONField(
        default=dict, verbose_name=_("Technical Specifications")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_materials",
        verbose_name=_("Created By"),
    )

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = _("Material")
        verbose_name_plural = _("Materials")
        db_table = "materials"
