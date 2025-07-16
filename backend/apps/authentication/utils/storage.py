# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Utilitaires de stockage pour l'authentification
# TODO: Migrer depuis storage.py

from django.core.files.storage import default_storage

class ProfilePictureStorage:
    """Gestionnaire de stockage pour les photos de profil"""
    # TODO: Implémenter
    pass

class ProfileStorage:
    """Gestionnaire de stockage pour les profils - placeholder"""
    # TODO: Implémenter - placeholder pour éviter les erreurs
    pass

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