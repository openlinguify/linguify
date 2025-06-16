"""
Django template-based authentication URLs
"""
from django.urls import path
from .views_auth import LoginView, RegisterView, logout_view

app_name = 'auth'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', logout_view, name='logout'),
]