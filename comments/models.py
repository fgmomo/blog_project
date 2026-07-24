from django.db import models
from django.contrib.auth.models import User
from blog.models import Post


class Comment(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    is_approved = models.BooleanField(default=True)

    reports_count = models.PositiveIntegerField(default=0)

    is_edited = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]