import json

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from blog.models import Category, Post
from comments.models import Comment

from .models import CommentLike, PostLike


class PostLikeToggleTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user("author", password="pass12345")
        self.liker = User.objects.create_user("liker", password="pass12345")
        category = Category.objects.create(name="Sport")

        self.post = Post.objects.create(
            title="Article",
            content="Contenu",
            status="Published",
            author=self.author,
            category=category,
        )
        self.like_url = reverse("like_post", args=[self.post.slug])

    def test_toggle_like_then_unlike(self):
        self.client.force_login(self.liker)

        response = self.client.post(self.like_url)
        data = json.loads(response.content)
        self.assertTrue(data["liked"])
        self.assertEqual(data["likes"], 1)

        response = self.client.post(self.like_url)
        data = json.loads(response.content)
        self.assertFalse(data["liked"])
        self.assertEqual(data["likes"], 0)

    def test_anonymous_user_gets_401(self):
        response = self.client.post(self.like_url)

        self.assertEqual(response.status_code, 401)

    def test_unique_together_prevents_duplicate_like(self):
        PostLike.objects.create(user=self.liker, post=self.post)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PostLike.objects.create(user=self.liker, post=self.post)


class CommentLikeToggleTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user("author", password="pass12345")
        self.liker = User.objects.create_user("liker", password="pass12345")
        category = Category.objects.create(name="Sport")

        post = Post.objects.create(
            title="Article",
            content="Contenu",
            status="Published",
            author=self.author,
            category=category,
        )
        self.comment = Comment.objects.create(
            post=post, user=self.author, content="Un commentaire"
        )
        self.like_url = reverse("comment_like", args=[self.comment.id])

    def test_toggle_like_then_unlike(self):
        self.client.force_login(self.liker)

        response = self.client.post(self.like_url)
        data = json.loads(response.content)
        self.assertTrue(data["liked"])

        response = self.client.post(self.like_url)
        data = json.loads(response.content)
        self.assertFalse(data["liked"])

    def test_anonymous_user_gets_401_json_not_redirect(self):
        response = self.client.post(self.like_url)

        self.assertEqual(response.status_code, 401)

    def test_unique_together_prevents_duplicate_like(self):
        CommentLike.objects.create(user=self.liker, comment=self.comment)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CommentLike.objects.create(user=self.liker, comment=self.comment)


class ReportCommentTests(TestCase):

    def setUp(self):
        cache.clear()
        self.author = User.objects.create_user("author", password="pass12345")
        category = Category.objects.create(name="Sport")

        post = Post.objects.create(
            title="Article",
            content="Contenu",
            status="Published",
            author=self.author,
            category=category,
        )
        self.comment = Comment.objects.create(
            post=post, user=self.author, content="Un commentaire"
        )
        self.report_url = reverse("comment_report", args=[self.comment.id])

    def test_anonymous_user_gets_401(self):
        response = self.client.post(self.report_url)

        self.assertEqual(response.status_code, 401)

    def test_reports_increment_and_hide_at_threshold(self):
        reporters = [
            User.objects.create_user(f"reporter{i}", password="pass12345")
            for i in range(3)
        ]

        last_data = None

        for reporter in reporters:
            self.client.force_login(reporter)
            response = self.client.post(self.report_url)
            last_data = json.loads(response.content)
            self.client.logout()

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.reports_count, 3)
        self.assertFalse(self.comment.is_approved)
        self.assertTrue(last_data["hidden"])


class RateLimitTests(TestCase):

    def setUp(self):
        cache.clear()
        self.author = User.objects.create_user("author", password="pass12345")
        category = Category.objects.create(name="Sport")

        post = Post.objects.create(
            title="Article",
            content="Contenu",
            status="Published",
            author=self.author,
            category=category,
        )
        self.comment = Comment.objects.create(
            post=post, user=self.author, content="Un commentaire"
        )
        self.report_url = reverse("comment_report", args=[self.comment.id])
        self.client.force_login(self.author)

    def test_exceeding_report_rate_limit_returns_429_not_500(self):
        responses = [self.client.post(self.report_url) for _ in range(11)]

        self.assertEqual(responses[-1].status_code, 429)
