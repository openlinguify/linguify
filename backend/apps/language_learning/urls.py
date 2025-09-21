"""
URLs configuration for language_learning app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import learning_views, settings_views, language_learning_progress_views, setup_views

app_name = 'language_learning'

# Create router for DRF ViewSets
router = DefaultRouter()
router.register(r'languages', views.LanguageViewSet, basename='language')
router.register(r'user-languages', views.UserLanguageViewSet, basename='user-language')
router.register(r'items', views.LanguagelearningItemViewSet, basename='languagelearning-item')

urlpatterns = [
    # Configuration initiale pour nouveaux utilisateurs
    path('setup/', setup_views.learning_setup, name='learning_setup'),
    path('setup/skip/', setup_views.skip_setup, name='skip_setup'),
    path('profile/settings/', setup_views.profile_settings, name='profile_settings'),

    # Main pages
    path('', learning_views.learning_interface, name='home'),
    path('learn/', learning_views.learning_interface, name='learning_interface'),
    path('progress/', language_learning_progress_views.progress_view, name='progress'),
    path('api/refresh-progress/', learning_views.refresh_progress, name='refresh_progress'),
    path('unit/<int:unit_id>/modules/', learning_views.unit_modules, name='unit_modules'),
    path('module/<int:module_id>/start/', learning_views.start_module, name='start_module'),
    path('module/<int:module_id>/complete/', learning_views.complete_module, name='complete_module'),

    # HTMX Partials endpoints
    path('partials/navbar/', learning_views.navbar_partial, name='navbar_partial'),
    path('partials/progress/', learning_views.progress_panel_partial, name='progress_panel_partial'),
    path('partials/units/', learning_views.units_list_partial, name='units_list_partial'),

    # Legacy pages (kept for compatibility)
    path('old/', views.language_learning_home, name='old_home'),
    path('create/', views.create_item, name='create_item'),
    path('edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),

    # Settings pages
    path('settings/', settings_views.language_learning_settings, name='settings'),

    # API endpoints
    path('api/items/', views.api_items, name='api_items'),
    path('api/start_language/', views.start_language_learning, name='start_language'),
    path('api/user-settings/', views.get_user_language_learning_settings, name='user_settings'),
    path('api/settings/', views.get_user_language_learning_settings, name='api_user_settings'),
    path('api/units/<int:unit_id>/modules/', learning_views.api_unit_modules, name='api_unit_modules'),

    # DRF ViewSets
    path('api/v1/', include(router.urls)),
]
