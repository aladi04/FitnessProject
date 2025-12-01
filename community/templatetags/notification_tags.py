from django import template
from community.models import Notification

register = template.Library()

@register.simple_tag
def unread_notifications_count(user):
    if user.is_authenticated:
        return Notification.objects.filter(recipient=user, is_read=False).count()
    return 0

