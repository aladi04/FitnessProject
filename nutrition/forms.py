# forms.py
from django import forms
from .models import Ingredient, Meal

# -----------------------------
# Ingredient Form
# -----------------------------
class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Bootstrap form-control class to every field
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

        # Select fields styling
        if 'category' in self.fields:
            self.fields['category'].widget.attrs.update({'class': 'form-select'})
        if 'calories' in self.fields:
            self.fields['calories'].widget.attrs.update({'class': 'form-control'})
        if 'protein' in self.fields:
            self.fields['protein'].widget.attrs.update({'class': 'form-control'})


# -----------------------------
# Meal Form
# -----------------------------
class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'ingredients': forms.CheckboxSelectMultiple(),  # show checkboxes instead of multiselect
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Standard inputs → add bootstrap styling
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({'class': 'form-control'})

        # Style checkbox list container
        self.fields['ingredients'].widget.attrs.update({
            'class': 'list-group'
        })
