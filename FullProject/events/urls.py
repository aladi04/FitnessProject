from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event-list'),
    path('event/<int:pk>/', views.event_detail, name='event-detail'),
    path('bookings/', views.booking_history, name='booking-history'),
    path('bookings/<int:pk>/update/', views.update_booking, name='update-booking'),
    path('bookings/<int:pk>/delete/', views.delete_booking, name='delete-booking'),
]