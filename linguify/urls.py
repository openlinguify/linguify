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


    # General pages
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('prices/', views.prices, name='prices'),
    path('courses/', views.courses, name='courses'),
    path('testlinguistique/', views.testlinguistique, name='testlinguistique'),

    # Vocabulary and Grammar
    path('vocabulaire/', views.vocabulaire, name='vocabulaire'),
    path('exercice/', views.exercice_vocabulary, name='exercice_vocabulary'),
    path('grammaire/', views.grammaire, name='grammaire'),
    path('revision/', views.revision, name='revision'),
    path('quiz/', views.quiz, name='quiz'),
    path('result/', views.check_answer, name='result'),
    path('search-vocabulary/', views.search_vocabulary, name='search_vocabulary'),

    # Flashcards
    path('flashcards/', views.flashcard_list, name='flashcard_list'),
    path('flashcards/create/', views.flashcard_create, name='flashcard_create'),
    path('flashcards/<int:flashcard_id>/', views.flashcard_detail, name='flashcard_detail'),
    path('flashcards/<int:flashcard_id>/add_vocabulary/', views.add_vocabulary_to_flashcard,
         name='add_vocabulary_to_flashcard'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Header and Footer (if these are actual views)
    path('header/', views.header, name='header'),
    path('footer/', views.footer, name='footer'),
]

