from django.urls import path
from . import views
from .feeds import LatestPostsFeed

urlpatterns = [
    path("", views.index, name="blog.index"),
    path("feed/", LatestPostsFeed(), name="blog.feed"),
    path("categories/", views.categories_index, name="blog.categories"),
    path("categorie/<slug:slug>/", views.category_detail, name="blog.category_detail"),
    path("auteur/<str:username>/", views.author_detail, name="blog.author_detail"),
    path("like/<slug:slug>/",views.like_post,name="like_post"),
    path("<slug:slug>/", views.detail, name="blog.detail"),
]