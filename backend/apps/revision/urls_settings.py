"""
URLs pour les paramètres de l'application Révision
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.settings_views import RevisionSettingsViewSet, RevisionSessionConfigViewSet

# Router pour les API REST
router = DefaultRouter()
router.register(r'settings', RevisionSettingsViewSet, basename='revision-settings')
router.register(r'session-configs', RevisionSessionConfigViewSet, basename='revision-session-configs')

app_name = 'revision_settings'

urlpatterns = [
    # API REST pour les paramètres
    path('api/', include(router.urls)),
    
    # URLs spécifiques pour l'intégration saas_web
    path('config/', RevisionSettingsViewSet.as_view({
        'get': 'list',
        'post': 'update',
        'patch': 'update',
    }), name='config'),
    
    path('presets/apply/', RevisionSettingsViewSet.as_view({
        'post': 'apply_preset'
    }), name='apply_preset'),
    
    path('stats/', RevisionSettingsViewSet.as_view({
        'get': 'stats'
    }), name='stats'),
]