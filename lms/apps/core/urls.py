from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.redirect_to_login, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]