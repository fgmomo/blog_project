from django.urls import path
from . import views

urlpatterns = [
    path("modifier/<int:id>/", views.edit_comment, name="comment.edit"),
]
