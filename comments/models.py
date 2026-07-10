from django.db import models
from django.contrib.auth.models import User
from blog.models import Post



class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.post.title}"
    
class CommentReply(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="replies"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="replies"
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Réponse de {self.user.username}"