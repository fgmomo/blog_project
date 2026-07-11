from django.shortcuts import render, get_object_or_404,redirect
from .models import Post, Category
from django.http import JsonResponse
from comments.forms import CommentForm
from comments.models import Comment
from .models import Post
from reactions.models import PostLike, CommentLike
def index(request):

    search = request.GET.get("search")

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

    categories = Category.objects.all()
    popular_posts = Post.objects.filter(status="Published").order_by("-views")[:2]

    recent_posts = Post.objects.filter(status="Published").order_by("-created_at")[:2]
    
    context = {
        "posts": posts.order_by("-created_at"),
        "categories": categories,
        "search": search,
        "liked_posts": liked_posts,

        "popular_posts": popular_posts,
        "recent_posts": recent_posts,

    }

    return render(request, "blog/index.html", context)

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

    context = {
        "post": post,
        "liked": liked,
        "form": form,
    }

    return render(
        request,
        "blog/detail.html",
        context
    )


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

    # Formulaire de commentaire
    form = CommentForm()

    if request.method == "POST" and request.user.is_authenticated:

        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)

            comment.user = request.user

            comment.post = post

            parent_id = request.POST.get("parent")

            if parent_id:

                comment.parent = Comment.objects.get(id=parent_id)

            comment.save()

            return redirect("blog.detail", slug=slug)

    context = {
        "post": post,
        "liked": liked,
        "form": form,
    }

    return render(
        request,
        "blog/detail.html",
        context
    )

    post = get_object_or_404(
        Post,
        slug=slug,
        status="Published"
    )

    # Incrémente le nombre de vues
    viewed_posts = request.session.get("viewed_posts", [])

    liked = False

    if request.user.is_authenticated:
        liked = PostLike.objects.filter(
            post=post,
            user=request.user
        ).exists()

    if post.id not in viewed_posts:
        post.views += 1
        post.save(update_fields=["views"])

        viewed_posts.append(post.id)
        request.session["viewed_posts"] = viewed_posts

    form = CommentForm()

    if request.method == "POST":

        if request.user.is_authenticated:

            form = CommentForm(request.POST)

            if form.is_valid():

                comment = form.save(commit=False)

                parent = request.POST.get("parent")

                if parent:

                    comment.parent_id = parent

                    comment.user = request.user

                    comment.post = post

                    comment.save()

                return redirect("blog.detail", slug=slug)

                context = {

                    "post": post,

                    "liked": liked,

                    "form": form,

                }

    return render(request,"blog/detail.html",context)
def like_post(request, slug):

    if not request.user.is_authenticated:
        return JsonResponse({
            "error": "Vous devez être connecté."
        }, status=401)

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