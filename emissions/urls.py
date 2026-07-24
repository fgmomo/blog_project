from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="emissions.index"),
    path("<slug:slug>/", views.detail, name="emissions.detail"),
]
