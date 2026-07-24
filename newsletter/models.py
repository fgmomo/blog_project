import uuid

from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db import models


class Subscriber(models.Model):

    email = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-subscribed_at"]
        verbose_name = "Abonné"
        verbose_name_plural = "Abonnés"

    def __str__(self):
        return self.email


class Campaign(models.Model):

    subject = models.CharField("Sujet", max_length=255)

    body = RichTextUploadingField("Contenu")

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="campaigns"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Campagne"
        verbose_name_plural = "Campagnes"

    @property
    def is_sent(self):
        return self.sent_at is not None

    def __str__(self):
        return self.subject
