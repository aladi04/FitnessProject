from django import forms
from .models import MealPlan

class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['day', 'breakfast', 'lunch', 'dinner', 'snacks']
        widgets = {
            'day': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'breakfast': forms.CheckboxSelectMultiple(),
            'lunch': forms.CheckboxSelectMultiple(),
            'dinner': forms.CheckboxSelectMultiple(),
            'snacks': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'day': 'Day',
            'breakfast': 'Breakfast',
            'lunch': 'Lunch',
            'dinner': 'Dinner',
            'snacks': 'Snacks',
        }
        help_texts = {
            'snacks': 'Select multiple snacks if desired.',
        }