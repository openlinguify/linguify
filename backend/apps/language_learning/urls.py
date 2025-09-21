"""
URLs configuration for language_learning app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import learning_progress_views, settings_views, setup_views, api_views

app_name = 'language_learning'

router = DefaultRouter()
router.register(r'languages', views.LanguageViewSet, basename='language')
router.register(r'user-languages', views.UserLanguageViewSet, basename='user-language')
router.register(r'course-units', views.CourseUnitViewSet, basename='course-unit')
router.register(r'module-progress', views.ModuleProgressViewSet, basename='module-progress')
router.register(r'user-progress', views.UserCourseProgressViewSet, basename='user-progress')
router.register(r'learning-profile', views.UserLearningProfileViewSet, basename='learning-profile')

urlpatterns = [
    # Configuration initiale pour nouveaux utilisateurs qui viennent d'installer l'application depuis l'app store.
    path('setup/', setup_views.learning_setup, name='learning_setup'),
    path('setup/skip/', setup_views.skip_setup, name='skip_setup'),
    path('profile/settings/', setup_views.profile_settings, name='profile_settings'),

    # Main pages
    path('', api_views.home, name='home'),
    path('progress/', learning_progress_views.progress_view, name='progress'),
    # Settings pages
    path('settings/', settings_views.language_learning_settings, name='settings'),

    # API endpoints pour HTMX
    path('api/dashboard/', api_views.api_dashboard_data, name='api_dashboard_data'),
    path('api/unit/<int:unit_id>/', api_views.api_unit_detail, name='api_unit_detail'),
    path('api/module/<int:module_id>/start/', api_views.api_start_module, name='api_start_module'),
    path('api/module/<int:module_id>/complete/', api_views.api_complete_module, name='api_complete_module'),

    # API endpoints DRF
    path('api/', include(router.urls)),
]
