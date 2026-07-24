from django.contrib import admin
from .models import Emission


@admin.register(Emission)
class EmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "host", "created_at")
    search_fields = ("title", "host", "description")

    prepopulated_fields = {
        "slug": ("title",)
    }
