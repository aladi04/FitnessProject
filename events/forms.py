from django import forms
from .models import Event, Booking

class EventSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search events...',
            'class': 'form-control'
        })
    )
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Filter by location...',
            'class': 'form-control'
        })
    )

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = []  # No fields needed since we're creating from event
    
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.event and self.user:
            # Check if user already has an active booking for this event
            existing_booking = Booking.objects.filter(
                user=self.user,
                event=self.event,
                is_cancelled=False
            ).exists()
            
            if existing_booking:
                raise forms.ValidationError('You have already booked this event.')
            
            # Check event availability
            if not self.event.is_available:
                raise forms.ValidationError('This event is fully booked.')
            
            # Check if event is in the future
            from django.utils import timezone
            if self.event.date <= timezone.now():
                raise forms.ValidationError('Cannot book past events.')
        
        return cleaned_data
    
    def save(self, commit=True):
        # Create the booking instance with event and user
        booking = Booking.objects.create(
            event=self.event,
            user=self.user
        )
        return booking