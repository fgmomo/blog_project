from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django_ratelimit.decorators import ratelimit

from .forms import CommentForm
from .models import Comment


@login_required
@ratelimit(key='user_or_ip', rate='20/m', method='POST', block=True)
def edit_comment(request, id):

    comment = get_object_or_404(Comment, id=id)

    if request.user != comment.user:
        return redirect("blog.detail", slug=comment.post.slug)

    if request.method == "POST":

        original_content = comment.content

        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():

            if form.cleaned_data["content"] != original_content:
                comment.is_edited = True

            form.save()

    return redirect(
        f"{comment.post.get_absolute_url()}#comment-{comment.id}"
    )
