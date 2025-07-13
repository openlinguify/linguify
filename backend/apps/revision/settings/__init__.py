"""
Settings module for Revision app

Ce module contient tous les paramètres et configurations spécifiques
à l'application Révision.
"""

# Import des modèles pour les enregistrer avec Django
from .models import RevisionSettings, RevisionSessionConfig

# Import des vues et serializers pour l'exposition d'API
try:
    from .serializers import RevisionSettingsSerializer, RevisionSessionConfigSerializer
    from .views import RevisionSettingsViewSet
except ImportError:
    # Les serializers/views seront créés plus tard
    pass

__all__ = [
    'RevisionSettings',
    'RevisionSessionConfig',
]

def get_user_settings(user):
    """
    Fonction utilitaire pour récupérer les paramètres d'un utilisateur
    """
    return RevisionSettings.get_or_create_for_user(user)

def get_settings_config():
    """
    Retourne la configuration des paramètres pour l'intégration saas_web
    """
    from ..apps import RevisionConfig
    return RevisionConfig.get_settings_config()