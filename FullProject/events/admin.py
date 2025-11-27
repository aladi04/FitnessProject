from django.contrib import admin
from .models import Event, Booking

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location', 'capacity', 'available_seats', 'is_upcoming']
    list_filter = ['date', 'location']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'participants', 'booked_at', 'updated_at']
    list_filter = ['booked_at', 'event']
    search_fields = ['user__username', 'event__title']
    readonly_fields = ['booked_at', 'updated_at']