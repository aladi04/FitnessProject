from django.urls import path
from . import views

urlpatterns = [
    path("", views.community_home, name="community"),
    path("create/", views.create_post, name="create_post"),
    path("details/<int:post_id>/", views.post_details, name="post_details"),
    path('edit/<int:post_id>/', views.update_post, name='update_post'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path("<int:post_id>/like/", views.like_post, name="like_post"),
    path("<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("comment/delete/<int:comment_id>/", views.delete_comment, name="delete_comment"),
    path("comment/edit/<int:comment_id>/", views.update_comment, name="update_comment"),
    path("notifications/", views.notifications_list, name="notifications_list"),
    path("notifications/read/<int:notification_id>/", views.mark_notification_read, name="mark_notification_read"),
]
