from django.shortcuts import render
from blog.models import Post, Category
from reactions.models import PostLike, CommentLike


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