from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from comments.models import Comment
from .models import CommentLike
from blog.models import Post
from django.contrib.auth.decorators import login_required
@login_required

def comment_like(request, id):

    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Connexion requise"},
            status=401
        )

    comment = get_object_or_404(
        Comment,
        id=id
    )

    like = CommentLike.objects.filter(
        comment=comment,
        user=request.user
    )

    if like.exists():

        like.delete()
        liked = False

    else:

        CommentLike.objects.create(
            comment=comment,
            user=request.user
        )

        liked = True

    return JsonResponse({
        "liked": liked,
        "likes": comment.likes.count()
    })

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