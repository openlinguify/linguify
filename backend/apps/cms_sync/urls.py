"""
URLs for CMS Sync API.
"""
from django.urls import path
from . import views

app_name = 'cms_sync'

urlpatterns = [
    # Sync endpoints
    path('teachers/', views.sync_teacher, name='sync_teacher'),
    path('units/', views.sync_unit, name='sync_unit'),
    path('chapters/', views.sync_chapter, name='sync_chapter'),
    path('lessons/', views.sync_lesson, name='sync_lesson'),
    
    # Status and management
    path('status/', views.sync_status, name='sync_status'),
    path('delete/', views.delete_synced_content, name='delete_content'),
]