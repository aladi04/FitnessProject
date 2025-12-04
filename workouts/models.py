from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.models import User


CATEGORY_CHOICES = [
    ('strength', 'Strength'),
    ('cardio', 'Cardio'),
    ('flexibility', 'Flexibility'),
]

DIFFICULTY_CHOICES = [
    ('easy', 'Easy'),
    ('medium', 'Medium'),
    ('hard', 'Hard'),
]

MUSCLE_CHOICES = [
    ('chest', 'Chest'),
    ('back', 'Back'),
    ('legs', 'Legs'),
    ('shoulders', 'Shoulders'),
    ('biceps', 'Biceps'),
    ('triceps', 'Triceps'),
    ('core', 'Core'),
]


class Exercise(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    target_muscle = models.CharField(max_length=20, choices=MUSCLE_CHOICES)

    description = models.TextField(blank=True, null=True)
    video_url = models.CharField(max_length=200, blank=True, null=True)

    sets = models.IntegerField(default=0)
    reps = models.IntegerField(default=0)
    weight = models.IntegerField(default=0)
    duration = models.IntegerField(blank=True, null=True, help_text="Required for cardio or flexibility exercises")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.category in ['cardio', 'flexibility'] and not self.duration:
            raise ValidationError({'duration': 'Duration is required for cardio or flexibility exercises.'})

    def has_video(self):
        return self.video_url is not None and self.video_url != ""


class Workout(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workouts",
        null=True,
        blank=True
    )

    exercises = models.ManyToManyField(Exercise, related_name="workouts")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
