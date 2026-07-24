from django.urls import path
from . import views

urlpatterns = [

    path(
        "comment-like/<int:id>/",
        views.comment_like,
        name="comment_like",
    ),

    path(
        "comment-report/<int:id>/",
        views.report_comment,
        name="comment_report",
    ),

]