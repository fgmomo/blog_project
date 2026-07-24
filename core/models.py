from django.db import models
from django.utils import timezone

from .validators import validate_image_extension, validate_image_size


class TeamMember(models.Model):

    name = models.CharField(max_length=100)

    role = models.CharField("Poste", max_length=100)

    photo = models.ImageField(
        upload_to="team/",
        blank=True,
        null=True,
        validators=[validate_image_extension, validate_image_size]
    )

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Membre de l'équipe"
        verbose_name_plural = "Membres de l'équipe"

    def __str__(self):
        return f"{self.name} — {self.role}"


class Partner(models.Model):

    name = models.CharField(max_length=100)

    logo = models.ImageField(
        upload_to="partners/",
        blank=True,
        null=True,
        validators=[validate_image_extension, validate_image_size]
    )

    website_url = models.URLField("Site web", blank=True)

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"

    def __str__(self):
        return self.name


class Advertisement(models.Model):

    PLACEMENT_CHOICES = [
        ("home", "Bandeau page d'accueil"),
        ("sidebar", "Sidebar des articles"),
        ("article", "Bas de page article"),
    ]

    title = models.CharField("Référence interne", max_length=100)

    image = models.ImageField(
        upload_to="ads/",
        validators=[validate_image_extension, validate_image_size]
    )

    link_url = models.URLField("Lien de destination")

    placement = models.CharField(max_length=20, choices=PLACEMENT_CHOICES)

    start_date = models.DateField()

    end_date = models.DateField()

    is_active = models.BooleanField(default=True)

    clicks_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Publicité"
        verbose_name_plural = "Publicités"

    def is_currently_active(self):
        today = timezone.localdate()
        return self.is_active and self.start_date <= today <= self.end_date

    def __str__(self):
        return f"{self.title} — {self.clicks_count} clics"
