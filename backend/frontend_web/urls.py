"""
URLs pour le frontend web de Linguify
"""

from django.urls import path
from django.http import FileResponse
from django.conf import settings
from . import views
import os

app_name = 'frontend_web'

def serve_robots(request):
    file_path = os.path.join(settings.BASE_DIR, 'frontend_web/static/robots.txt')
    return FileResponse(open(file_path, 'rb'), content_type='text/plain')

def serve_sitemap(request):
    file_path = os.path.join(settings.BASE_DIR, 'frontend_web/static/sitemap.xml')
    return FileResponse(open(file_path, 'rb'), content_type='application/xml')

def serve_manifest(request):
    file_path = os.path.join(settings.BASE_DIR, 'frontend_web/static/manifest.json')
    return FileResponse(open(file_path, 'rb'), content_type='application/json')

urlpatterns = [
    # Page d'accueil
    path('', views.landing_page, name='landing'),
    
    # Pages d'information
    path('features/', views.features_page, name='features'),
    
    # Changement de langue
    path('set-language/<str:language>/', views.set_language, name='set_language'),
    
    # Authentification
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Profil
    path('profile/', views.profile_view, name='profile'),
    
    # Paramètres
    path('settings/', views.settings_view, name='settings'),
    
    # Conditions d'utilisation
    path('annexes/terms/', views.terms_view, name='terms'),
    path('annexes/terms/accept/', views.accept_terms_view, name='accept_terms'),
    
    # API endpoints pour le dashboard
    path('api/user/stats/', views.get_user_stats, name='user_stats'),
    path('api/apps/', views.get_available_apps, name='available_apps'),
    
    # API endpoints pour les notifications
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/<str:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # SEO et PWA files
    path('robots.txt', serve_robots, name='robots'),
    path('sitemap.xml', serve_sitemap, name='sitemap'),
    path('manifest.json', serve_manifest, name='manifest'),
]