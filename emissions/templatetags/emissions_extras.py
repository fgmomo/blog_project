from urllib.parse import urlparse, parse_qs

from django import template

register = template.Library()


def _youtube_video_id(url):
    if not url:
        return None

    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")

    if host in ("youtube.com", "m.youtube.com") and parsed.path == "/watch":
        return parse_qs(parsed.query).get("v", [None])[0]

    if host == "youtu.be":
        return parsed.path.lstrip("/") or None

    return None


@register.filter
def youtube_embed_url(url):
    """Convertit une URL YouTube/Vimeo classique en URL embarquable.

    Renvoie None si l'URL n'est pas reconnue, pour laisser le template
    afficher un simple lien "Regarder le replay" en secours.
    """
    if not url:
        return None

    video_id = _youtube_video_id(url)
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}"

    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")

    if host == "vimeo.com":
        video_id = parsed.path.lstrip("/")
        if video_id.isdigit():
            return f"https://player.vimeo.com/video/{video_id}"

    return None


@register.filter
def youtube_thumbnail_url(url):
    """Renvoie la miniature YouTube de la vidéo, ou None si non reconnue."""
    video_id = _youtube_video_id(url)

    if video_id:
        return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

    return None
