"""
Django template-based authentication URLs
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from ..views.auth_views import LoginView, RegisterView, logout_view
from ..views.password_views import CustomPasswordResetView

app_name = 'auth'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', logout_view, name='logout'),
    
    # Password reset URLs
    path('password-reset/', 
         CustomPasswordResetView.as_view(
             template_name='authentication/password_reset/password_reset.html',
             email_template_name='authentication/password_reset/password_reset_email.txt',
             html_email_template_name='authentication/password_reset/password_reset_email.html',
             subject_template_name='authentication/password_reset/password_reset_subject.txt',
             success_url='/auth/password-reset/done/'
         ),
         name='password_reset'),
    
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='authentication/password_reset/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='authentication/password_reset/password_reset_confirm.html',
             success_url='/auth/password-reset/complete/'
         ),
         name='password_reset_confirm'),
    
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='authentication/password_reset/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]