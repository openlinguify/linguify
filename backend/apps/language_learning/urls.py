"""
URLs configuration for language_learning app.
"""
from django.urls import path, include
from . import views
from .views import learning_views, settings_views

app_name = 'language_learning'

urlpatterns = [
    # Main pages
    path('', learning_views.learning_interface, name='home'),
    path('learn/', learning_views.learning_interface, name='learning_interface'),
    path('unit/<int:unit_id>/modules/', learning_views.unit_modules, name='unit_modules'),
    path('module/<int:module_id>/start/', learning_views.start_module, name='start_module'),
    path('module/<int:module_id>/complete/', learning_views.complete_module, name='complete_module'),
    path('refresh-progress/', learning_views.refresh_progress, name='refresh_progress'),

    # Legacy pages (kept for compatibility)
    path('old/', views.language_learning_home, name='old_home'),
    path('create/', views.create_item, name='create_item'),
    path('edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),
    
    # Settings pages
    path('settings/', settings_views.language_learning_settings, name='settings'),
    
    # API endpoints (legacy compatibility)
    path('api/items/', views.api_items, name='api_items'),
    path('api/start_language/', views.start_language_learning, name='start_language'),
    path('api/user-settings/', views.get_user_language_learning_settings, name='user_settings'),
    
    # Include DRF ViewSets
    path('api/v1/', include('apps.language_learning.urls_api')),
]
