from django import forms
from .models import MealPlan, Ingredient, Meal, MealIngredient

class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['day', 'calorie_goal', 'protein_goal', 'carb_goal', 'fat_goal', 'notes']
        widgets = {
            'day': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'calorie_goal': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'protein_goal': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'carb_goal': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'fat_goal': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'description', 'category', 'calories', 'proteins', 'carbs', 'fats', 
                 'fiber', 'sugar', 'sodium', 'allergens', 'serving_size']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'proteins': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'carbs': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'fats': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'fiber': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'sugar': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'sodium': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
            'allergens': forms.Select(attrs={'class': 'form-control'}),
            'serving_size': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'calories': 'Calories (per 100g)',
            'proteins': 'Proteins (g per 100g)',
            'carbs': 'Carbs (g per 100g)',
            'fats': 'Fats (g per 100g)',
        }

class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['name', 'meal_type', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Greek Yogurt Bowl'}),
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any notes about this meal...'}),
        }

class MealIngredientForm(forms.ModelForm):
    class Meta:
        model = MealIngredient
        fields = ['ingredient', 'quantity']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.1', 'step': '0.1'}),
        }

class IngredientSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search ingredients...',
        })
    )
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + Ingredient.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
