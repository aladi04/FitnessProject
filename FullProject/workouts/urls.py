from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='workout-list'),
]

from .views import workoutListView, workoutCreateView, workoutDeleteView, workoutDetailView, workoutUpdateView

urlpatterns = [
    path('', workoutListView.as_view(), name='workout_list_view'),
    path('addW/', workoutCreateView.as_view(), name='workout_create_view'),
    path('detailsW/<int:pk>', workoutDetailView.as_view(), name='workout_details_view'),
    path('updateW/<int:pk>', workoutUpdateView.as_view(), name='workout_update_view'),
    path('deleteW/<int:pk>', workoutDeleteView.as_view(), name='workout_delete_view'),
]

