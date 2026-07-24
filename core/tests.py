import datetime

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Advertisement, Partner, TeamMember
from .validators import validate_image_extension, validate_image_size

# 1x1 GIF valide, utilisé pour satisfaire la validation Pillow d'ImageField dans les tests.
GIF_1PX = (
    b"GIF87a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00,"
    b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


class ImageValidatorTests(TestCase):

    def test_rejects_disallowed_extension(self):
        file = SimpleUploadedFile("test.exe", b"content")

        with self.assertRaises(ValidationError):
            validate_image_extension(file)

    def test_accepts_allowed_extension(self):
        file = SimpleUploadedFile("test.jpg", b"content")

        validate_image_extension(file)

    def test_rejects_oversized_file(self):
        file = SimpleUploadedFile("test.jpg", b"x" * (6 * 1024 * 1024))

        with self.assertRaises(ValidationError):
            validate_image_size(file)

    def test_accepts_file_under_limit(self):
        file = SimpleUploadedFile("test.jpg", b"x" * 1024)

        validate_image_size(file)


class SEOTests(TestCase):

    def test_sitemap_returns_200(self):
        response = self.client.get(reverse("sitemap"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("xml", response["Content-Type"])

    def test_robots_txt_references_sitemap(self):
        response = self.client.get(reverse("robots_txt"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sitemap:", response.content.decode())


class ErrorPageTests(TestCase):

    def test_404_uses_custom_template(self):
        response = self.client.get("/cette-page-nexiste-pas/")

        self.assertEqual(response.status_code, 404)


class TeamAndPartnerModelTests(TestCase):

    def test_team_members_are_ordered_by_order_field(self):
        TeamMember.objects.create(name="Zoe", role="Redactrice", order=2)
        TeamMember.objects.create(name="Amadou", role="Photographe", order=1)

        names = list(TeamMember.objects.values_list("name", flat=True))
        self.assertEqual(names, ["Amadou", "Zoe"])

    def test_partners_are_ordered_by_order_field(self):
        Partner.objects.create(name="Beta Corp", order=2)
        Partner.objects.create(name="Alpha Corp", order=1)

        names = list(Partner.objects.values_list("name", flat=True))
        self.assertEqual(names, ["Alpha Corp", "Beta Corp"])


class AboutViewTests(TestCase):

    def setUp(self):
        self.member = TeamMember.objects.create(name="Awa Sangare", role="Redactrice en chef")
        self.partner = Partner.objects.create(name="Orange Mali")

    def test_about_page_returns_200_and_lists_team_and_partners(self):
        response = self.client.get(reverse("core.about"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.member.name)
        self.assertContains(response, self.partner.name)


class AdvertisementTests(TestCase):

    def setUp(self):
        today = timezone.localdate()
        self.ad = Advertisement.objects.create(
            title="Bannière Orange Mali",
            image=SimpleUploadedFile("ad.jpg", GIF_1PX, content_type="image/jpeg"),
            link_url="https://orange.ml",
            placement="sidebar",
            start_date=today - datetime.timedelta(days=1),
            end_date=today + datetime.timedelta(days=5),
            is_active=True,
        )

    def test_active_ad_returns_ad_within_window(self):
        from blog.templatetags.blog_extras import active_ad

        self.assertEqual(active_ad("sidebar"), self.ad)

    def test_active_ad_ignores_other_placement(self):
        from blog.templatetags.blog_extras import active_ad

        self.assertIsNone(active_ad("article"))

    def test_active_ad_ignores_inactive_ad(self):
        self.ad.is_active = False
        self.ad.save(update_fields=["is_active"])

        from blog.templatetags.blog_extras import active_ad

        self.assertIsNone(active_ad("sidebar"))

    def test_active_ad_ignores_expired_ad(self):
        self.ad.end_date = timezone.localdate() - datetime.timedelta(days=1)
        self.ad.save(update_fields=["end_date"])

        from blog.templatetags.blog_extras import active_ad

        self.assertIsNone(active_ad("sidebar"))

    def test_ad_click_increments_count_and_redirects(self):
        response = self.client.get(reverse("core.ad_click", args=[self.ad.pk]))

        self.ad.refresh_from_db()
        self.assertEqual(self.ad.clicks_count, 1)
        self.assertRedirects(response, "https://orange.ml", fetch_redirect_response=False)
