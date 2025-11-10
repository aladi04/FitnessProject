from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone 

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date']
    
    def __str__(self):
        return self.title
    
    @property
    def available_seats(self):
        return self.capacity - self.bookings.filter(is_cancelled=False).count()
    
    @property
    def is_available(self):
        return self.available_seats > 0 and self.date > timezone.now()
    
    @property
    def is_upcoming(self):
        return self.date > timezone.now()

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    booked_at = models.DateTimeField(auto_now_add=True)
    is_cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-booked_at']
        unique_together = ['user', 'event','is_cancelled','cancelled_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
    
    def clean(self):
        if not self.event.is_available:
            raise ValidationError('This event is fully booked.')
        if self.event.date <= timezone.now():
            raise ValidationError('Cannot book past events.')
    
    def cancel(self):
        self.is_cancelled = True
        self.cancelled_at = timezone.now()
        self.save()