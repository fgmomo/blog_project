from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify

from core.validators import validate_image_extension, validate_image_size


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog.category_detail", args=[self.slug])

    def __str__(self):
        return self.name


class Post(models.Model):

    STATUS_CHOICES = (
        ("Draft", "Brouillon"),
        ("Published", "Publié"),
    )

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    content = RichTextUploadingField()

    image = models.ImageField(
        upload_to="posts/",
        blank=True,
        null=True,
        validators=[validate_image_extension, validate_image_size]
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Draft"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    views = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog.detail", args=[self.slug])

    def __str__(self):
        return self.title