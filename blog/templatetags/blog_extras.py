from django import template
from django.utils import timezone

from core.models import Advertisement

register = template.Library()


def _active_ads_queryset(placement):
    today = timezone.localdate()
    return Advertisement.objects.filter(
        placement=placement,
        is_active=True,
        start_date__lte=today,
        end_date__gte=today,
    )


@register.simple_tag
def active_ad(placement):
    return _active_ads_queryset(placement).first()


@register.simple_tag
def active_ads(placement):
    return _active_ads_queryset(placement)


@register.simple_tag(takes_context=True)
def paginate_url(context, page_number):
    """Reconstruit l'URL courante avec ?page=N, en gardant les autres paramètres (search, category...)."""
    request = context["request"]
    params = request.GET.copy()
    params["page"] = page_number
    return "?" + params.urlencode()


@register.filter
def time_since(value):
    if not value:
        return ""

    now = timezone.now()
    diff = now - value

    seconds = diff.total_seconds()

    if seconds < 60:
        return "À l'instant"

    minutes = int(seconds / 60)

    if minutes < 60:
        return f"Il y a {minutes} min"

    hours = int(minutes / 60)

    if hours < 24:
        return f"Il y a {hours} heure(s)"

    days = diff.days

    if days == 1:
        return "Hier"

    return f"Il y a {days} jours"