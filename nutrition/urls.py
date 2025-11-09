from django.urls import path
from .views import mealListView, mealCreateView, mealDeleteView, mealDetailView, mealUpdateView

urlpatterns = [
    path('', mealListView.as_view(), name='meal_list_view'),
    path('add/', mealCreateView.as_view(), name='meal_create_view'),
    path('details/<int:pk>/', mealDetailView.as_view(), name='meal_details_view'),
    path('update/<int:pk>/', mealUpdateView.as_view(), name='meal_update_view'),
    path('delete/<int:pk>/', mealDeleteView.as_view(), name='meal_delete_view'),
]
