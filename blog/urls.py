from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="blog.index"),
    path("<slug:slug>/", views.detail, name="blog.detail"),
]