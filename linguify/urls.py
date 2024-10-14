# linguifY/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('courses/', views.courses, name='courses'),
    path('header/', views.header, name='header'),
    path('footer/', views.footer, name='footer'),
    path('prices/', views.prices, name='prices'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('search-vocabulary/', views.search_vocabulary, name='search_vocabulary'),
    path('result/', views.check_answer, name='result'),
    path('testlinguisitique/', views.testlinguisitique, name='testlinguisitique'),
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('grammaire/', views.grammaire, name='grammaire'),
    path('exercice/', views.exercice_vocabulary, name='exercice_vocabulaire'),
    path('quiz/', views.quiz, name='quiz'),
    path('vocabulaire/', views.vocabulaire, name='vocabulaire'),  # Ajoutez cette ligne
]

