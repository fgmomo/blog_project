from blog.models import Category, Post
from comments.models import Comment
from core.models import Advertisement, Partner, TeamMember
from django.contrib.auth.models import User
from emissions.models import Emission
from newsletter.models import Subscriber


def sidebar_counts(request):
    if not request.path.startswith("/dashboard/"):
        return {}

    if not request.user.is_authenticated or not request.user.is_staff:
        return {}

    return {
        "sidebar_posts_count": Post.objects.count(),
        "sidebar_pending_comments_count": Comment.objects.filter(is_approved=False).count(),
        "sidebar_reported_comments_count": Comment.objects.filter(reports_count__gt=0).count(),
        "sidebar_users_count": User.objects.count(),
        "sidebar_categories_count": Category.objects.count(),
        "sidebar_emissions_count": Emission.objects.count(),
        "sidebar_team_count": TeamMember.objects.count(),
        "sidebar_partners_count": Partner.objects.count(),
        "sidebar_ads_count": Advertisement.objects.filter(is_active=True).count(),
        "sidebar_subscribers_count": Subscriber.objects.filter(is_active=True).count(),
    }
