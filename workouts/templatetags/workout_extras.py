from django import template
import re
from urllib.parse import urlparse, parse_qs

register = template.Library()  # ← THIS MUST BE BEFORE ANY @register.filter


@register.filter(name='youtube_embed')
def youtube_embed(value):
    """
    Convert ANY YouTube link to an embeddable URL.
    Supports watch, youtu.be, shorts, embed, live, and mobile links.
    Returns https://www.youtube.com/embed/VIDEO_ID
    """
    if not value:
        return ''

    try:
        url_data = urlparse(value)
    except Exception:
        return ''

    netloc = url_data.netloc.lower()

    # Validate it's a YouTube domain
    if "youtube" not in netloc and "youtu.be" not in netloc:
        return ''

    # Regex to extract the video ID
    pattern = re.compile(
        r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/|live/))'
        r'(?P<id>[\w-]{11})'
    )

    match = pattern.search(value)
    if match:
        video_id = match.group('id')
        return f"https://www.youtube.com/embed/{video_id}"

    # Fallback for watch URLs with multiple parameters
    query = parse_qs(url_data.query)
    video_ids = query.get("v")
    if video_ids:
        video_id = video_ids[0]
        if re.match(r'^[\w-]{11}$', video_id):
            return f"https://www.youtube.com/embed/{video_id}"

    return ''

