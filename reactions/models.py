from django.db import models
from django.contrib.auth.models import User
from blog.models import Post
from comments.models import Comment

class PostLike(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} ❤️ {self.post.title}"
    
class CommentLike(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "comment")

    def __str__(self):
        return f"{self.user.username} ❤️ Commentaire"