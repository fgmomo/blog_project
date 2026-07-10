from django.urls import path
from . import views

urlpatterns = [

    path(
        "post/<slug:slug>/",
        views.like_post,
        name="like_post"
    ),

]