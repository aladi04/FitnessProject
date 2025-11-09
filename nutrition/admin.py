from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Meal, Ingredient


class IngredientInline(admin.TabularInline):
    model = Meal.ingredients.through
    extra = 1


class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_favorite')
    search_fields = ('name',)
    inlines = [IngredientInline]


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'calories', 'protein')
    search_fields = ('name',)


admin.site.register(Meal, MealAdmin)
admin.site.register(Ingredient, IngredientAdmin)
