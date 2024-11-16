from django.urls import path
from . import views
from .views import RegisterView, LoginView, LogoutView, UserView

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    ]
