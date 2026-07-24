from django.contrib.sitemaps import Sitemap

from blog.models import Post, Category
from emissions.models import Emission


class PostSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Post.objects.filter(status="Published")

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Category.objects.all()


class EmissionSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Emission.objects.all()

    def lastmod(self, obj):
        return obj.created_at
