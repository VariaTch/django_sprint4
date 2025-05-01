from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.index, name="index"),
    path("posts/create/", views.post_create, name="create_post"),
    path("posts/<int:id>/", views.post_detail, name="post_detail"),
    path("posts/<int:id>/edit/", views.post_edit, name="edit_post"),
    path("posts/<int:post_id>/delete/", views.post_delete, name="delete_post"),
    path("category/<slug:category_slug>/",
         views.category_posts, name="category_posts"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path(
        "profile/<str:username>/edit/",
        views.ProfileUpdateView.as_view(),
        name="profile_edit",
    ),
    path(
        "posts/<int:post_id>/comment/",
        views.CommentCreateView.as_view(),
        name="add_comment",
    ),
    path(
        "posts/<int:post_id>/comment/<int:comment_id>/edit/",
        views.CommentUpdateView.as_view(),
        name="edit_comment",
    ),
    path(
        "posts/<int:post_id>/delete_comment/<int:comment_id>/",
        views.CommentDeleteView.as_view(),
        name="delete_comment",
    ),
    path("about/", views.AboutPageView.as_view(), name="about"),
    path("rules/", views.RulesPageView.as_view(), name="rules"),
]
