from django.db import models

# Create your models here.
from django.db import models
from django.core.exceptions import ValidationError


CATEGORY_CHOICES = [
    
    ('fruits', 'Fruits'),
    ('vegetables', 'Vegetables'),
    ('grains', 'Grains & Cereals'),
    ('dairy', 'Dairy & Alternatives'),
    ('meat', 'Meat & Poultry'),
    ('seafood', 'Seafood'),
    ('legumes', 'Legumes & Beans'),
    ('nuts_seeds', 'Nuts & Seeds'),
    ('oils_fats', 'Oils & Fats'),
    ('beverages', 'Beverages'),
    ('snacks', 'Snacks & Sweets'),
    ('condiments', 'Condiments & Spices'),
    ('breakfast', 'Breakfast Foods'),
    ('processed', 'Processed / Fast Foods'),
    ('supplements', 'Supplements & Powders'),
]

MEAL_TYPE_CHOICES = [
    ('breakfast', 'Breakfast'),
    ('lunch', 'Lunch'),
    ('dinner', 'Dinner'),
    ('snack', 'Snack'),
]


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    description = models.TextField(blank=True, null=True)
    calories = models.IntegerField(default=0)
    protein = models.FloatField(default=0.0)
    carbs = models.FloatField(default=0.0)
    fat = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Meal(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    is_favorite = models.BooleanField(default=False)

    ingredients = models.ManyToManyField(Ingredient, related_name="meals")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def total_calories(self):
        return sum(ingredient.calories for ingredient in self.ingredients.all())

    def total_protein(self):
        return sum(ingredient.protein for ingredient in self.ingredients.all())
