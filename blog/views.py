from django.shortcuts import render, get_object_or_404
from .models import Post, Category


def index(request):

    search = request.GET.get("search")

    posts = Post.objects.filter(status="Published")

    if search:
        posts = posts.filter(title__icontains=search)

    categories = Category.objects.all()

    context = {
        "posts": posts.order_by("-created_at"),
        "categories": categories,
        "search": search,
    }

    return render(request, "blog/index.html", context)


def detail(request, slug):

    post = get_object_or_404(
        Post,
        slug=slug,
        status="Published"
    )

    # Incrémente le nombre de vues
    viewed_posts = request.session.get("viewed_posts", [])

    if post.id not in viewed_posts:
        post.views += 1
        post.save(update_fields=["views"])

        viewed_posts.append(post.id)
        request.session["viewed_posts"] = viewed_posts

    context = {
        "post": post
    }

    return render(
        request,
        "blog/detail.html",
        context
    )