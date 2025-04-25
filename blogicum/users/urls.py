from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('registration/', views.register, name='registration'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/edit/', views.profile_edit, name='profile_edit'),
]