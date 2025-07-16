# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Validateurs pour l'authentification
# TODO: Migrer depuis validators.py

def validate_username(username):
    """Valide un nom d'utilisateur"""
    # TODO: Implémenter
    pass

def validate_profile_picture(picture):
    """Valide une photo de profil"""
    # TODO: Implémenter
    pass

def validate_password_strength(password):
    """Valide la force d'un mot de passe"""
    # TODO: Implémenter
    pass

def validate_username_format(username):
    """Valide le format d'un nom d'utilisateur"""
    # TODO: Implémenter - placeholder pour éviter les erreurs
    return username

def is_username_available(username, exclude_user=None):
    """
    Check if a username is available for registration.
    
    Args:
        username (str): Username to check
        exclude_user (User, optional): User to exclude from the check (for profile updates)
    
    Returns:
        dict: Result with 'available' boolean and 'message' string
    """
    import re
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    if not username:
        return {
            'available': False,
            'message': 'Le nom d\'utilisateur ne peut pas être vide'
        }
    
    username = username.strip()
    
    # Check minimum length
    if len(username) < 3:
        return {
            'available': False,
            'message': 'Le nom d\'utilisateur doit contenir au moins 3 caractères'
        }
    
    # Check maximum length
    if len(username) > 30:
        return {
            'available': False,
            'message': 'Le nom d\'utilisateur ne peut pas dépasser 30 caractères'
        }
    
    # Check for valid characters (letters, numbers, underscores, hyphens)
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return {
            'available': False,
            'message': 'Le nom d\'utilisateur ne peut contenir que des lettres, chiffres, _ et -'
        }
    
    # Check that it contains at least one alphanumeric character
    if not re.search(r'[a-zA-Z0-9]', username):
        return {
            'available': False,
            'message': 'Le nom d\'utilisateur doit contenir au moins une lettre ou un chiffre'
        }
    
    # Check if username already exists
    query = User.objects.filter(username__iexact=username)
    if exclude_user:
        query = query.exclude(pk=exclude_user.pk)
    
    if query.exists():
        return {
            'available': False,
            'message': 'Ce nom d\'utilisateur est déjà pris'
        }
    
    return {
        'available': True,
        'message': 'Ce nom d\'utilisateur est disponible'
    }