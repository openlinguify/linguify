# plateforme/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('platforme/', views.platforme, name='platforme'),
    path('sous-categorie/<int:sous_categorie_id>/lessons/', views.lesson_list, name='lesson_list'),
    path('lesson/<int:lesson_id>/activities/', views.activity_list, name='activity_list'),
    path('activity/<int:activity_id>/', views.activity, name='activity'),
    path('activity/<int:activity_id>/vocabulaire/', views.vocabulaire_list, name='vocabulaire_list'),
    path('video/<int:activity_id>/', views.video_list, name='video_list'),
    path('exercice/<int:activity_id>/', views.exercice_list, name='exercice_list'),
    path('test/<int:activity_id>/', views.test_list, name='test_list'),
]
