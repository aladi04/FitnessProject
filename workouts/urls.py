from django.urls import path
from .views import (
    workoutListView,
    workoutCreateView,
    workoutDeleteView,
    workoutDetailView,
    workoutUpdateView,
    workout_export_pdf,
)

urlpatterns = [
    path('', workoutListView.as_view(), name='workout_list_view'),
    path('addW/', workoutCreateView.as_view(), name='workout_create_view'),
    path('detailsW/<int:pk>', workoutDetailView.as_view(), name='workout_details_view'),
    path('updateW/<int:pk>', workoutUpdateView.as_view(), name='workout_update_view'),
    path('deleteW/<int:pk>', workoutDeleteView.as_view(), name='workout_delete_view'),
    path('exportW/<int:pk>/', workout_export_pdf, name='workout_export_pdf'),
]
