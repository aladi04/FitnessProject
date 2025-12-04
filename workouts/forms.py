# forms.py
from django import forms
from .models import Exercise, Workout

# -----------------------------
# Exercise Form
# -----------------------------


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'video_url': forms.URLInput(attrs={'placeholder': 'https://'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Bootstrap form-control class to every field
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # Checkbox/radio and select need different class handling
        if 'category' in self.fields:
            self.fields['category'].widget.attrs.update({'class': 'form-select'})
        if 'difficulty' in self.fields:
            self.fields['difficulty'].widget.attrs.update({'class': 'form-select'})
        if 'target_muscle' in self.fields:
            self.fields['target_muscle'].widget.attrs.update({'class': 'form-select'})


# -----------------------------
# Workout Form
# -----------------------------
class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['name', 'description', 'is_completed', 'exercises']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'exercises': forms.CheckboxSelectMultiple(),  # show checkboxes instead of a multiselect
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # All standard inputs → add bootstrap styling
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': 'form-control'})

        # Style checkbox list container
        self.fields['exercises'].widget.attrs.update({
            'class': 'list-group'
        })
