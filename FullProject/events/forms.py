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
        fields = ['participants']
        widgets = {
            'participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
            })
        }
        labels = {
            'participants': 'Number of Participants'
        }
    
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.event:
            max_participants = min(10, self.event.available_seats)
            self.fields['participants'].widget.attrs['max'] = max_participants
    
    def clean(self):
        cleaned_data = super().clean()
        participants = cleaned_data.get('participants')
        
        if participants and self.event:
            if participants < 1:
                raise forms.ValidationError('Number of participants must be at least 1.')
            
            if participants > self.event.available_seats:
                raise forms.ValidationError(
                    f'Only {self.event.available_seats} spots available for this event.'
                )
        
        return cleaned_data


class BookingUpdateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['participants']
        widgets = {
            'participants': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
            })
        }
        labels = {
            'participants': 'Number of Participants'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.event:
            # For updates, available seats include current booking's participants
            available_seats = self.instance.event.available_seats + self.instance.participants
            max_participants = min(10, available_seats)
            self.fields['participants'].widget.attrs['max'] = max_participants
    
    def clean_participants(self):
        participants = self.cleaned_data.get('participants')
        
        if participants and self.instance and self.instance.event:
            if participants < 1:
                raise forms.ValidationError('Number of participants must be at least 1.')
            
            # Calculate available seats including current booking
            available_seats = self.instance.event.available_seats + self.instance.participants
            
            if participants > available_seats:
                raise forms.ValidationError(
                    f'Only {available_seats} spots available for this event.'
                )
        
        return participants