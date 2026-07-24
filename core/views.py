from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from blog.models import Post, Category
from emissions.models import Emission
from reactions.models import PostLike

from .models import Advertisement, Partner, TeamMember


def home(request):

    latest_posts = Post.objects.filter(
        status="Published"
    ).order_by("-created_at")[:3]

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

    categories = Category.objects.all()[:6]
    emissions = Emission.objects.all()[:3]

    return render(

        request,

        "core/home.html",

        {
            "latest_posts": latest_posts,
            "liked_posts": liked_posts,
            "categories": categories,
            "emissions": emissions,
        }

    )


def services(request):
    return render(request, "core/services.html")


def legal_notice(request):
    return render(request, "core/mentions_legales.html")


def privacy_policy(request):
    return render(request, "core/confidentialite.html")


def terms(request):
    return render(request, "core/cgu.html")


def about(request):
    return render(
        request,
        "core/about.html",
        {
            "team_members": TeamMember.objects.all(),
            "partners": Partner.objects.all(),
        }
    )


def ad_click(request, pk):
    ad = get_object_or_404(Advertisement, pk=pk)
    Advertisement.objects.filter(pk=pk).update(clicks_count=F("clicks_count") + 1)
    return redirect(ad.link_url)