from django.contrib import admin
from .models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "author",
        "category",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "category",
    )

    search_fields = (
        "title",
        "content",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }