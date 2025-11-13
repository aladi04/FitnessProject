from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='challenge-list'),
    path('join/<int:challenge_id>/', views.join_challenge, name='challenge-join'),
    path('submit/<int:challenge_id>/', views.submit_score, name='challenge-submit'),
]