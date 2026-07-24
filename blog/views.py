from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import models
from .models import Post, Category
from django.http import JsonResponse
from comments.forms import CommentForm
from comments.models import Comment
from .models import Post
from reactions.models import PostLike, CommentLike
from django_ratelimit.decorators import ratelimit

POSTS_PER_PAGE = 9
POSTS_PER_PAGE_CHOICES = [9, 15, 21]


def index(request):

    search = request.GET.get("search")
    category_id = request.GET.get("category")

    posts = Post.objects.filter(status="Published")
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

    if search:
        posts = posts.filter(title__icontains=search)

    if category_id:
        posts = posts.filter(category_id=category_id)

    categories = Category.objects.all()
    popular_posts = Post.objects.filter(status="Published").order_by("-views")[:2]

    recent_posts = Post.objects.filter(status="Published").order_by("-created_at")[:2]

    try:
        per_page = int(request.GET.get("per_page", POSTS_PER_PAGE))
    except (TypeError, ValueError):
        per_page = POSTS_PER_PAGE

    if per_page not in POSTS_PER_PAGE_CHOICES:
        per_page = POSTS_PER_PAGE

    paginator = Paginator(posts.order_by("-created_at"), per_page)
    posts_page = paginator.get_page(request.GET.get("page"))

    context = {
        "posts": posts_page,
        "paginator": paginator,
        "categories": categories,
        "search": search,
        "liked_posts": liked_posts,

        "popular_posts": popular_posts,
        "recent_posts": recent_posts,

        "per_page": per_page,
        "per_page_choices": POSTS_PER_PAGE_CHOICES,

    }

    return render(request, "blog/index.html", context)

@ratelimit(key='user_or_ip', rate='20/m', method='POST', block=True)
def detail(request, slug):

    post = get_object_or_404(
        Post,
        slug=slug,
        status="Published"
    )

    # Gestion des vues
    viewed_posts = request.session.get("viewed_posts", [])

    if post.id not in viewed_posts:
        post.views += 1
        post.save(update_fields=["views"])

        viewed_posts.append(post.id)
        request.session["viewed_posts"] = viewed_posts

    # Vérifie si l'utilisateur a liké
    liked = False

    if request.user.is_authenticated:
        liked = PostLike.objects.filter(
            post=post,
            user=request.user
        ).exists()

    form = CommentForm()

    if request.method == "POST" and request.user.is_authenticated:

        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)

            comment.user = request.user
            comment.post = post

            parent_id = request.POST.get("parent")

            if parent_id:
                comment.parent_id = parent_id

            comment.save()

            return redirect("blog.detail", slug=slug)

    # Recommandations : d'abord la même catégorie, complété par les plus récents si besoin.
    related_posts = list(
        Post.objects.filter(status="Published", category=post.category)
        .exclude(pk=post.pk)
        .order_by("-created_at")[:3]
    )

    if len(related_posts) < 3:
        exclude_ids = [post.pk] + [p.pk for p in related_posts]
        related_posts += list(
            Post.objects.filter(status="Published")
            .exclude(pk__in=exclude_ids)
            .order_by("-created_at")[:3 - len(related_posts)]
        )

    liked_posts = []

    if request.user.is_authenticated:
        liked_posts = list(
            PostLike.objects.filter(
                user=request.user,
                post__in=related_posts
            ).values_list("post_id", flat=True)
        )

    context = {
        "post": post,
        "liked": liked,
        "form": form,
        "related_posts": related_posts,
        "liked_posts": liked_posts,
    }

    return render(
        request,
        "blog/detail.html",
        context
    )


@ratelimit(key='user_or_ip', rate='30/m', block=False)
def like_post(request, slug):

    if not request.user.is_authenticated:
        return JsonResponse({
            "error": "Vous devez être connecté."
        }, status=401)

    if getattr(request, "limited", False):
        return JsonResponse({
            "error": "Trop de requêtes, réessayez plus tard."
        }, status=429)

    post = get_object_or_404(Post, slug=slug)

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


def categories_index(request):

    categories = Category.objects.annotate(
        published_count=models.Count(
            "posts",
            filter=models.Q(posts__status="Published")
        )
    )

    return render(
        request,
        "blog/categories.html",
        {"categories": categories}
    )


def category_detail(request, slug):

    category = get_object_or_404(Category, slug=slug)

    posts = Post.objects.filter(
        status="Published",
        category=category
    ).order_by("-created_at")

    paginator = Paginator(posts, POSTS_PER_PAGE)
    posts_page = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "blog/category_detail.html",
        {
            "category": category,
            "posts": posts_page,
            "paginator": paginator,
        }
    )


def author_detail(request, username):

    author = get_object_or_404(User, username=username)

    posts = Post.objects.filter(
        status="Published",
        author=author
    ).order_by("-created_at")

    paginator = Paginator(posts, POSTS_PER_PAGE)
    posts_page = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "blog/author_detail.html",
        {
            "author": author,
            "posts": posts_page,
            "paginator": paginator,
        }
    )