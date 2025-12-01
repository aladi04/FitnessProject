from django.db import models



# Create your models here.
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
    ('processed', 'Processed / Fast Foods'),
    ('supplements', 'Supplements & Powders'),
]



class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    calories = models.FloatField(default=0)
    proteins = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fats = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    


class MealPlan(models.Model):
    day = models.DateField(unique=True)

    breakfast = models.ManyToManyField(
        Ingredient, related_name='breakfast_meals', blank=True
    )
    lunch = models.ManyToManyField(
        Ingredient, related_name='lunch_meals', blank=True
    )
    dinner = models.ManyToManyField(
        Ingredient, related_name='dinner_meals', blank=True
    )
    snacks = models.ManyToManyField(
        Ingredient, related_name='snack_meals', blank=True
    )

    def __str__(self):
        return f"Meal Plan for {self.day}"
   