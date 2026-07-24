from django.contrib import admin
from .models import Comment


@admin.action(description="Réapprouver les commentaires sélectionnés")
def approve_comments(modeladmin, request, queryset):
    queryset.update(is_approved=True, reports_count=0)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "post",
        "is_approved",
        "reports_count",
        "created_at",
    )

    search_fields = (
        "content",
        "user__username",
    )

    list_filter = (
        "is_approved",
        "created_at",
    )

    actions = [approve_comments]
