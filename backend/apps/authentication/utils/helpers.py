# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Fonctions utilitaires pour l'authentification
# TODO: Migrer depuis helpers.py

def get_user_profile_picture_url(user):
    """Récupère l'URL de la photo de profil d'un utilisateur"""
    # TODO: Implémenter
    pass

def send_notification_email(user, subject, message):
    """Envoie un email de notification"""
    # TODO: Implémenter
    pass

def clean_username(username):
    """Nettoie un nom d'utilisateur"""
    # TODO: Implémenter
    return username

def get_profile_picture_urls(user):
    """Récupère les URLs de photos de profil pour différentes tailles"""
    # TODO: Implémenter - placeholder pour éviter les erreurs
    return {
        'small': None,
        'medium': None, 
        'large': None,
        'optimized': None,
        'original': None
    }

def get_profile_picture_html(user, size='medium'):
    """Génère le HTML pour la photo de profil d'un utilisateur"""
    # TODO: Implémenter - placeholder pour éviter les erreurs
    return f'<img src="" alt="Photo de profil" class="profile-picture-{size}" />'