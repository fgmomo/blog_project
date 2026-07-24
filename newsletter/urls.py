from django.urls import path

from . import views

app_name = "newsletter"

urlpatterns = [
    path("inscription/", views.subscribe, name="subscribe"),
    path("desabonnement/<uuid:token>/", views.unsubscribe, name="unsubscribe"),
]
