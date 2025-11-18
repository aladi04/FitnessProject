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

    def get_queryset(self):
        queryset = super().get_queryset()
        # Always show workouts created by admins (superusers)
        admin_workouts = queryset.filter(created_by__is_superuser=True)
        if self.request.user.is_superuser:
            # Admins see all workouts
            user_workouts = queryset
        else:
            # Regular users see admin workouts + their own
            user_workouts = queryset.filter(created_by=self.request.user)
        queryset = admin_workouts | user_workouts
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        sort = self.request.GET.get('sort')
        if sort:
            queryset = queryset.order_by(sort)
        return queryset.distinct()


class exerciseListView(LoginRequiredMixin, ListView):
    model = Exercise
    template_name = 'workouts/listExercise.html'
    context_object_name = 'Exercises'


class workoutCreateView(LoginRequiredMixin, CreateView):
    model = Workout
    success_url = reverse_lazy('workout_list_view')
    form_class = WorkoutForm

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class workoutDetailView(LoginRequiredMixin, DetailView):
    model = Workout


class workoutUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Workout
    success_url = reverse_lazy('workout_list_view')
    form_class = WorkoutForm

    def test_func(self):
        workout = self.get_object()
        return self.request.user.is_superuser or workout.created_by == self.request.user


class workoutDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Workout
    success_url = reverse_lazy('workout_list_view')

    def test_func(self):
        workout = self.get_object()
        return self.request.user.is_superuser or workout.created_by == self.request.user
