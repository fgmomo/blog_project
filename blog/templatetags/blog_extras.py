from django import template
from django.utils import timezone

register = template.Library()


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