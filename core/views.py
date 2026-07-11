from django.shortcuts import render
from blog.models import Post, Category
from reactions.models import PostLike, CommentLike, Comment

from django.http import JsonResponse
from django.shortcuts import get_object_or_404


def comment_like(request, id):

    if not request.user.is_authenticated:
        return JsonResponse({"error": "login"}, status=401)

    comment = get_object_or_404(Comment, id=id)

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


def home(request):

    latest_posts = Post.objects.filter(
        status="Published"
    ).order_by("-created_at")[:6]

    liked_posts = []

    if request.user.is_authenticated:

        liked_posts = list(

            PostLike.objects.filter(
                user=request.user
            ).values_list(
                "post_id",
                flat=True
            )

        )

    return render(

        request,

        "core/home.html",

        {
            "latest_posts": latest_posts,
            "liked_posts": liked_posts,
        }

    )