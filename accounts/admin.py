from django.contrib import admin
from .models import Role, Profile


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email")

