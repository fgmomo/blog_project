from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from comments.models import Comment

from .models import Category, Post


class PostModelTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user("author", password="pass12345")
        self.category = Category.objects.create(name="Sport")

    def test_slug_is_auto_generated_from_title(self):
        post = Post.objects.create(
            title="Mon Premier Article",
            content="Contenu",
            author=self.author,
            category=self.category,
        )
        self.assertEqual(post.slug, "mon-premier-article")

    def test_slug_is_not_overwritten_if_provided(self):
        post = Post.objects.create(
            title="Un Article",
            slug="custom-slug",
            content="Contenu",
            author=self.author,
            category=self.category,
        )
        self.assertEqual(post.slug, "custom-slug")


class BlogIndexViewTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user("author", password="pass12345")
        self.cat_sport = Category.objects.create(name="Sport")
        self.cat_tech = Category.objects.create(name="Tech")

        self.published = Post.objects.create(
            title="Article publié",
            content="Contenu",
            status="Published",
            author=self.author,
            category=self.cat_sport,
        )
        self.draft = Post.objects.create(
            title="Article brouillon",
            content="Contenu",
            status="Draft",
            author=self.author,
            category=self.cat_sport,
        )

    def test_index_only_shows_published_posts(self):
        response = self.client.get(reverse("blog.index"))

        self.assertContains(response, self.published.title)
        self.assertNotContains(response, self.draft.title)

    def test_index_search_filters_by_title(self):
        response = self.client.get(reverse("blog.index"), {"search": "publié"})

        self.assertIn(self.published, response.context["posts"])

        response = self.client.get(reverse("blog.index"), {"search": "inexistant"})

        self.assertNotIn(self.published, response.context["posts"])

    def test_index_category_filter(self):
        tech_post = Post.objects.create(
            title="Article tech",
            content="Contenu",
            status="Published",
            author=self.author,
            category=self.cat_tech,
        )

        response = self.client.get(
            reverse("blog.index"), {"category": self.cat_sport.id}
        )

        self.assertIn(self.published, response.context["posts"])
        self.assertNotIn(tech_post, response.context["posts"])


class BlogDetailViewTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user("author", password="pass12345")
        self.category = Category.objects.create(name="Sport")

        self.published = Post.objects.create(
            title="Article publié",
            content="Contenu",
            status="Published",
            author=self.author,
            category=self.category,
        )
        self.draft = Post.objects.create(
            title="Article brouillon",
            content="Contenu",
            status="Draft",
            author=self.author,
            category=self.category,
        )

    def test_detail_returns_404_for_draft(self):
        response = self.client.get(
            reverse("blog.detail", args=[self.draft.slug])
        )

        self.assertEqual(response.status_code, 404)

    def test_view_count_increments_once_per_session(self):
        url = reverse("blog.detail", args=[self.published.slug])

        self.client.get(url)
        self.client.get(url)

        self.published.refresh_from_db()
        self.assertEqual(self.published.views, 1)


class CategoryModelTests(TestCase):

    def test_slug_is_auto_generated_from_name(self):
        category = Category.objects.create(name="Économie Locale")

        self.assertEqual(category.slug, "economie-locale")


class CategoryDetailViewTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user("author", password="pass12345")
        self.cat_sport = Category.objects.create(name="Sport")
        self.cat_tech = Category.objects.create(name="Tech")

        self.sport_post = Post.objects.create(
            title="Match du week-end",
            content="Contenu",
            status="Published",
            author=self.author,
            category=self.cat_sport,
        )
        self.tech_post = Post.objects.create(
            title="Nouveau smartphone",
            content="Contenu",
            status="Published",
            author=self.author,
            category=self.cat_tech,
        )

    def test_category_detail_only_shows_its_own_posts(self):
        response = self.client.get(
            reverse("blog.category_detail", args=[self.cat_sport.slug])
        )

        self.assertContains(response, self.sport_post.title)
        self.assertNotContains(response, self.tech_post.title)

    def test_category_detail_404_for_unknown_slug(self):
        response = self.client.get(
            reverse("blog.category_detail", args=["inexistant"])
        )

        self.assertEqual(response.status_code, 404)

    def test_categories_index_lists_all_categories(self):
        response = self.client.get(reverse("blog.categories"))

        self.assertContains(response, "Sport")
        self.assertContains(response, "Tech")


class AuthorDetailViewTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user("author", password="pass12345")
        self.other_author = User.objects.create_user("other", password="pass12345")
        category = Category.objects.create(name="Sport")

        self.post = Post.objects.create(
            title="Article principal",
            content="Contenu",
            status="Published",
            author=self.author,
            category=category,
        )
        self.other_post = Post.objects.create(
            title="Article secondaire",
            content="Contenu",
            status="Published",
            author=self.other_author,
            category=category,
        )

    def test_author_detail_only_shows_their_own_posts(self):
        response = self.client.get(
            reverse("blog.author_detail", args=[self.author.username])
        )

        self.assertContains(response, self.post.title)
        self.assertNotContains(response, self.other_post.title)

    def test_author_detail_404_for_unknown_username(self):
        response = self.client.get(
            reverse("blog.author_detail", args=["inconnu"])
        )

        self.assertEqual(response.status_code, 404)


class BlogPaginationTests(TestCase):

    def setUp(self):
        author = User.objects.create_user("author", password="pass12345")
        category = Category.objects.create(name="Sport")

        for i in range(15):
            Post.objects.create(
                title=f"Article {i}",
                content="Contenu",
                status="Published",
                author=author,
                category=category,
            )

    def test_first_page_has_9_posts(self):
        response = self.client.get(reverse("blog.index"))

        self.assertEqual(len(response.context["posts"]), 9)

    def test_second_page_has_remaining_posts(self):
        response = self.client.get(reverse("blog.index"), {"page": 2})

        self.assertEqual(len(response.context["posts"]), 6)

    def test_per_page_param_changes_page_size(self):
        response = self.client.get(reverse("blog.index"), {"per_page": 15})

        self.assertEqual(len(response.context["posts"]), 15)

    def test_invalid_per_page_falls_back_to_default(self):
        response = self.client.get(reverse("blog.index"), {"per_page": 999})

        self.assertEqual(len(response.context["posts"]), 9)

    def test_out_of_range_page_does_not_crash(self):
        response = self.client.get(reverse("blog.index"), {"page": 999})

        self.assertEqual(response.status_code, 200)


class CommentModerationDisplayTests(TestCase):

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

        Comment.objects.create(
            post=self.post,
            user=self.commenter,
            content="Commentaire visible",
            is_approved=True,
        )
        Comment.objects.create(
            post=self.post,
            user=self.commenter,
            content="Commentaire masque",
            is_approved=False,
        )

    def test_only_approved_comments_are_shown(self):
        response = self.client.get(
            reverse("blog.detail", args=[self.post.slug])
        )

        self.assertContains(response, "Commentaire visible")
        self.assertNotContains(response, "Commentaire masque")


class FeedTests(TestCase):

    def test_feed_returns_200_with_rss_content_type(self):
        response = self.client.get(reverse("blog.feed"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("rss", response["Content-Type"])


class ShareButtonsTests(TestCase):

    def setUp(self):
        author = User.objects.create_user("author", password="pass12345")
        category = Category.objects.create(name="Sport")

        self.post = Post.objects.create(
            title="Article a partager",
            content="Contenu",
            status="Published",
            author=author,
            category=category,
        )

    def test_detail_page_contains_share_links(self):
        response = self.client.get(
            reverse("blog.detail", args=[self.post.slug])
        )

        content = response.content.decode()

        self.assertIn("wa.me", content)
        self.assertIn("facebook.com/sharer", content)
        self.assertIn(self.post.slug, content)
        self.assertIn("copy-link-btn", content)
