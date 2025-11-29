# events/admin.py
from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone

from .models import Event, Booking


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location', 'capacity', 'available_seats', 'is_upcoming']
    list_filter = ['date', 'location']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        """
        Override save_model so when an Event's date or location changes,
        we notify all booked users by email.
        """
        # If this is an update (not a create) try to fetch previous values
        previous = None
        if obj.pk:
            try:
                previous = Event.objects.get(pk=obj.pk)
            except Event.DoesNotExist:
                previous = None

        # Save the Event first (so emails link to up-to-date event)
        super().save_model(request, obj, form, change)

        # If previous existed, check if date or location changed
        if previous:
            date_changed = previous.date != obj.date
            location_changed = previous.location != obj.location

            if date_changed or location_changed:
                # Collect recipients (emails) from bookings
                bookings = obj.bookings.select_related('user').all()
                recipients = []
                user_objects = []
                for booking in bookings:
                    user = getattr(booking, 'user', None)
                    if user and getattr(user, 'email', None):
                        recipients.append(user.email)
                        user_objects.append(user)

                # No recipients -> nothing to do
                if not recipients:
                    return

                # Email subject
                subject = f'Update: "{obj.title}" — event details changed'

                # Build context for template
                context = {
                    'event': obj,
                    'previous_date': previous.date,
                    'previous_location': previous.location,
                    'new_date': obj.date,
                    'new_location': obj.location,
                    'site_name': getattr(settings, 'SITE_NAME', 'FitMate'),
                    'admin_user': request.user,
                }

                from django.urls import reverse
                event_url = request.build_absolute_uri(reverse('event-detail', args=[obj.pk]))
                context['event_url'] = event_url


                # Render HTML and plain text alternatives
                html_content = render_to_string('events/emails/event_updated.html', context)
                text_content = strip_tags(html_content)  # simple fallback

                # Send email (to individual recipients BCC to preserve privacy)
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)

                message = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=from_email,
                    to=[from_email],  # To field required by some providers
                    bcc=recipients,
                )
                message.attach_alternative(html_content, "text/html")
                try:
                    message.send(fail_silently=False)
                except Exception:
                    # avoid crashing admin if email fails; admin will get the normal error trace if DEBUG=True
                    # optionally you could log here
                    pass


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'participants', 'booked_at', 'updated_at']
    list_filter = ['booked_at', 'event']
    search_fields = ['user__username', 'event__title']
    readonly_fields = ['booked_at', 'updated_at']
