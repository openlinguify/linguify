# vocab/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ThemeViewSet, UnitViewSet, ExerciseViewSet
from . import views
router = DefaultRouter()
router.register(r'themes', ThemeViewSet, basename='theme')
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'exercises', ExerciseViewSet, basename='exercise')

urlpatterns = [
    path('', include(router.urls)),
    path('update_word_status/', views.update_word_status, name='update_word_status'),

]
