# lingoProject/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
)
from authentication import views as auth_views
from linguify import views as linguify_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('base/', linguify_views.base),

    path('', LoginView.as_view(
        template_name='authentication/login.html',
        redirect_authenticated_user=False
    ), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', auth_views.signup_page, name='signup'),
    path('change-password/', PasswordChangeView.as_view(
        template_name='authentication/password_change_form.html'
    ), name='password_change'),
    path('change-password-done/', PasswordChangeDoneView.as_view(
        template_name='authentication/password_change_done.html'
    ), name='password_change_done'),
    path('home/', linguify_views.home, name='home'),
    path('index/', linguify_views.index, name='index'),
    path('vocabulaire/', linguify_views.vocabulaire, name='vocabulaire'),
    path('grammaire/', linguify_views.grammaire, name='grammaire'),
    path('exercice/', linguify_views.exercice_vocabulary, name='exercice_vocabulaire'),
    path('revision/', linguify_views.revision, name='revision'),
    path('quiz/', linguify_views.quiz, name='quiz'),
    path('pricing/', linguify_views.prices, name='pricing'),

    path('testlinguisitique/', linguify_views.testlinguisitique, name='testlinguisitique'),

    path('result/', linguify_views.check_answer, name='result'),
    path('header/', linguify_views.header),
    path('footer/', linguify_views.footer),
    path('courses/', linguify_views.courses),
    path('prices/', linguify_views.prices),
    path('contact/', linguify_views.contact),
    path('about/', linguify_views.about),
    path("", include("cards.urls")),
]
