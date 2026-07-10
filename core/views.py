from django.shortcuts import render
from blog.models import Post, Category


def home(request):
    featured_post = Post.objects.filter(status="Published").order_by("-created_at").first()
    latest_posts = Post.objects.filter(status="Published").order_by("-created_at")[:6]
    
    categories = Category.objects.all()

    context = {
        "latest_posts": latest_posts,
        "featured_post": featured_post,
        "categories": categories,
    }

    return render(request, "core/home.html", context)