from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.validators import validate_image_extension, validate_image_size


class Emission(models.Model):

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    description = models.TextField()

    cover_image = models.ImageField(
        upload_to="emissions/",
        blank=True,
        null=True,
        validators=[validate_image_extension, validate_image_size]
    )

    host = models.CharField(
        "Animateur(s)",
        max_length=255,
        blank=True
    )

    video_url = models.URLField(
        "Lien vidéo / replay",
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Émission"
        verbose_name_plural = "Émissions"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("emissions.detail", args=[self.slug])

    def __str__(self):
        return self.title
