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
        # Calculate total participants from all active bookings
        total_participants = self.bookings.aggregate(
            total=models.Sum('participants')
        )['total'] or 0
        return self.capacity - total_participants
    
    @property
    def is_available(self):
        return self.available_seats > 0 and self.date > timezone.now()
    
    @property
    def is_upcoming(self):
        return self.date > timezone.now()

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    participants = models.PositiveIntegerField(default=1)
    booked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-booked_at']
        unique_together = ['user', 'event']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.participants} participants)"
    
    def clean(self):
        # Don't validate during deletion
        if not self.pk and hasattr(self, '_deleting'):
            return
            
        if self.event.date <= timezone.now():
            raise ValidationError('Cannot book or modify past events.')
        
        if self.participants < 1:
            raise ValidationError('Number of participants must be at least 1.')
        
        # Calculate available seats excluding current booking if updating
        if self.pk:
            current_booking = Booking.objects.get(pk=self.pk)
            available_seats = self.event.available_seats + current_booking.participants
        else:
            available_seats = self.event.available_seats
            
        if self.participants > available_seats:
            raise ValidationError(
                f'Only {available_seats} spots available for this event.'
            )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)