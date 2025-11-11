from django.urls import path
from . import views

urlpatterns = [
    path("", views.community_home, name="community"),
    path("create/", views.create_post, name="create_post"),
    path("<int:post_id>/", views.post_details, name="post_details"),
    path("<int:post_id>/like/", views.like_post, name="like_post"),
    path("<int:post_id>/comment/", views.add_comment, name="add_comment"),
]
