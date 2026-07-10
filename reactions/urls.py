from django.urls import path
from . import views

urlpatterns = [

    path('post-like/', views.post_like, name='post.like'),

    path('comment-like/', views.comment_like, name='comment.like'),

]