from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone

class Ingredient(models.Model):
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
    
    ALLERGEN_CHOICES = [
        ('gluten', 'Gluten'),
        ('dairy', 'Dairy'),
        ('nuts', 'Nuts'),
        ('soy', 'Soy'),
        ('eggs', 'Eggs'),
        ('fish', 'Fish'),
        ('shellfish', 'Shellfish'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # Nutritional information per 100g
    calories = models.FloatField(default=0, validators=[MinValueValidator(0)])
    proteins = models.FloatField(default=0, validators=[MinValueValidator(0)])
    carbs = models.FloatField(default=0, validators=[MinValueValidator(0)])
    fats = models.FloatField(default=0, validators=[MinValueValidator(0)])
    fiber = models.FloatField(default=0, validators=[MinValueValidator(0)])
    sugar = models.FloatField(default=0, validators=[MinValueValidator(0)])
    sodium = models.FloatField(default=0, validators=[MinValueValidator(0)])
    
    # Additional info
    allergens = models.CharField(max_length=100, blank=True, choices=ALLERGEN_CHOICES)
    serving_size = models.CharField(max_length=50, default="100g", help_text="e.g., 100g, 1 cup, 1 piece")
    
    # Make these nullable for migration
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ingredients', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class MealIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(default=100, validators=[MinValueValidator(0.1)], help_text="Quantity in grams")
    
    @property
    def calculated_calories(self):
        return (self.ingredient.calories * self.quantity) / 100
    
    @property
    def calculated_proteins(self):
        return (self.ingredient.proteins * self.quantity) / 100
    
    @property
    def calculated_carbs(self):
        return (self.ingredient.carbs * self.quantity) / 100
    
    @property
    def calculated_fats(self):
        return (self.ingredient.fats * self.quantity) / 100

    def __str__(self):
        return f"{self.quantity}g of {self.ingredient.name}"

class Meal(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    name = models.CharField(max_length=100, blank=True)
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPES)
    ingredients = models.ManyToManyField(MealIngredient, blank=True)
    notes = models.TextField(blank=True)
    
    # ADD THIS: ForeignKey to MealPlan to establish the relationship
    mealplan = models.ForeignKey('MealPlan', on_delete=models.CASCADE, related_name='meals', null=True, blank=True)
    
    @property
    def total_calories(self):
        return sum(ingredient.calculated_calories for ingredient in self.ingredients.all())
    
    @property
    def total_proteins(self):
        return sum(ingredient.calculated_proteins for ingredient in self.ingredients.all())
    
    @property
    def total_carbs(self):
        return sum(ingredient.calculated_carbs for ingredient in self.ingredients.all())
    
    @property
    def total_fats(self):
        return sum(ingredient.calculated_fats for ingredient in self.ingredients.all())

    def __str__(self):
        return f"{self.meal_type}: {self.name or 'Unnamed Meal'}"

class MealPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meal_plans', null=True, blank=True)
    day = models.DateField()
    # REMOVE this line: meals = models.ManyToManyField(Meal, blank=True)
    
    # Daily goals
    calorie_goal = models.FloatField(default=2000, validators=[MinValueValidator(0)])
    protein_goal = models.FloatField(default=50, validators=[MinValueValidator(0)])
    carb_goal = models.FloatField(default=250, validators=[MinValueValidator(0)])
    fat_goal = models.FloatField(default=70, validators=[MinValueValidator(0)])
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ['user', 'day']
        ordering = ['-day']

    def __str__(self):
        return f"Meal Plan for {self.day} ({self.user.username})"

    @property
    def total_calories(self):
        return sum(meal.total_calories for meal in self.meals.all())
    
    @property
    def total_proteins(self):
        return sum(meal.total_proteins for meal in self.meals.all())
    
    @property
    def total_carbs(self):
        return sum(meal.total_carbs for meal in self.meals.all())
    
    @property
    def total_fats(self):
        return sum(meal.total_fats for meal in self.meals.all())

    @property
    def calorie_progress(self):
        if self.calorie_goal > 0:
            return min((self.total_calories / self.calorie_goal) * 100, 100)
        return 0
    
    @property
    def protein_progress(self):
        if self.protein_goal > 0:
            return min((self.total_proteins / self.protein_goal) * 100, 100)
        return 0
