from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
import json

from .models import MealPlan, Ingredient, Meal, MealIngredient
from .forms import MealPlanForm, IngredientForm, MealForm, MealIngredientForm, IngredientSearchForm

# Helper functions
def get_nutrition_totals(meals):
    """Calculate total nutrition from a list of meals"""
    totals = {
        'calories': 0,
        'proteins': 0,
        'carbs': 0,
        'fats': 0
    }
    for meal in meals:
        totals['calories'] += meal.total_calories
        totals['proteins'] += meal.total_proteins
        totals['carbs'] += meal.total_carbs
        totals['fats'] += meal.total_fats
    return totals

@login_required
def index(request):
    """Render the nutrition dashboard"""
    from django.utils import timezone
    today = timezone.now().date()
    
    # Temporary fix - handle missing user field
    try:
        # Try to get today's plan without user filter first
        today_plan = MealPlan.objects.filter(day=today).first()
    except Exception as e:
        today_plan = None
    
    # If no today_plan, set defaults
    if not today_plan:
        nutrition_totals = {'calories': 0, 'proteins': 0, 'carbs': 0, 'fats': 0}
        calorie_progress = 0
        protein_progress = 0
        recent_plans = []
    else:
        today_meals = today_plan.meals.all()
        nutrition_totals = get_nutrition_totals(today_meals)
        calorie_progress = min((nutrition_totals['calories'] / today_plan.calorie_goal) * 100, 100) if today_plan.calorie_goal > 0 else 0
        protein_progress = min((nutrition_totals['proteins'] / today_plan.protein_goal) * 100, 100) if today_plan.protein_goal > 0 else 0
        recent_plans = MealPlan.objects.all().order_by('-day')[:5]
    
    context = {
        'today_plan': today_plan,
        'nutrition_totals': nutrition_totals,
        'calorie_progress': calorie_progress,
        'protein_progress': protein_progress,
        'recent_plans': recent_plans,
    }
    return render(request, 'nutrition/index.html', context)

class ListMealPlan(LoginRequiredMixin, ListView):
    model = MealPlan
    template_name = 'nutrition/list_MealPlan.html'
    context_object_name = 'mealplans'
    paginate_by = 10
    
    def get_queryset(self):
        # Temporary: Return all meal plans until user field is fixed
        return MealPlan.objects.all().order_by("-day")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for plan in context['mealplans']:
            plan.nutrition_totals = get_nutrition_totals(plan.meals.all())
        return context

class DetailMealPlan(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = MealPlan
    template_name = 'nutrition/detail_MealPlan.html'
    context_object_name = 'mealplan'
    
    def test_func(self):
        mealplan = self.get_object()
        return self.request.user == mealplan.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mealplan = self.get_object()
        
        meals_by_type = {}
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
            meals_by_type[meal_type] = mealplan.meals.filter(meal_type=meal_type)
        
        context['meals_by_type'] = meals_by_type
        context['nutrition_totals'] = get_nutrition_totals(mealplan.meals.all())
        context['calorie_progress'] = mealplan.calorie_progress
        context['protein_progress'] = mealplan.protein_progress
        
        return context

class AddMealPlan(LoginRequiredMixin, CreateView):
    model = MealPlan
    form_class = MealPlanForm
    template_name = 'nutrition/add_MealPlan.html'
    success_url = reverse_lazy('nutrition:list_mealplans')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Meal plan created successfully!')
        return super().form_valid(form)

class UpdateMealPlan(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = MealPlan
    form_class = MealPlanForm
    template_name = 'nutrition/update_MealPlan.html'
    success_url = reverse_lazy('nutrition:list_mealplans')
    
    def test_func(self):
        mealplan = self.get_object()
        return self.request.user == mealplan.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Meal plan updated successfully!')
        return super().form_valid(form)

class DeleteMealPlan(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = MealPlan
    template_name = 'nutrition/delete_MealPlan.html'
    success_url = reverse_lazy('nutrition:list_mealplans')
    
    def test_func(self):
        mealplan = self.get_object()
        return self.request.user == mealplan.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Meal plan deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def list_ingredients(request):
    form = IngredientSearchForm(request.GET or None)
    ingredients = Ingredient.objects.all()
    
    if form.is_valid():
        query = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        
        if query:
            ingredients = ingredients.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        if category:
            ingredients = ingredients.filter(category=category)
    
    paginator = Paginator(ingredients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'nutrition/list_ingredients.html', {
        'ingredients': page_obj,
        'form': form,
        'page_obj': page_obj,
    })



@login_required
def manage_meal_plan_meals(request, mealplan_id):
    mealplan = get_object_or_404(MealPlan, id=mealplan_id, user=request.user)
    
    if request.method == 'POST':
        print("=== COMPLETE POST DATA ===")
        print(dict(request.POST))
        print("==========================")
        
        action = request.POST.get('action')
        
        if action == 'add_ingredient':
            meal_type = request.POST.get('meal_type')
            ingredient_id = request.POST.get('ingredient_id')
            quantity = request.POST.get('quantity')
            
            print(f"DEBUG: meal_type={meal_type}, ingredient_id={ingredient_id}, quantity={quantity}")
            
            if meal_type and ingredient_id and quantity:
                try:
                    # Get or create meal for this meal plan and type
                    meal, created = Meal.objects.get_or_create(
                        mealplan=mealplan,
                        meal_type=meal_type,
                        defaults={'name': f'{meal_type.title()} Meal'}
                    )
                    print(f"Meal: {meal.id}, created: {created}")
                    
                    # Get the ingredient
                    ingredient = Ingredient.objects.get(id=ingredient_id)
                    print(f"Ingredient: {ingredient.name} (ID: {ingredient.id})")
                    
                    # CORRECTED: Create MealIngredient WITHOUT meal field
                    meal_ingredient = MealIngredient.objects.create(
                        ingredient=ingredient,  # Only these two fields!
                        quantity=quantity
                    )
                    print(f"MealIngredient created: {meal_ingredient.id}")
                    
                    # CORRECTED: Add the MealIngredient to the meal's ingredients
                    meal.ingredients.add(meal_ingredient)
                    print(f"Added to meal. Meal now has {meal.ingredients.count()} ingredients")
                    
                    messages.success(request, f'Added {ingredient.name} to {meal_type}.')
                    
                except Ingredient.DoesNotExist:
                    print("ERROR: Ingredient not found")
                    messages.error(request, 'Ingredient not found.')
                except Exception as e:
                    print(f"ERROR: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    messages.error(request, f'Error adding ingredient: {str(e)}')
            else:
                # Debug what's missing
                missing = []
                if not meal_type: missing.append("meal type")
                if not ingredient_id: missing.append("ingredient")
                if not quantity: missing.append("quantity")
                print(f"ERROR: Missing {missing}")
                messages.error(request, f'Missing: {", ".join(missing)}')
            
            # Redirect to avoid form resubmission
            return redirect('nutrition:manage_meal_plan_meals', mealplan_id=mealplan_id)
                    
        elif action == 'remove_ingredient':
            # Handle ingredient removal
            meal_ingredient_id = request.POST.get('meal_ingredient_id')
            if meal_ingredient_id:
                try:
                    # Get the MealIngredient and ensure it belongs to the current user
                    meal_ingredient = MealIngredient.objects.get(
                        id=meal_ingredient_id,
                        meal__mealplan__user=request.user
                    )
                    ingredient_name = meal_ingredient.ingredient.name
                    meal_ingredient.delete()
                    messages.success(request, f'Removed {ingredient_name}.')
                except MealIngredient.DoesNotExist:
                    messages.error(request, 'Ingredient not found.')
            
            # Redirect after POST to avoid resubmission
            return redirect('nutrition:manage_meal_plan_meals', mealplan_id=mealplan_id)
    
    # Prepare meals data for template (GET request or after redirect)
    meals_by_type = {}
    for meal_type, _ in Meal.MEAL_TYPES:
        meals = Meal.objects.filter(mealplan=mealplan, meal_type=meal_type)
        # Prefetch related ingredients for performance
        meals = meals.prefetch_related('ingredients__ingredient')
        meals_by_type[meal_type] = meals
        
        # DEBUG: Print what meals we found
        print(f"Meals for {meal_type}: {meals.count()}")
        for meal in meals:
            print(f"  Meal {meal.id} has {meal.ingredients.count()} ingredients")
            for mi in meal.ingredients.all():
                print(f"    - {mi.ingredient.name}: {mi.quantity}g")
    
    # Calculate daily totals for the summary
    daily_totals = {
        'calories': 0,
        'proteins': 0,
        'carbs': 0,
        'fats': 0
    }
    
    for meal_type, meals in meals_by_type.items():
        for meal in meals:
            daily_totals['calories'] += meal.total_calories
            daily_totals['proteins'] += meal.total_proteins
            daily_totals['carbs'] += meal.total_carbs
            daily_totals['fats'] += meal.total_fats
    
    # Get all ingredients for the dropdown
    all_ingredients = Ingredient.objects.all()
    
    context = {
        'mealplan': mealplan,
        'meals_by_type': meals_by_type,
        'all_ingredients': all_ingredients,
        'daily_totals': daily_totals,
    }
    
    return render(request, 'nutrition/manage_meals.html', context)
    
def add_meal_ingredient(request, meal_id):
    meal = get_object_or_404(Meal, pk=meal_id)
    
    if request.method == 'POST':
        form = MealIngredientForm(request.POST)
        if form.is_valid():
            meal_ingredient = form.save()
            meal.ingredients.add(meal_ingredient)
            messages.success(request, 'Ingredient added to meal!')
            # Use mealplan_id instead of pk, and access mealplan directly
            return redirect('nutrition:manage_meal_plan_meals', mealplan_id=meal.mealplan.id)
    
    else:
        form = MealIngredientForm()
    
    return render(request, 'nutrition/add_meal_ingredient.html', {
        'form': form,
        'meal': meal
    })

@login_required
def search_ingredients_api(request):
    query = request.GET.get('q', '')
    if query:
        ingredients = Ingredient.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )[:10]
        results = [
            {
                'id': ing.id,
                'name': ing.name,
                'calories': ing.calories,
                'proteins': ing.proteins,
                'carbs': ing.carbs,
                'fats': ing.fats,
                'category': ing.get_category_display()
            }
            for ing in ingredients
        ]
    else:
        results = []
    
    return JsonResponse(results, safe=False)
