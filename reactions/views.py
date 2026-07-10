from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404

from .models import PostLike
from blog.models import Post


@login_required
def like_post(request, slug):

    post = get_object_or_404(Post, slug=slug)

    like = PostLike.objects.filter(
        user=request.user,
        post=post
    ).first()

    if like:
        like.delete()
    else:
        PostLike.objects.create(
            user=request.user,
            post=post
        )

    return redirect("blog.detail", slug=slug)