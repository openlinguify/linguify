from django.urls import path
from . import views

urlpatterns = [
    path('platforme/', views.platforme, name='platforme'),
    path('sous-categorie/<int:sous_categorie_id>/lessons/', views.lesson_list, name='lesson_list'),
    path('lesson/<int:lesson_id>/activities/', views.activity_list, name='activity_list'),
    ]

