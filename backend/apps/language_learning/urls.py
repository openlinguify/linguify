"""
URLs configuration for language_learning app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import learning_progress_views, learning_views, settings_views, setup_views

app_name = 'language_learning'

router = DefaultRouter()

urlpatterns = [
    # Configuration initiale pour nouveaux utilisateurs qui viennent d'installer l'application depuis l'app store.
    path('setup/', setup_views.learning_setup, name='learning_setup'),
    path('setup/skip/', setup_views.skip_setup, name='skip_setup'),
    path('profile/settings/', setup_views.profile_settings, name='profile_settings'),

    # Main pages
    path('', learning_views.learning_interface, name='home'),
    path('progress/', learning_progress_views.progress_view, name='progress'),

    # HTMX Partials endpoints
    path('partials/navbar/', learning_views.navbar_partial, name='navbar_partial'),
    path('partials/progress/', learning_views.progress_panel_partial, name='progress_panel_partial'),
    path('partials/units/', learning_views.units_list_partial, name='units_list_partial'),
    path('learn/', learning_views.learning_interface, name='learning_interface'),
    path('api/refresh-progress/', learning_views.refresh_progress, name='refresh_progress'),
    path('unit/<int:unit_id>/modules/', learning_views.unit_modules, name='unit_modules'),
    path('module/<int:module_id>/start/', learning_views.start_module, name='start_module'),
    path('module/<int:module_id>/complete/', learning_views.complete_module, name='complete_module'),

    # Settings pages
    path('settings/', settings_views.language_learning_settings, name='settings'),
]
