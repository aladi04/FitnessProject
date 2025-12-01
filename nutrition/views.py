from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import MealPlan
from .forms import MealPlanForm
from .models import Ingredient



@login_required
def index(request):
	"""Render the nutrition (meals) index page (login required)."""
	return render(request, 'nutrition/index.html', {})

class ListMealPlan(ListView):
    model = MealPlan
    template_name = 'nutrition/list_MealPlan.html'
    context_object_name = 'mealplans' 
    queryset = MealPlan.objects.all().order_by("-day")


class DetailMealPlan(DetailView):
    model = MealPlan
    template_name = 'nutrition/detail_MealPlan.html'
    context_object_name = 'mealplan'

class AddMealPlan(CreateView):
    model = MealPlan
    form_class = MealPlanForm  
    template_name = 'nutrition/add_MealPlan.html'
    success_url = reverse_lazy('list_mealplans')
    success_url = reverse_lazy('list_mealplans')


class UpdateMealPlan(UpdateView):
    model = MealPlan
    form_class = MealPlanForm
    template_name = 'nutrition/update_MealPlan.html'
    success_url = reverse_lazy('list_mealplans')


class DeleteMealPlan(DeleteView):
    model = MealPlan
    template_name = 'nutrition/delete_MealPlan.html'
    success_url = reverse_lazy('list_mealplans')

def list_ingredients(request):
    query = request.GET.get('q')  
    if query:
        ingredients = Ingredient.objects.filter(name__icontains=query)  
    else:
        ingredients = Ingredient.objects.all()
    return render(request, 'nutrition/list_ingredients.html', {
        'ingredients': ingredients,
        'query': query
    })

