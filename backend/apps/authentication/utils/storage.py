# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Utilitaires de stockage pour l'authentification
# TODO: Migrer depuis storage.py

from django.core.files.storage import default_storage, FileSystemStorage
from django.conf import settings
import os

class ProfilePictureStorage:
    """Gestionnaire de stockage pour les photos de profil"""
    # TODO: Implémenter
    pass

class ProfileStorage(FileSystemStorage):
    """Gestionnaire de stockage pour les profils"""
    
    def __init__(self, *args, **kwargs):
        # Utiliser le dossier media/profiles pour les photos de profil
        kwargs.setdefault('location', os.path.join(settings.MEDIA_ROOT, 'profiles'))
        kwargs.setdefault('base_url', f"{settings.MEDIA_URL}profiles/")
        super().__init__(*args, **kwargs)
    
    def deconstruct(self):
        """Nécessaire pour la sérialisation des migrations Django"""
        return (
            'apps.authentication.utils.storage.ProfileStorage',
            [],
            {}
        )

class SecureUniqueFileStorage:
    """Gestionnaire de stockage sécurisé avec noms de fichiers uniques"""
    # TODO: Implémenter - placeholder pour éviter les erreurs
    pass

def upload_profile_picture(user, picture):
    """Upload une photo de profil"""
    # TODO: Implémenter
    pass

def delete_profile_picture(user):
    """Supprime une photo de profil"""
    # TODO: Implémenter
    pass