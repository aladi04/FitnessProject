from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Ingredient, MealPlan, Meal, MealIngredient

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = "__all__"
        labels = {
            "calories": "Calories (per 100g)",
            "proteins": "Proteins (g per 100g)",
            "carbs": "Carbs (g per 100g)",
            "fats": "Fats (g per 100g)",
        }

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    form = IngredientForm
    fieldsets = (
        ("Basic Information", {
            "fields": (
                "name", "description", "category", "serving_size", "allergens"
            )
        }),
        ("Nutritional Information (per 100g)", {
            "fields": (
                "calories", "proteins", "carbs", "fats", "fiber", "sugar", "sodium"
            )
        }),
        ("Metadata", {
            "fields": ("created_by", "created_at", "updated_at")
        }),
    )
    
    list_display = ("name", "category", "calories", "proteins", "carbs", "fats", "created_by")
    list_filter = ("category", "created_at", "allergens")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 20
    ordering = ("name",)
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # If creating a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class MealIngredientInline(admin.TabularInline):
    model = Meal.ingredients.through
    extra = 1
    verbose_name = "Meal Ingredient"
    verbose_name_plural = "Meal Ingredients"

# Add this inline to show meals in MealPlan admin
class MealInline(admin.TabularInline):
    model = Meal
    extra = 1
    fields = ['meal_type', 'name', 'notes']
    show_change_link = True

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'meal_type', 'mealplan', 'total_calories', 'total_proteins')
    list_filter = ('meal_type', 'mealplan')
    inlines = [MealIngredientInline]
    search_fields = ('name', 'notes')
    exclude = ('ingredients',)
    
    def total_calories(self, obj):
        return f"{obj.total_calories:.1f} kcal"
    total_calories.short_description = 'Total Calories'
    
    def total_proteins(self, obj):
        return f"{obj.total_proteins:.1f} g"
    total_proteins.short_description = 'Total Proteins'

@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('day', 'user', 'total_calories', 'calorie_goal', 'calorie_progress', 'created_at')
    list_filter = ('day', 'user', 'created_at')
    search_fields = ('user__username', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'total_calories', 'total_proteins', 'total_carbs', 'total_fats')
    # REMOVE THIS LINE: filter_horizontal = ('meals',)
    inlines = [MealInline]  # ADD THIS to show meals inline
    fieldsets = (
        ("Basic Information", {
            "fields": ("user", "day", "notes")
        }),
        ("Daily Goals", {
            "fields": ("calorie_goal", "protein_goal", "carb_goal", "fat_goal")
        }),
        ("Calculated Totals", {
            "fields": ("total_calories", "total_proteins", "total_carbs", "total_fats")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at")
        }),
    )
    
    def total_calories(self, obj):
        return f"{obj.total_calories:.1f} kcal"
    total_calories.short_description = 'Total Calories'
    
    def calorie_progress(self, obj):
        return f"{obj.calorie_progress:.1f}%"
    calorie_progress.short_description = 'Calorie Progress'

@admin.register(MealIngredient)
class MealIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'quantity', 'calculated_calories', 'calculated_proteins')
    list_filter = ('ingredient__category',)
    search_fields = ('ingredient__name',)
    
    def calculated_calories(self, obj):
        return f"{obj.calculated_calories:.1f} kcal"
    calculated_calories.short_description = 'Calories'
    
    def calculated_proteins(self, obj):
        return f"{obj.calculated_proteins:.1f} g"
    calculated_proteins.short_description = 'Proteins'

admin.site.site_header = "Nutrition App Administration"
admin.site.site_title = "Nutrition App Admin"
admin.site.index_title = "Welcome to Nutrition App Dashboard"
