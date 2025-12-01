from django import forms
from django.contrib import admin
from .models import Ingredient,MealPlan


# Custom form for IngredientAdmin
class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = "__all__"
        labels = {
            "calories": "Calories (per 100g)",
            "proteins": "Proteins (per 100g)",
            "carbs": "Carbs (per 100g)",
            "fats": "Fats (per 100g)",
        }

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    form = IngredientForm

    fieldsets = (
        ("Information about ingredient", {
            "fields": (
                "name",
                "description",
                "category",
                "calories",
                "proteins",
                "carbs",
                "fats",
            )
        }),
    )

    list_display = ("name", "category", "calories", "proteins", "carbs", "fats")
    search_fields = ("name", "description")
    list_filter = ("category",)
    list_per_page = 10
    ordering = ("name",)

@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('day', 'get_breakfast', 'get_lunch', 'get_dinner', 'get_snacks')

    def get_breakfast(self, obj):
        return ", ".join([i.name for i in obj.breakfast.all()])
    get_breakfast.short_description = 'Breakfast'

    def get_lunch(self, obj):
        return ", ".join([i.name for i in obj.lunch.all()])
    get_lunch.short_description = 'Lunch'

    def get_dinner(self, obj):
        return ", ".join([i.name for i in obj.dinner.all()])
    get_dinner.short_description = 'Dinner'

    def get_snacks(self, obj):
        return ", ".join([i.name for i in obj.snacks.all()])
    get_snacks.short_description = 'Snacks'


admin.site.site_header = "Nutrition  Administration"
admin.site.site_title = "Nutrition  Admin"
admin.site.index_title = "Welcome to your Nutrition  Dashboard"