from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from blog.models import Category, Post

from .models import Comment


class CommentPostingTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user("author", password="pass12345")
        self.commenter = User.objects.create_user("commenter", password="pass12345")
        category = Category.objects.create(name="Sport")

        self.post = Post.objects.create(
            title="Article",
            content="Contenu",
            status="Published",
            author=self.author,
            category=category,
        )
        self.detail_url = reverse("blog.detail", args=[self.post.slug])

    def test_authenticated_user_can_post_root_comment(self):
        self.client.force_login(self.commenter)

        self.client.post(self.detail_url, {"content": "Bel article !"})

        comment = Comment.objects.get()
        self.assertEqual(comment.content, "Bel article !")
        self.assertEqual(comment.user, self.commenter)
        self.assertIsNone(comment.parent)

    def test_authenticated_user_can_reply_to_a_comment(self):
        root = Comment.objects.create(
            post=self.post, user=self.author, content="Premier commentaire"
        )

        self.client.force_login(self.commenter)
        self.client.post(
            self.detail_url,
            {"content": "Je suis d'accord", "parent": root.id},
        )

        reply = Comment.objects.exclude(id=root.id).get()
        self.assertEqual(reply.parent, root)
        self.assertIn(reply, root.replies.all())

    def test_anonymous_user_cannot_post_comment(self):
        self.client.post(self.detail_url, {"content": "Spam"})

        self.assertEqual(Comment.objects.count(), 0)


class CommentEditTests(TestCase):

    def setUp(self):
        cache.clear()

        self.author = User.objects.create_user("author", password="pass12345")
        self.owner = User.objects.create_user("owner", password="pass12345")
        self.other = User.objects.create_user("other", password="pass12345")
        category = Category.objects.create(name="Sport")

        post = Post.objects.create(
            title="Article",
            content="Contenu",
            status="Published",
            author=self.author,
            category=category,
        )
        self.comment = Comment.objects.create(
            post=post, user=self.owner, content="Contenu original"
        )
        self.edit_url = reverse("comment.edit", args=[self.comment.id])

    def test_owner_can_edit_their_comment(self):
        self.client.force_login(self.owner)

        self.client.post(self.edit_url, {"content": "Contenu modifie"})

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "Contenu modifie")
        self.assertTrue(self.comment.is_edited)

    def test_editing_with_same_content_does_not_mark_as_edited(self):
        self.client.force_login(self.owner)

        self.client.post(self.edit_url, {"content": "Contenu original"})

        self.comment.refresh_from_db()
        self.assertFalse(self.comment.is_edited)

    def test_other_user_cannot_edit_comment(self):
        self.client.force_login(self.other)

        self.client.post(self.edit_url, {"content": "Piratage"})

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "Contenu original")
        self.assertFalse(self.comment.is_edited)

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
