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

    # -------------------------
    # HEADER
    # -------------------------
    pdf.set_font("Arial", "B", 22)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 15, f"{workout.name.upper()}", ln=True, align='C')

    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.6)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    # -------------------------
    # DESCRIPTION
    # -------------------------
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, "Description", ln=True)

    pdf.set_font("Arial", "", 12)
    description = workout.description or "No description provided."
    pdf.multi_cell(0, 8, description)
    pdf.ln(4)

    # -------------------------
    # STATUS
    # -------------------------
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Status", ln=True)

    pdf.set_font("Arial", "", 12)
    status = "Completed" if workout.is_completed else "Not Completed"
    pdf.set_text_color(0, 102, 51) if workout.is_completed else pdf.set_text_color(153, 102, 0)
    pdf.cell(0, 8, status, ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    # -------------------------
    # EXERCISES HEADER
    # -------------------------
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 12, "Exercises Included", ln=True)
    pdf.ln(3)

    # -------------------------
    # EXERCISES LIST
    # -------------------------
    exercise_count = 0

    for exercise in workout.exercises.all():
        exercise_count += 1
        x_start = 10
        box_width = 190
        page_start = pdf.page_no()
        y_start = pdf.get_y()

        # Exercise Name
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, exercise.name, ln=True)

        # Helper for label/value inside box
        def label_value(label, value, multiline=False):
            label_width = 40
            value_width = box_width - label_width - 2

            pdf.set_font("Arial", "B", 12)
            pdf.set_text_color(50, 50, 50)
            x_label = pdf.get_x()
            y_label = pdf.get_y()
            pdf.cell(label_width, 8, f"{label}:", border=0)

            pdf.set_font("Arial", "", 12)
            pdf.set_text_color(0, 0, 0)

            if multiline:
                x_value = pdf.get_x()
                y_value = pdf.get_y()
                pdf.set_xy(x_value, y_value)
                pdf.multi_cell(value_width, 8, value)
                pdf.set_xy(x_start, pdf.get_y())  # reset to left margin
            else:
                pdf.cell(value_width, 8, value, ln=True)

            pdf.ln(1)  # spacing between fields

        # Exercise Details
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

        page_end = pdf.page_no()
        y_end = pdf.get_y()

        # Draw box
        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.3)
        if page_start == page_end:
            box_height = y_end - y_start + 2
            pdf.rect(x_start, y_start - 1, box_width, box_height)
        else:
            # Split box across pages
            pdf.rect(x_start, y_start - 1, box_width, pdf.h - y_start - 15)
            pdf.rect(x_start, 10, box_width, y_end - 10 + 2)

        pdf.ln(5)

        # Force page break after every 2 exercises
        if exercise_count % 2 == 0:
            pdf.add_page()

    # -------------------------
    # OUTPUT PDF
    # -------------------------
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{workout.name}.pdf"'
    return response
