from django.contrib import admin
from .models import PostLike, CommentLike


admin.site.register(PostLike)
admin.site.register(CommentLike)