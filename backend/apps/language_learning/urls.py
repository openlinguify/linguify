"""
URLs configuration for language_learning app.
"""
from django.urls import path, include
from . import views

app_name = 'language_learning'

urlpatterns = [
    # Main pages
    path('', views.language_learning_home, name='home'),
    path('create/', views.create_item, name='create_item'),
    path('edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),
    
    # Settings pages
    path('settings/', views.LanguageLearningSettingsView.as_view(), name='settings'),
    
    # API endpoints (legacy compatibility)
    path('api/items/', views.api_items, name='api_items'),
    path('api/start_language/', views.start_language_learning, name='start_language'),
    path('api/user-settings/', views.get_user_language_learning_settings, name='user_settings'),
    
    # Include DRF ViewSets
    path('api/v1/', include('apps.language_learning.urls_api')),
]
