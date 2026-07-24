from django.test import TestCase
from django.urls import reverse

from .models import Emission
from .templatetags.emissions_extras import youtube_embed_url, youtube_thumbnail_url


class EmissionModelTests(TestCase):

    def test_slug_is_auto_generated_from_title(self):
        emission = Emission.objects.create(
            title="Le Débat du Soir",
            description="Une émission de débat.",
        )

        self.assertEqual(emission.slug, "le-debat-du-soir")


class YoutubeEmbedUrlFilterTests(TestCase):

    def test_converts_watch_url(self):
        url = "https://www.youtube.com/watch?v=abc123XYZ"

        self.assertEqual(
            youtube_embed_url(url),
            "https://www.youtube.com/embed/abc123XYZ",
        )

    def test_converts_short_url(self):
        url = "https://youtu.be/abc123XYZ"

        self.assertEqual(
            youtube_embed_url(url),
            "https://www.youtube.com/embed/abc123XYZ",
        )

    def test_converts_vimeo_url(self):
        url = "https://vimeo.com/123456789"

        self.assertEqual(
            youtube_embed_url(url),
            "https://player.vimeo.com/video/123456789",
        )

    def test_returns_none_for_unrecognized_url(self):
        self.assertIsNone(youtube_embed_url("https://example.com/video"))

    def test_returns_none_for_empty_value(self):
        self.assertIsNone(youtube_embed_url(""))


class YoutubeThumbnailUrlFilterTests(TestCase):

    def test_returns_thumbnail_for_watch_url(self):
        url = "https://www.youtube.com/watch?v=abc123XYZ"

        self.assertEqual(
            youtube_thumbnail_url(url),
            "https://i.ytimg.com/vi/abc123XYZ/hqdefault.jpg",
        )

    def test_returns_thumbnail_for_short_url(self):
        url = "https://youtu.be/abc123XYZ"

        self.assertEqual(
            youtube_thumbnail_url(url),
            "https://i.ytimg.com/vi/abc123XYZ/hqdefault.jpg",
        )

    def test_returns_none_for_vimeo(self):
        self.assertIsNone(youtube_thumbnail_url("https://vimeo.com/123456789"))

    def test_returns_none_for_empty_value(self):
        self.assertIsNone(youtube_thumbnail_url(""))


class EmissionViewTests(TestCase):

    def setUp(self):
        self.emission = Emission.objects.create(
            title="Journal du Soir",
            description="Le journal quotidien.",
        )

    def test_index_returns_200(self):
        response = self.client.get(reverse("emissions.index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.emission.title)

    def test_detail_returns_200(self):
        response = self.client.get(
            reverse("emissions.detail", args=[self.emission.slug])
        )

        self.assertEqual(response.status_code, 200)

    def test_detail_404_for_unknown_slug(self):
        response = self.client.get(
            reverse("emissions.detail", args=["inexistant"])
        )

        self.assertEqual(response.status_code, 404)
