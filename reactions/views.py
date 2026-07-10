from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse

from .models import PostLike
from blog.models import Post


@login_required
def like_post(request, slug):

    if not request.user.is_authenticated:

        return JsonResponse({

            "error": "login"

        })

    post = get_object_or_404(

        Post,

        slug=slug

    )

    like = PostLike.objects.filter(

        post=post,

        user=request.user

    )

    if like.exists():

        like.delete()

        liked = False

    else:

        PostLike.objects.create(

            post=post,

            user=request.user

        )

        liked = True

    return JsonResponse({

        "liked": liked,

        "likes": post.likes.count()

    })