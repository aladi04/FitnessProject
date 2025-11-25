from .models import Workout, Exercise
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from fpdf import FPDF

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

@login_required
def workout_export_pdf(request, pk):
    workout = get_object_or_404(Workout, pk=pk)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title - Centered and larger font
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 15, f"Workout: {workout.name}", ln=True, align='C')

    # Separator line
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # Description section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Description:", ln=True)
    pdf.set_font("Arial", "", 12)
    description = workout.description if workout.description else "No description provided."
    pdf.multi_cell(0, 8, description)
    pdf.ln(3)

    # Status section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Status:", ln=True)
    pdf.set_font("Arial", "", 12)
    status = "Completed" if workout.is_completed else "Not Completed"
    pdf.cell(0, 8, status, ln=True)
    pdf.ln(5)

    # Exercises list header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 12, "Exercises Included:", ln=True)
    pdf.ln(3)

    '''
    # Exercises details with border box and better spacing
    for exercise in workout.exercises.all():
        y_before = pdf.get_y()
        pdf.set_line_width(0.1)
        pdf.set_draw_color(0, 0, 0)

        # Draw a rectangle as border for each exercise block
        x_start = 10
        width = 190
        height_start = pdf.get_y()

        # Exercise Title
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, exercise.name, ln=True)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(30, 8, "Category:", border=0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, exercise.category.title(), ln=True)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(30, 8, "Difficulty:", border=0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, exercise.difficulty.title(), ln=True)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(30, 8, "Target Muscle:", border=0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, exercise.target_muscle.title(), ln=True)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(30, 8, "Description:", border=0)
        pdf.set_font("Arial", "", 12)
        description = exercise.description if exercise.description else "No description."
        pdf.multi_cell(0, 8, description)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(30, 8, "Sets:", border=0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, str(exercise.sets), ln=True)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(30, 8, "Reps:", border=0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, str(exercise.reps), ln=True)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(30, 8, "Weight:", border=0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, str(exercise.weight), ln=True)

        if exercise.duration:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(30, 8, "Duration:", border=0)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 8, f"{exercise.duration} seconds", ln=True)

        if exercise.video_url:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(30, 8, "Video URL:", border=0)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 8, exercise.video_url)

        # Calculate height for the border rectangle after the block content
        height_end = pdf.get_y()
        height = height_end - height_start + 3
        pdf.rect(x_start, height_start - 2, width, height)

        pdf.ln(5)'''
    for exercise in workout.exercises.all():
        x_start = 10
        box_width = 190
        y_start = pdf.get_y()

        # Start drawing content
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, exercise.name, ln=True)

        def label_value(label, value, multiline=False):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(30, 8, f"{label}:", border=0)
            pdf.set_font("Arial", "", 12)
            if multiline:
                pdf.multi_cell(0, 8, value)
            else:
                pdf.cell(0, 8, value, ln=True)

        label_value("Category", exercise.category.title())
        label_value("Difficulty", exercise.difficulty.title())
        label_value("Target Muscle", exercise.target_muscle.title())
        label_value("Description", exercise.description or "No description.", multiline=True)
        label_value("Sets", str(exercise.sets))
        label_value("Reps", str(exercise.reps))
        label_value("Weight", str(exercise.weight))
        if exercise.duration:
            label_value("Duration", f"{exercise.duration} seconds")
        if exercise.video_url:
            label_value("Video URL", exercise.video_url, multiline=True)

        # Draw rectangle after content
        y_end = pdf.get_y()
        box_height = y_end - y_start + 2
        pdf.rect(x_start, y_start - 1, box_width, box_height)

        pdf.ln(5)

    # Output PDF response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{workout.name}.pdf"'
    response.write(bytes(pdf.output(dest="S")))
    return response
