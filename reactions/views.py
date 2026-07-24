from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from comments.models import Comment
from .models import CommentLike

REPORTS_THRESHOLD = 3


@ratelimit(key='user_or_ip', rate='30/m', block=False)
def comment_like(request, id):

    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Connexion requise"},
            status=401
        )

    if getattr(request, "limited", False):
        return JsonResponse(
            {"error": "Trop de requêtes, réessayez plus tard."},
            status=429
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


@ratelimit(key='user_or_ip', rate='10/m', block=False)
def report_comment(request, id):

    if not request.user.is_authenticated:
        return JsonResponse(
            {"error": "Connexion requise"},
            status=401
        )

    if getattr(request, "limited", False):
        return JsonResponse(
            {"error": "Trop de requêtes, réessayez plus tard."},
            status=429
        )

    comment = get_object_or_404(Comment, id=id)

    comment.reports_count += 1

    if comment.reports_count >= REPORTS_THRESHOLD:
        comment.is_approved = False

    comment.save(update_fields=["reports_count", "is_approved"])

    return JsonResponse({
        "reported": True,
        "hidden": not comment.is_approved
    })
