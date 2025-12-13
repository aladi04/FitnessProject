from django.urls import path
from . import views

app_name = 'nutrition'

urlpatterns = [
    # Dashboard
    path('', views.index, name='index'),
    
    # Meal Plans
    path('mealplans/', views.ListMealPlan.as_view(), name='list_mealplans'),
    path('mealplans/<int:pk>/', views.DetailMealPlan.as_view(), name='detail_mealplan'),
    path('mealplans/add/', views.AddMealPlan.as_view(), name='add_mealplan'),
    path('mealplans/<int:pk>/update/', views.UpdateMealPlan.as_view(), name='update_mealplan'),
    path('mealplans/<int:pk>/delete/', views.DeleteMealPlan.as_view(), name='delete_mealplan'),
    path('mealplans/<int:mealplan_id>/meals/', views.manage_meal_plan_meals, name='manage_meal_plan_meals'),
    
    # Ingredients
    path('ingredients/', views.list_ingredients, name='list_ingredients'),
    
    # Meal Management
    path('meals/<int:meal_id>/add-ingredient/', views.add_meal_ingredient, name='add_meal_ingredient'),
    
    # API Endpoints
    path('api/search-ingredients/', views.search_ingredients_api, name='search_ingredients_api'),
]
