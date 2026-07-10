from django.contrib import admin
from .models import Comment, CommentReply


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "post",
        "created_at",
    )

    search_fields = (
        "content",
        "user__username",
    )

    list_filter = (
        "created_at",
    )


@admin.register(CommentReply)
class CommentReplyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "comment",
        "created_at",
    )

    search_fields = (
        "content",
    )