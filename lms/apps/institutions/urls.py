from django.urls import path
from . import views

app_name = 'institutions'

urlpatterns = [
    path('', views.institution_list, name='list'),
    path('register/', views.institution_register, name='register'),
]