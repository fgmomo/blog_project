from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('services/', views.services, name='core.services'),

    path('mentions-legales/', views.legal_notice, name='core.legal_notice'),
    path('confidentialite/', views.privacy_policy, name='core.privacy_policy'),
    path('cgu/', views.terms, name='core.terms'),
    path('a-propos/', views.about, name='core.about'),

    path('pub/<int:pk>/clic/', views.ad_click, name='core.ad_click'),

]