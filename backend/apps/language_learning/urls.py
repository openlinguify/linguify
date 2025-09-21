"""
URLs configuration for language_learning app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import learning_progress_views, template_views, settings_views, setup_views

app_name = 'language_learning'

router = DefaultRouter()
router.register(r'languages', views.LanguageViewSet, basename='language')
router.register(r'user-languages', views.UserLanguageViewSet, basename='user-language')
router.register(r'course-units', views.CourseUnitViewSet, basename='course-unit')
router.register(r'module-progress', views.ModuleProgressViewSet, basename='module-progress')
router.register(r'user-progress', views.UserCourseProgressViewSet, basename='user-progress')
router.register(r'learning-profile', views.UserLearningProfileViewSet, basename='learning-profile')
router.register(r'learning-interface', views.LearningInterfaceViewSet, basename='learning-interface')

urlpatterns = [
    # Configuration initiale pour nouveaux utilisateurs qui viennent d'installer l'application depuis l'app store.
    path('setup/', setup_views.learning_setup, name='learning_setup'),
    path('setup/skip/', setup_views.skip_setup, name='skip_setup'),
    path('profile/settings/', setup_views.profile_settings, name='profile_settings'),

    # Main pages
    path('', template_views.learning_interface, name='home'),
    path('progress/', learning_progress_views.progress_view, name='progress'),

    # HTMX Partials endpoints
    path('partials/navbar/', template_views.navbar_partial, name='navbar_partial'),
    path('partials/progress/', template_views.progress_panel_partial, name='progress_panel_partial'),
    path('partials/units/', template_views.units_list_partial, name='units_list_partial'),
    path('learn/', template_views.learning_interface, name='learning_interface'),
    path('api/refresh-progress/', template_views.refresh_progress, name='refresh_progress'),
    path('unit/<int:unit_id>/modules/', template_views.unit_modules, name='unit_modules'),
    path('module/<int:module_id>/start/', template_views.start_module, name='start_module'),
    path('module/<int:module_id>/complete/', template_views.complete_module, name='complete_module'),

    # Settings pages
    path('settings/', settings_views.language_learning_settings, name='settings'),

    # API endpoints DRF
    path('api/', include(router.urls)),
]
