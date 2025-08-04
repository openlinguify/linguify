# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Validateurs pour l'authentification
# TODO: Migrer depuis validators.py

def validate_username(username):
    """Valide un nom d'utilisateur"""
    # TODO: Implémenter
    pass

def validate_profile_picture(picture):
    """
    Valide une photo de profil avec contrôles de sécurité renforcés
    
    Args:
        picture: Fichier uploadé
        
    Raises:
        ValidationError: Si la validation échoue
    """
    from django.core.exceptions import ValidationError
    from django.conf import settings
    from PIL import Image
    import os
    
    if not picture:
        return
    
    # Paramètres de validation
    max_size = getattr(settings, 'PROFILE_PICTURE_MAX_SIZE', 5 * 1024 * 1024)  # 5MB
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    min_width = getattr(settings, 'PROFILE_PICTURE_MIN_WIDTH', 100)
    min_height = getattr(settings, 'PROFILE_PICTURE_MIN_HEIGHT', 100)
    max_width = getattr(settings, 'PROFILE_PICTURE_MAX_WIDTH', 4000)
    max_height = getattr(settings, 'PROFILE_PICTURE_MAX_HEIGHT', 4000)
    
    # 1. Vérifier la taille du fichier
    if picture.size > max_size:
        raise ValidationError(f"Le fichier est trop volumineux ({picture.size} bytes). Taille maximale: {max_size} bytes.")
    
    # 2. Vérifier l'extension du fichier
    file_ext = picture.name.lower().split('.')[-1] if '.' in picture.name else ''
    if f'.{file_ext}' not in allowed_extensions:
        raise ValidationError(f"Extension de fichier non autorisée. Extensions autorisées: {', '.join(allowed_extensions)}")
    
    # 3. Vérifier le type MIME
    if hasattr(picture, 'content_type') and picture.content_type not in allowed_types:
        raise ValidationError(f"Type de fichier non autorisé: {picture.content_type}. Types autorisés: {', '.join(allowed_types)}")
    
    # 4. Vérifier que c'est une image valide avec PIL
    try:
        picture.seek(0)
        image = Image.open(picture)
        image.verify()
        picture.seek(0)
        
        # Vérifier les dimensions
        image = Image.open(picture)
        width, height = image.size
        
        if width < min_width or height < min_height:
            raise ValidationError(f"Image trop petite ({width}x{height}). Dimensions minimales: {min_width}x{min_height}")
        
        if width > max_width or height > max_height:
            raise ValidationError(f"Image trop grande ({width}x{height}). Dimensions maximales: {max_width}x{max_height}")
            
        # Vérifier le format d'image
        if image.format not in ['JPEG', 'PNG']:
            raise ValidationError(f"Format d'image non supporté: {image.format}. Formats supportés: JPEG, PNG")
            
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError("Le fichier n'est pas une image valide.")
    
    finally:
        picture.seek(0)

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