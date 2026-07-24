from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("profil/", views.profile_settings, name="profile"),

    # Articles
    path("articles/", views.PostListView.as_view(), name="post_list"),
    path("articles/nouveau/", views.PostCreateView.as_view(), name="post_create"),
    path("articles/<int:pk>/modifier/", views.PostUpdateView.as_view(), name="post_update"),
    path("articles/<int:pk>/supprimer/", views.PostDeleteView.as_view(), name="post_delete"),

    # Commentaires
    path("commentaires/", views.comment_moderation_list, name="comment_list"),
    path("commentaires/<int:pk>/approuver/", views.comment_approve, name="comment_approve"),
    path("commentaires/<int:pk>/supprimer/", views.comment_delete, name="comment_delete"),

    # Utilisateurs
    path("utilisateurs/", views.user_list, name="user_list"),
    path("utilisateurs/<int:pk>/toggle/", views.user_toggle_active, name="user_toggle_active"),

    # Catégories
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/nouveau/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/modifier/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/supprimer/", views.CategoryDeleteView.as_view(), name="category_delete"),

    # Émissions
    path("emissions/", views.EmissionListView.as_view(), name="emission_list"),
    path("emissions/nouveau/", views.EmissionCreateView.as_view(), name="emission_create"),
    path("emissions/<int:pk>/modifier/", views.EmissionUpdateView.as_view(), name="emission_update"),
    path("emissions/<int:pk>/supprimer/", views.EmissionDeleteView.as_view(), name="emission_delete"),

    # Équipe
    path("equipe/", views.TeamMemberListView.as_view(), name="team_list"),
    path("equipe/nouveau/", views.TeamMemberCreateView.as_view(), name="team_create"),
    path("equipe/<int:pk>/modifier/", views.TeamMemberUpdateView.as_view(), name="team_update"),
    path("equipe/<int:pk>/supprimer/", views.TeamMemberDeleteView.as_view(), name="team_delete"),

    # Partenaires
    path("partenaires/", views.PartnerListView.as_view(), name="partner_list"),
    path("partenaires/nouveau/", views.PartnerCreateView.as_view(), name="partner_create"),
    path("partenaires/<int:pk>/modifier/", views.PartnerUpdateView.as_view(), name="partner_update"),
    path("partenaires/<int:pk>/supprimer/", views.PartnerDeleteView.as_view(), name="partner_delete"),

    # Publicités
    path("publicites/", views.AdvertisementListView.as_view(), name="ad_list"),
    path("publicites/nouveau/", views.AdvertisementCreateView.as_view(), name="ad_create"),
    path("publicites/<int:pk>/modifier/", views.AdvertisementUpdateView.as_view(), name="ad_update"),
    path("publicites/<int:pk>/supprimer/", views.AdvertisementDeleteView.as_view(), name="ad_delete"),

    # Newsletter
    path("newsletter/abonnes/", views.SubscriberListView.as_view(), name="subscriber_list"),
    path("newsletter/campagnes/", views.CampaignListView.as_view(), name="campaign_list"),
    path("newsletter/campagnes/nouveau/", views.CampaignCreateView.as_view(), name="campaign_create"),
    path("newsletter/campagnes/<int:pk>/modifier/", views.CampaignUpdateView.as_view(), name="campaign_update"),
    path("newsletter/campagnes/<int:pk>/supprimer/", views.CampaignDeleteView.as_view(), name="campaign_delete"),
    path("newsletter/campagnes/<int:pk>/envoyer/", views.campaign_send, name="campaign_send"),
]
