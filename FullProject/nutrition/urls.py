from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name='meal-list'),
    path('mealplans/', views.ListMealPlan.as_view(), name='list_mealplans'),
    path('mealplans/<int:pk>/', views.DetailMealPlan.as_view(), name='detail_mealplan'),
    path('mealplans/add/', views.AddMealPlan.as_view(), name='add_mealplan'),
    path('mealplans/<int:pk>/update/', views.UpdateMealPlan.as_view(), name='update_mealplan'),
    path('mealplans/<int:pk>/delete/', views.DeleteMealPlan.as_view(), name='delete_mealplan'),
    path('ingredients/', views.list_ingredients, name='list_ingredients'),
    
]