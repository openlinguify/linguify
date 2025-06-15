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
    
    # Pages des applications
    path('apps/', views.apps_page, name='apps'),
    path('apps/courses/', views.app_courses_page, name='app_courses'),
    path('apps/revision/', views.app_revision_page, name='app_revision'),
    path('apps/notebook/', views.app_notebook_page, name='app_notebook'),
    path('apps/quizz/', views.app_quizz_page, name='app_quizz'),
    path('apps/language-ai/', views.app_language_ai_page, name='app_language_ai'),
    
    # Pages entreprise
    path('about/', views.about_page, name='about'),
    path('careers/', views.careers_page, name='careers'),
    path('blog/', views.blog_page, name='blog'),
    path('press/', views.press_page, name='press'),
    path('roadmap/', views.roadmap_page, name='roadmap'),
    
    # Pages support
    path('help/', views.help_page, name='help'),
    path('contact/', views.contact_page, name='contact'),
    path('bug-report/', views.bug_report_page, name='bug_report'),
    path('status/', views.status_page, name='status'),
    
    # Pages légales
    path('privacy/', views.privacy_page, name='privacy'),
    path('cookies/', views.cookies_page, name='cookies'),
    
    # Changement de langue
    path('set-language/<str:language>/', views.set_language, name='set_language'),
    
    # Authentification
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # App Store
    path('app-store/', views.app_store_view, name='app_store'),
    
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
    
    # Admin tools
    path('admin-tools/fix-apps/', views.fix_apps_view, name='fix_apps'),
    
    # SEO et PWA files
    path('robots.txt', serve_robots, name='robots'),
    path('sitemap.xml', serve_sitemap, name='sitemap'),
    path('manifest.json', serve_manifest, name='manifest'),
]