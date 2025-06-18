from django.core.management.base import BaseCommand
from apps.authentication.storage import CreateProfileDirectories

class Command(CreateProfileDirectories):
    """
    Commande Django: create_profile_directories
    Crée les répertoires nécessaires pour le stockage des photos de profil
    
    Usage: python manage.py create_profile_directories
    """
    pass