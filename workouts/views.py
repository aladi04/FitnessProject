from .models import Workout, Exercise
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import WorkoutForm


@login_required
def index(request):
    """Render the workouts index page (login required)."""
    return render(request, 'workouts/index.html', {})


class workoutListView(LoginRequiredMixin, ListView):
    model = Workout
    template_name = 'workouts/index.html'
    context_object_name = 'Workouts'


class exerciseListView(LoginRequiredMixin, ListView):
    model = Exercise
    template_name = 'workouts/listExercise.html'
    context_object_name = 'Exercises'


class workoutCreateView(LoginRequiredMixin, CreateView):
    model = Workout
    success_url = reverse_lazy('workout_list_view')
    form_class = WorkoutForm


class workoutDetailView(LoginRequiredMixin, DetailView):
    model = Workout


class workoutUpdateView(LoginRequiredMixin, UpdateView):
    model = Workout
    success_url = reverse_lazy('workout_list_view')
    form_class = WorkoutForm


class workoutDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Workout
    success_url = reverse_lazy('workout_list_view')

    def test_func(self):
        return self.request.user.is_superuser
