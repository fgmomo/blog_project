import datetime

from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Category, Post
from comments.models import Comment
from core.models import Advertisement
from newsletter.models import Campaign, Subscriber
from reactions.models import PostLike

# 1x1 GIF valide, utilisé pour satisfaire la validation Pillow d'ImageField dans les tests.
GIF_1PX = (
    b"GIF87a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00,"
    b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class DashboardPermissionTests(TestCase):

    def setUp(self):
        self.staff = User.objects.create_user("staff", password="pass12345", is_staff=True)
        self.client_user = User.objects.create_user("client", password="pass12345")

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_non_staff_cannot_access_post_list(self):
        self.client.force_login(self.client_user)

        response = self.client.get(reverse("dashboard:post_list"))

        self.assertEqual(response.status_code, 403)

    def test_non_staff_cannot_access_category_list(self):
        self.client.force_login(self.client_user)

        response = self.client.get(reverse("dashboard:category_list"))

        self.assertEqual(response.status_code, 403)

    def test_non_staff_cannot_access_user_list(self):
        self.client.force_login(self.client_user)

        response = self.client.get(reverse("dashboard:user_list"))

        self.assertRedirects(response, reverse("dashboard:home"))

    def test_staff_can_access_post_list(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("dashboard:post_list"))

        self.assertEqual(response.status_code, 200)

    def test_home_renders_staff_template_for_staff(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("dashboard:home"))

        self.assertTemplateUsed(response, "dashboard/home_staff.html")

    def test_home_renders_client_template_for_regular_user(self):
        self.client.force_login(self.client_user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertTemplateUsed(response, "dashboard/home_client.html")


class PostCRUDTests(TestCase):

    def setUp(self):
        self.staff = User.objects.create_user("staff", password="pass12345", is_staff=True)
        self.category = Category.objects.create(name="Sport")
        self.client.force_login(self.staff)

    def test_create_post_assigns_current_user_as_author(self):
        response = self.client.post(reverse("dashboard:post_create"), {
            "title": "Nouvel article",
            "content": "Contenu de test",
            "category": self.category.id,
            "status": "Draft",
        })

        post = Post.objects.get(title="Nouvel article")
        self.assertEqual(post.author, self.staff)
        self.assertRedirects(response, reverse("dashboard:post_list"))

    def test_update_post(self):
        post = Post.objects.create(
            title="Ancien titre", content="Contenu", author=self.staff, category=self.category
        )

        self.client.post(reverse("dashboard:post_update", args=[post.pk]), {
            "title": "Nouveau titre",
            "content": "Contenu",
            "category": self.category.id,
            "status": "Published",
        })

        post.refresh_from_db()
        self.assertEqual(post.title, "Nouveau titre")
        self.assertEqual(post.status, "Published")

    def test_delete_post(self):
        post = Post.objects.create(
            title="À supprimer", content="Contenu", author=self.staff, category=self.category
        )

        self.client.post(reverse("dashboard:post_delete", args=[post.pk]))

        self.assertFalse(Post.objects.filter(pk=post.pk).exists())


class CategoryCRUDTests(TestCase):
    """Représentatif du pattern générique partagé (Émission/Équipe/Partenaire suivent le même schéma)."""

    def setUp(self):
        self.staff = User.objects.create_user("staff", password="pass12345", is_staff=True)
        self.client.force_login(self.staff)

    def test_create_category(self):
        response = self.client.post(reverse("dashboard:category_create"), {
            "name": "Culture",
            "description": "Articles culturels",
        })

        self.assertTrue(Category.objects.filter(name="Culture").exists())
        self.assertRedirects(response, reverse("dashboard:category_list"))

    def test_update_category(self):
        category = Category.objects.create(name="Ancien nom")

        self.client.post(reverse("dashboard:category_update", args=[category.pk]), {
            "name": "Nouveau nom",
            "description": "",
        })

        category.refresh_from_db()
        self.assertEqual(category.name, "Nouveau nom")

    def test_delete_category(self):
        category = Category.objects.create(name="À supprimer")

        self.client.post(reverse("dashboard:category_delete", args=[category.pk]))

        self.assertFalse(Category.objects.filter(pk=category.pk).exists())


class CommentModerationTests(TestCase):

    def setUp(self):
        self.staff = User.objects.create_user("staff", password="pass12345", is_staff=True)
        self.author = User.objects.create_user("author", password="pass12345")
        category = Category.objects.create(name="Sport")
        post = Post.objects.create(
            title="Article", content="Contenu", status="Published",
            author=self.author, category=category,
        )
        self.comment = Comment.objects.create(
            post=post, user=self.author, content="Un commentaire",
            is_approved=False, reports_count=3,
        )
        self.client.force_login(self.staff)

    def test_approve_comment(self):
        self.client.get(reverse("dashboard:comment_approve", args=[self.comment.pk]))

        self.comment.refresh_from_db()
        self.assertTrue(self.comment.is_approved)
        self.assertEqual(self.comment.reports_count, 0)

    def test_delete_comment(self):
        self.client.get(reverse("dashboard:comment_delete", args=[self.comment.pk]))

        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())


class UserManagementTests(TestCase):

    def setUp(self):
        self.staff = User.objects.create_user("staff", password="pass12345", is_staff=True)
        self.member = User.objects.create_user("member", password="pass12345")
        self.client.force_login(self.staff)

    def test_toggle_active_deactivates_user(self):
        self.client.get(reverse("dashboard:user_toggle_active", args=[self.member.pk]))

        self.member.refresh_from_db()
        self.assertFalse(self.member.is_active)

    def test_staff_cannot_deactivate_self(self):
        self.client.get(reverse("dashboard:user_toggle_active", args=[self.staff.pk]))

        self.staff.refresh_from_db()
        self.assertTrue(self.staff.is_active)


class ClientDashboardTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("client", password="pass12345")
        self.other_user = User.objects.create_user("other", password="pass12345")
        author = User.objects.create_user("author", password="pass12345")
        category = Category.objects.create(name="Sport")

        self.post = Post.objects.create(
            title="Article aime", content="Contenu", status="Published",
            author=author, category=category,
        )
        PostLike.objects.create(user=self.user, post=self.post)

        Comment.objects.create(post=self.post, user=self.user, content="Mon commentaire")
        Comment.objects.create(post=self.post, user=self.other_user, content="Commentaire d'un autre")

        self.client.force_login(self.user)

    def test_dashboard_shows_only_own_comments(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertContains(response, "Mon commentaire")
        self.assertNotContains(response, "Commentaire d'un autre")

    def test_dashboard_shows_liked_posts(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertContains(response, self.post.title)


class ProfileSettingsTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            "kevin", email="kevin@example.com", password="pass12345"
        )

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(reverse("dashboard:profile"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_authenticated_user_can_update_email(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("dashboard:profile"), {
            "email": "kevin-nouveau@example.com",
        })

        self.assertRedirects(response, reverse("dashboard:profile"))

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "kevin-nouveau@example.com")


class AdvertisementCRUDTests(TestCase):

    def setUp(self):
        self.staff = User.objects.create_user("staff", password="pass12345", is_staff=True)
        self.client.force_login(self.staff)
        self.today = timezone.localdate()

    def test_non_staff_cannot_access_ad_list(self):
        client_user = User.objects.create_user("client", password="pass12345")
        self.client.force_login(client_user)

        response = self.client.get(reverse("dashboard:ad_list"))

        self.assertEqual(response.status_code, 403)

    def test_create_advertisement(self):
        response = self.client.post(reverse("dashboard:ad_create"), {
            "title": "Bannière Orange Mali",
            "image": SimpleUploadedFile("ad.jpg", GIF_1PX, content_type="image/jpeg"),
            "link_url": "https://orange.ml",
            "placement": "sidebar",
            "start_date": self.today,
            "end_date": self.today + datetime.timedelta(days=30),
            "is_active": True,
        })

        self.assertTrue(Advertisement.objects.filter(title="Bannière Orange Mali").exists())
        self.assertRedirects(response, reverse("dashboard:ad_list"))

    def test_update_advertisement(self):
        ad = Advertisement.objects.create(
            title="Ancienne pub",
            image=SimpleUploadedFile("ad.jpg", GIF_1PX, content_type="image/jpeg"),
            link_url="https://example.com",
            placement="sidebar",
            start_date=self.today,
            end_date=self.today + datetime.timedelta(days=30),
        )

        self.client.post(reverse("dashboard:ad_update", args=[ad.pk]), {
            "title": "Nouvelle pub",
            "link_url": "https://example.com",
            "placement": "article",
            "start_date": self.today,
            "end_date": self.today + datetime.timedelta(days=30),
            "is_active": True,
        })

        ad.refresh_from_db()
        self.assertEqual(ad.title, "Nouvelle pub")
        self.assertEqual(ad.placement, "article")

    def test_delete_advertisement(self):
        ad = Advertisement.objects.create(
            title="À supprimer",
            image=SimpleUploadedFile("ad.jpg", GIF_1PX, content_type="image/jpeg"),
            link_url="https://example.com",
            placement="sidebar",
            start_date=self.today,
            end_date=self.today + datetime.timedelta(days=30),
        )

        self.client.post(reverse("dashboard:ad_delete", args=[ad.pk]))

        self.assertFalse(Advertisement.objects.filter(pk=ad.pk).exists())


class NewsletterDashboardTests(TestCase):

    def setUp(self):
        self.staff = User.objects.create_user("staff", password="pass12345", is_staff=True)
        self.client.force_login(self.staff)

    def test_non_staff_cannot_access_subscriber_list(self):
        client_user = User.objects.create_user("client", password="pass12345")
        self.client.force_login(client_user)

        response = self.client.get(reverse("dashboard:subscriber_list"))

        self.assertEqual(response.status_code, 403)

    def test_subscriber_list_shows_subscribers(self):
        Subscriber.objects.create(email="lecteur@example.com")

        response = self.client.get(reverse("dashboard:subscriber_list"))

        self.assertContains(response, "lecteur@example.com")

    def test_create_campaign_assigns_current_user(self):
        response = self.client.post(reverse("dashboard:campaign_create"), {
            "subject": "Actus de la semaine",
            "body": "Contenu de la campagne",
        })

        campaign = Campaign.objects.get(subject="Actus de la semaine")
        self.assertEqual(campaign.created_by, self.staff)
        self.assertRedirects(response, reverse("dashboard:campaign_list"))

    def test_send_campaign_emails_only_active_subscribers(self):
        Subscriber.objects.create(email="actif@example.com", is_active=True)
        Subscriber.objects.create(email="inactif@example.com", is_active=False)
        campaign = Campaign.objects.create(subject="Newsletter", body="Bonjour", created_by=self.staff)

        response = self.client.post(reverse("dashboard:campaign_send", args=[campaign.pk]))

        campaign.refresh_from_db()
        self.assertIsNotNone(campaign.sent_at)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["actif@example.com"])
        self.assertRedirects(response, reverse("dashboard:campaign_list"))

    def test_sent_campaign_cannot_be_updated(self):
        campaign = Campaign.objects.create(
            subject="Déjà envoyée", body="Contenu",
            created_by=self.staff, sent_at=timezone.now(),
        )

        response = self.client.post(reverse("dashboard:campaign_update", args=[campaign.pk]), {
            "subject": "Modifiée",
            "body": "Contenu modifié",
        })

        campaign.refresh_from_db()
        self.assertEqual(campaign.subject, "Déjà envoyée")
        self.assertRedirects(response, reverse("dashboard:campaign_list"))
