from django.contrib import admin


# Register your models here.

from .models import Workout, Exercise


class ExerciseInline(admin.TabularInline):
    model = Workout.exercises.through
    extra = 1


class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_completed')
    search_fields = ('name',)
    inlines = [ExerciseInline]


class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'difficulty', 'target_muscle')
    search_fields = ('name',)


admin.site.register(Workout, WorkoutAdmin)
admin.site.register(Exercise, ExerciseAdmin)

