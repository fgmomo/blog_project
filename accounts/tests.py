from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .forms import SignUpForm
from .models import Profile


class ProfileSignalTests(TestCase):

    def test_profile_is_created_when_user_is_created(self):
        user = User.objects.create_user("alice", password="pass12345")

        self.assertTrue(Profile.objects.filter(user=user).exists())


class SignUpFormTests(TestCase):

    def test_rejects_duplicate_email(self):
        User.objects.create_user(
            "bob", email="bob@example.com", password="pass12345"
        )

        form = SignUpForm(data={
            "username": "bob2",
            "email": "bob@example.com",
            "password1": "SuperSecret123",
            "password2": "SuperSecret123",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_accepts_unique_email(self):
        form = SignUpForm(data={
            "username": "carol",
            "email": "carol@example.com",
            "password1": "SuperSecret123",
            "password2": "SuperSecret123",
        })

        self.assertTrue(form.is_valid())


class AuthViewTests(TestCase):

    def setUp(self):
        cache.clear()

    def test_login_success_redirects_home(self):
        User.objects.create_user("dave", password="pass12345")

        response = self.client.post(reverse("login"), {
            "username": "dave",
            "password": "pass12345",
        })

        self.assertRedirects(response, reverse("home"))

    def test_login_failure_shows_error(self):
        response = self.client.post(reverse("login"), {
            "username": "unknown",
            "password": "wrong",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "incorrect")

    def test_logout_redirects_home(self):
        user = User.objects.create_user("erin", password="pass12345")
        self.client.force_login(user)

        response = self.client.get(reverse("logout"))

        self.assertRedirects(response, reverse("home"))

    def test_login_rate_limit_returns_403_not_500(self):
        responses = [
            self.client.post(reverse("login"), {
                "username": "unknown",
                "password": "wrong",
            })
            for _ in range(11)
        ]

        self.assertEqual(responses[-1].status_code, 403)


class EmailVerificationTests(TestCase):

    def setUp(self):
        cache.clear()

    def test_signup_creates_inactive_user_and_sends_email(self):
        response = self.client.post(reverse("signup"), {
            "username": "frank",
            "email": "frank@example.com",
            "password1": "SuperSecret123",
            "password2": "SuperSecret123",
        })

        self.assertEqual(response.status_code, 200)

        user = User.objects.get(username="frank")
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("frank@example.com", mail.outbox[0].to)

    def test_cannot_login_before_verification(self):
        self.client.post(reverse("signup"), {
            "username": "gina",
            "email": "gina@example.com",
            "password1": "SuperSecret123",
            "password2": "SuperSecret123",
        })

        response = self.client.post(reverse("login"), {
            "username": "gina",
            "password": "SuperSecret123",
        })

        self.assertContains(response, "activé")

    def test_verify_email_activates_account(self):
        self.client.post(reverse("signup"), {
            "username": "henry",
            "email": "henry@example.com",
            "password1": "SuperSecret123",
            "password2": "SuperSecret123",
        })

        user = User.objects.get(username="henry")
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(
            reverse("verify_email", args=[uid, token])
        )

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertContains(response, "activé")

    def test_verify_email_with_invalid_token_fails(self):
        user = User.objects.create_user(
            "iris", email="iris@example.com", password="pass12345", is_active=False
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        response = self.client.get(
            reverse("verify_email", args=[uid, "token-invalide"])
        )

        user.refresh_from_db()
        self.assertFalse(user.is_active)
        self.assertContains(response, "invalide")


class PasswordResetTests(TestCase):

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            "jade", email="jade@example.com", password="OldPassword123"
        )

    def test_password_reset_sends_email(self):
        response = self.client.post(
            reverse("password_reset"), {"email": "jade@example.com"}
        )

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)

    def test_full_reset_flow_changes_password(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        confirm_url = reverse(
            "password_reset_confirm", args=[uid, token]
        )

        # Django échange le token contre un token de session à la première visite
        session_response = self.client.get(confirm_url, follow=True)
        self.assertEqual(session_response.status_code, 200)

        final_url = session_response.redirect_chain[-1][0]

        response = self.client.post(final_url, {
            "new_password1": "NewPassword456",
            "new_password2": "NewPassword456",
        })

        self.assertRedirects(response, reverse("password_reset_complete"))

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword456"))


class ProfileEditRedirectTests(TestCase):
    """La page profil vit maintenant dans le dashboard ; cette URL ne fait plus que rediriger."""

    def test_profile_edit_redirects_to_dashboard_profile(self):
        user = User.objects.create_user("kevin", password="pass12345")
        self.client.force_login(user)

        response = self.client.get(reverse("profile_edit"))

        self.assertRedirects(response, reverse("dashboard:profile"))
