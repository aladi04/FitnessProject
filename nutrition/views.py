from .models import Meal, Ingredient
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import MealForm


@login_required
def index(request):
    """Render the meals index page (login required)."""
    return render(request, 'nutrition/index.html', {})


class mealListView(LoginRequiredMixin, ListView):
    model = Meal
    template_name = 'nutrition/index.html'
    context_object_name = 'Meals'


class ingredientListView(LoginRequiredMixin, ListView):
    model = Ingredient
    template_name = 'nutrition/listIngredient.html'
    context_object_name = 'Ingredients'


class mealCreateView(LoginRequiredMixin, CreateView):
    model = Meal
    form_class = MealForm
    template_name = 'nutrition/meal_form.html'  # <- explicitly
    success_url = reverse_lazy('meal_list_view')
    form_class = MealForm


class mealDetailView(LoginRequiredMixin, DetailView):
    model = Meal


class mealUpdateView(LoginRequiredMixin, UpdateView):
    model = Meal
    success_url = reverse_lazy('meal_list_view')
    form_class = MealForm


class mealDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Meal
    success_url = reverse_lazy('meal_list_view')

    def test_func(self):
        return self.request.user.is_superuser
