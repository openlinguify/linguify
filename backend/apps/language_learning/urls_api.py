"""
API URLs configuration for language_learning app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for DRF ViewSets
router = DefaultRouter()
router.register(r'languages', views.LanguageViewSet, basename='language')
router.register(r'user-languages', views.UserLanguageViewSet, basename='user-language')
router.register(r'items', views.LanguagelearningItemViewSet, basename='languagelearning-item')
router.register(r'settings', views.LanguageLearningSettingsViewSet, basename='language-learning-settings')

app_name = 'language_learning_api'

urlpatterns = [
    # API endpoints (fonction based views)
    path('items/', views.api_items, name='api_items'),
    path('start_language/', views.start_language_learning, name='start_language'),
    path('settings/', views.get_user_language_learning_settings, name='user_settings'),
    
    # DRF ViewSets
    path('', include(router.urls)),
]