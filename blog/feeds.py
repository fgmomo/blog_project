from django.contrib.syndication.views import Feed
from django.urls import reverse

from .models import Post


class LatestPostsFeed(Feed):
    title = "OM News — Dernières actualités"
    link = "/blog/"
    description = "Les derniers articles publiés sur OM News."

    def items(self):
        return Post.objects.filter(status="Published").order_by("-created_at")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content

    def item_link(self, item):
        return reverse("blog.detail", args=[item.slug])

    def item_pubdate(self, item):
        return item.created_at

    def item_author_name(self, item):
        return item.author.username
