from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard, name='home'),
    path('login/', views.user_login, name='login'),  # Use your custom login view
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:user_id>/', views.profile, name='profile_detail'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/add-member/', views.add_member, name='add_member'),
    path('admin/edit-member/<int:pk>/', views.edit_member, name='edit_member'),
    path('admin/delete-member/<int:pk>/', views.delete_member, name='delete_member'),
    path('admin/add-admin/', views.add_admin, name='add_admin'),
    path('admin/edit-admin/<int:pk>/', views.edit_admin, name='edit_admin'),
    path('admin/delete-admin/<int:pk>/', views.delete_admin, name='delete_admin'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/deactivate/', views.deactivate_account, name='deactivate_account'),
    path('profile/delete/', views.delete_account, name='delete_account'),
]