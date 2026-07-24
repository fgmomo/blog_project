from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.forms import ProfileEditForm

from blog.models import Category, Post
from comments.models import Comment
from core.models import Advertisement, Partner, TeamMember
from emissions.models import Emission
from newsletter.models import Campaign, Subscriber

from .forms import (
    AdvertisementForm, CampaignForm, CategoryForm, EmissionForm,
    PartnerForm, PostForm, TeamMemberForm,
)
from .mixins import SearchableListMixin, StaffRequiredMixin


@login_required
def dashboard_home(request):

    if request.user.is_staff:

        context = {
            "published_count": Post.objects.filter(status="Published").count(),
            "draft_count": Post.objects.filter(status="Draft").count(),
            "pending_comments_count": Comment.objects.filter(is_approved=False).count(),
            "users_count": User.objects.count(),
            "categories_count": Category.objects.count(),
            "emissions_count": Emission.objects.count(),
        }

        return render(request, "dashboard/home_staff.html", context)

    liked_post_list = Post.objects.filter(likes__user=request.user)

    context = {
        "my_comments": Comment.objects.filter(user=request.user)[:10],
        "liked_post_list": liked_post_list,
        "liked_posts": list(liked_post_list.values_list("id", flat=True)),
    }

    return render(request, "dashboard/home_client.html", context)


@login_required
def profile_settings(request):

    profile = request.user.profile

    if request.method == "POST":

        form = ProfileEditForm(
            request.POST,
            request.FILES,
            instance=profile,
            user=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour.")
            return redirect("dashboard:profile")

    else:
        form = ProfileEditForm(instance=profile, user=request.user)

    context = {
        "form": form,
        "comments_count": Comment.objects.filter(user=request.user).count(),
        "liked_count": Post.objects.filter(likes__user=request.user).count(),
    }

    return render(request, "dashboard/profile.html", context)


# ==================== ARTICLES ====================

class PostListView(StaffRequiredMixin, ListView):
    model = Post
    template_name = "dashboard/post_list.html"
    context_object_name = "posts"
    paginate_by = 15

    def get_queryset(self):
        qs = Post.objects.all().order_by("-created_at")

        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)

        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(title__icontains=search)

        return qs


class PostCreateView(StaffRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "dashboard/post_form.html"
    success_url = reverse_lazy("dashboard:post_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Article créé.")
        return super().form_valid(form)


class PostUpdateView(StaffRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "dashboard/post_form.html"
    success_url = reverse_lazy("dashboard:post_list")

    def form_valid(self, form):
        messages.success(self.request, "Article mis à jour.")
        return super().form_valid(form)


class PostDeleteView(StaffRequiredMixin, DeleteView):
    model = Post
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:post_list")
    extra_context = {"back_url_name": "dashboard:post_list"}

    def form_valid(self, form):
        messages.success(self.request, "Article supprimé.")
        return super().form_valid(form)


# ==================== COMMENTAIRES ====================

@login_required
def comment_moderation_list(request):

    if not request.user.is_staff:
        return redirect("dashboard:home")

    comments = Comment.objects.select_related("post", "user").order_by("-created_at")

    status = request.GET.get("status")
    if status == "pending":
        comments = comments.filter(is_approved=False)
    elif status == "reported":
        comments = comments.filter(reports_count__gt=0)

    paginator = Paginator(comments, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "dashboard/comment_list.html",
        {"comments": page_obj, "status": status}
    )


@login_required
def comment_approve(request, pk):

    if not request.user.is_staff:
        return redirect("dashboard:home")

    comment = get_object_or_404(Comment, pk=pk)
    comment.is_approved = True
    comment.reports_count = 0
    comment.save(update_fields=["is_approved", "reports_count"])

    messages.success(request, "Commentaire approuvé.")
    return redirect("dashboard:comment_list")


@login_required
def comment_delete(request, pk):

    if not request.user.is_staff:
        return redirect("dashboard:home")

    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()

    messages.success(request, "Commentaire supprimé.")
    return redirect("dashboard:comment_list")


# ==================== UTILISATEURS ====================

@login_required
def user_list(request):

    if not request.user.is_staff:
        return redirect("dashboard:home")

    users = User.objects.all().order_by("-date_joined")

    search = request.GET.get("search")
    if search:
        users = users.filter(username__icontains=search)

    paginator = Paginator(users, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "dashboard/user_list.html", {"users": page_obj})


@login_required
def user_toggle_active(request, pk):

    if not request.user.is_staff:
        return redirect("dashboard:home")

    user = get_object_or_404(User, pk=pk)

    if user == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect("dashboard:user_list")

    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])

    messages.success(request, f"Compte {'activé' if user.is_active else 'désactivé'}.")
    return redirect("dashboard:user_list")


# ==================== CRUD SIMPLE (Catégorie / Émission / Équipe / Partenaire) ====================

class CategoryListView(StaffRequiredMixin, SearchableListMixin, ListView):
    model = Category
    template_name = "dashboard/simple_model_list.html"
    context_object_name = "object_list"
    search_field = "name"
    extra_context = {
        "section_title": "Catégories",
        "create_url_name": "dashboard:category_create",
        "edit_url_name": "dashboard:category_update",
        "delete_url_name": "dashboard:category_delete",
    }


class CategoryCreateView(StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "dashboard/simple_model_form.html"
    success_url = reverse_lazy("dashboard:category_list")
    extra_context = {"section_title": "Catégories", "back_url_name": "dashboard:category_list"}


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "dashboard/simple_model_form.html"
    success_url = reverse_lazy("dashboard:category_list")
    extra_context = {"section_title": "Catégories", "back_url_name": "dashboard:category_list"}


class CategoryDeleteView(StaffRequiredMixin, DeleteView):
    model = Category
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:category_list")
    extra_context = {"back_url_name": "dashboard:category_list"}


class EmissionListView(StaffRequiredMixin, SearchableListMixin, ListView):
    model = Emission
    template_name = "dashboard/simple_model_list.html"
    context_object_name = "object_list"
    search_field = "title"
    extra_context = {
        "section_title": "Émissions",
        "create_url_name": "dashboard:emission_create",
        "edit_url_name": "dashboard:emission_update",
        "delete_url_name": "dashboard:emission_delete",
    }


class EmissionCreateView(StaffRequiredMixin, CreateView):
    model = Emission
    form_class = EmissionForm
    template_name = "dashboard/simple_model_form.html"
    success_url = reverse_lazy("dashboard:emission_list")
    extra_context = {"section_title": "Émissions", "back_url_name": "dashboard:emission_list"}


class EmissionUpdateView(StaffRequiredMixin, UpdateView):
    model = Emission
    form_class = EmissionForm
    template_name = "dashboard/simple_model_form.html"
    success_url = reverse_lazy("dashboard:emission_list")
    extra_context = {"section_title": "Émissions", "back_url_name": "dashboard:emission_list"}


class EmissionDeleteView(StaffRequiredMixin, DeleteView):
    model = Emission
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:emission_list")
    extra_context = {"back_url_name": "dashboard:emission_list"}


class TeamMemberListView(StaffRequiredMixin, SearchableListMixin, ListView):
    model = TeamMember
    template_name = "dashboard/simple_model_list.html"
    context_object_name = "object_list"
    search_field = "name"
    extra_context = {
        "section_title": "Équipe",
        "create_url_name": "dashboard:team_create",
        "edit_url_name": "dashboard:team_update",
        "delete_url_name": "dashboard:team_delete",
    }


class TeamMemberCreateView(StaffRequiredMixin, CreateView):
    model = TeamMember
    form_class = TeamMemberForm
    template_name = "dashboard/simple_model_form.html"
    success_url = reverse_lazy("dashboard:team_list")
    extra_context = {"section_title": "Équipe", "back_url_name": "dashboard:team_list"}


class TeamMemberUpdateView(StaffRequiredMixin, UpdateView):
    model = TeamMember
    form_class = TeamMemberForm
    template_name = "dashboard/simple_model_form.html"
    success_url = reverse_lazy("dashboard:team_list")
    extra_context = {"section_title": "Équipe", "back_url_name": "dashboard:team_list"}


class TeamMemberDeleteView(StaffRequiredMixin, DeleteView):
    model = TeamMember
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:team_list")
    extra_context = {"back_url_name": "dashboard:team_list"}


class PartnerListView(StaffRequiredMixin, SearchableListMixin, ListView):
    model = Partner
    template_name = "dashboard/simple_model_list.html"
    context_object_name = "object_list"
    search_field = "name"
    extra_context = {
        "section_title": "Partenaires",
        "create_url_name": "dashboard:partner_create",
        "edit_url_name": "dashboard:partner_update",
        "delete_url_name": "dashboard:partner_delete",
    }


class PartnerCreateView(StaffRequiredMixin, CreateView):
    model = Partner
    form_class = PartnerForm
    template_name = "dashboard/simple_model_form.html"
    success_url = reverse_lazy("dashboard:partner_list")
    extra_context = {"section_title": "Partenaires", "back_url_name": "dashboard:partner_list"}


class PartnerUpdateView(StaffRequiredMixin, UpdateView):
    model = Partner
    form_class = PartnerForm
    template_name = "dashboard/simple_model_form.html"
    success_url = reverse_lazy("dashboard:partner_list")
    extra_context = {"section_title": "Partenaires", "back_url_name": "dashboard:partner_list"}


class PartnerDeleteView(StaffRequiredMixin, DeleteView):
    model = Partner
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:partner_list")
    extra_context = {"back_url_name": "dashboard:partner_list"}


class AdvertisementListView(StaffRequiredMixin, SearchableListMixin, ListView):
    model = Advertisement
    template_name = "dashboard/simple_model_list.html"
    context_object_name = "object_list"
    search_field = "title"
    extra_context = {
        "section_title": "Publicités",
        "create_url_name": "dashboard:ad_create",
        "edit_url_name": "dashboard:ad_update",
        "delete_url_name": "dashboard:ad_delete",
    }


class AdvertisementCreateView(StaffRequiredMixin, CreateView):
    model = Advertisement
    form_class = AdvertisementForm
    template_name = "dashboard/simple_model_form.html"
    success_url = reverse_lazy("dashboard:ad_list")
    extra_context = {"section_title": "Publicités", "back_url_name": "dashboard:ad_list"}


class AdvertisementUpdateView(StaffRequiredMixin, UpdateView):
    model = Advertisement
    form_class = AdvertisementForm
    template_name = "dashboard/simple_model_form.html"
    success_url = reverse_lazy("dashboard:ad_list")
    extra_context = {"section_title": "Publicités", "back_url_name": "dashboard:ad_list"}


class AdvertisementDeleteView(StaffRequiredMixin, DeleteView):
    model = Advertisement
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:ad_list")
    extra_context = {"back_url_name": "dashboard:ad_list"}


# ==================== NEWSLETTER ====================

class SubscriberListView(StaffRequiredMixin, SearchableListMixin, ListView):
    model = Subscriber
    template_name = "dashboard/subscriber_list.html"
    context_object_name = "object_list"
    search_field = "email"


class CampaignListView(StaffRequiredMixin, ListView):
    model = Campaign
    template_name = "dashboard/campaign_list.html"
    context_object_name = "campaigns"
    paginate_by = 15


class CampaignCreateView(StaffRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = "dashboard/campaign_form.html"
    success_url = reverse_lazy("dashboard:campaign_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Campagne créée.")
        return super().form_valid(form)


class CampaignUpdateView(StaffRequiredMixin, UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name = "dashboard/campaign_form.html"
    success_url = reverse_lazy("dashboard:campaign_list")

    def dispatch(self, request, *args, **kwargs):
        campaign = self.get_object()
        if campaign.is_sent:
            messages.error(request, "Une campagne déjà envoyée ne peut plus être modifiée.")
            return redirect("dashboard:campaign_list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Campagne mise à jour.")
        return super().form_valid(form)


class CampaignDeleteView(StaffRequiredMixin, DeleteView):
    model = Campaign
    template_name = "dashboard/confirm_delete.html"
    success_url = reverse_lazy("dashboard:campaign_list")
    extra_context = {"back_url_name": "dashboard:campaign_list"}


@login_required
def campaign_send(request, pk):

    if not request.user.is_staff:
        return redirect("dashboard:home")

    campaign = get_object_or_404(Campaign, pk=pk)

    if campaign.is_sent:
        messages.error(request, "Cette campagne a déjà été envoyée.")
        return redirect("dashboard:campaign_list")

    subscribers = Subscriber.objects.filter(is_active=True)

    for subscriber in subscribers:
        unsubscribe_url = request.build_absolute_uri(
            reverse("newsletter:unsubscribe", args=[subscriber.token])
        )
        html_body = render_to_string(
            "newsletter/campaign_email.html",
            {"campaign": campaign, "unsubscribe_url": unsubscribe_url}
        )
        send_mail(
            subject=campaign.subject,
            message=strip_tags(html_body),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            html_message=html_body,
        )

    campaign.sent_at = timezone.now()
    campaign.save(update_fields=["sent_at"])

    messages.success(request, f"Campagne envoyée à {subscribers.count()} abonné(s).")
    return redirect("dashboard:campaign_list")
