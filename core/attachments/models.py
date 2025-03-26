from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from core.common.models import TimeStampedModel
from django.contrib.auth import get_user_model


User = get_user_model()


def attachment_upload_path(instance, filename):
    return f"attachments/{instance.content_type.model}/{instance.object_id}/{filename}"


class Attachment(TimeStampedModel):
    file = models.FileField(upload_to=attachment_upload_path, verbose_name=_("File"))
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name=_("Content Type")
    )
    object_id = models.PositiveIntegerField(verbose_name=_("Object ID"))
    content_object = GenericForeignKey("content_type", "object_id")
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="uploaded_attachments",
        verbose_name=_("Uploaded By"),
    )
    file_type = models.CharField(max_length=50, blank=True, verbose_name=_("File Type"))
    file_size = models.PositiveIntegerField(default=0, verbose_name=_("File Size"))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name and self.file:
            self.name = self.file.name
        if self.file:
            self.file_size = self.file.size
            # Extract file extension
            name_parts = self.file.name.split(".")
            if len(name_parts) > 1:
                self.file_type = name_parts[-1].lower()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")
        db_table = "attachments"
