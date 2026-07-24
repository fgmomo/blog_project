from django.test import TestCase
from django.urls import reverse

from .models import Subscriber


class SubscribeTests(TestCase):

    def test_subscribe_creates_subscriber(self):
        response = self.client.post(reverse("newsletter:subscribe"), {"email": "test@example.com"})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Subscriber.objects.filter(email="test@example.com", is_active=True).exists())

    def test_subscribe_twice_does_not_duplicate_or_error(self):
        self.client.post(reverse("newsletter:subscribe"), {"email": "test@example.com"})
        response = self.client.post(reverse("newsletter:subscribe"), {"email": "test@example.com"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Subscriber.objects.filter(email="test@example.com").count(), 1)

    def test_subscribe_reactivates_inactive_subscriber(self):
        subscriber = Subscriber.objects.create(email="test@example.com", is_active=False)

        self.client.post(reverse("newsletter:subscribe"), {"email": "test@example.com"})

        subscriber.refresh_from_db()
        self.assertTrue(subscriber.is_active)


class UnsubscribeTests(TestCase):

    def test_unsubscribe_deactivates_subscriber(self):
        subscriber = Subscriber.objects.create(email="test@example.com", is_active=True)

        response = self.client.get(reverse("newsletter:unsubscribe", args=[subscriber.token]))

        subscriber.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(subscriber.is_active)
