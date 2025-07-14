"""
Centralized validation functions for authentication app
"""
import re
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


def validate_username_format(username):
    """
    Validates username format requirements.
    
    Args:
        username (str): The username to validate
        
    Raises:
        ValidationError: If username doesn't meet format requirements
        
    Returns:
        str: The validated username
    """
    if not username:
        raise ValidationError("Username cannot be empty.")
    
    username = username.strip()
    
    if len(username) < 3:
        raise ValidationError("Username must be at least 3 characters long.")
    
    # Must contain at least one letter or number
    if not re.search(r'[a-zA-Z0-9]', username):
        raise ValidationError(
            "Le nom d'utilisateur doit contenir au moins une lettre ou un chiffre."
        )
    
    return username


def validate_username_uniqueness(username, exclude_user=None):
    """
    Validates that username is unique (case-insensitive).
    
    Args:
        username (str): The username to validate
        exclude_user (User, optional): User to exclude from uniqueness check
        
    Raises:
        ValidationError: If username is already taken
        
    Returns:
        str: The validated username
    """
    User = get_user_model()
    
    query = User.objects.filter(username__iexact=username)
    
    if exclude_user:
        query = query.exclude(pk=exclude_user.pk)
    
    if query.exists():
        raise ValidationError(f'Username "{username}" is already taken.')
    
    return username


def validate_username_complete(username, exclude_user=None):
    """
    Complete username validation including format and uniqueness.
    
    Args:
        username (str): The username to validate
        exclude_user (User, optional): User to exclude from uniqueness check
        
    Raises:
        ValidationError: If username is invalid
        
    Returns:
        str: The validated username
    """
    # First validate format
    username = validate_username_format(username)
    
    # Then validate uniqueness
    username = validate_username_uniqueness(username, exclude_user)
    
    return username


def is_username_available(username, exclude_user=None):
    """
    Check if username is available (format valid and unique).
    
    Args:
        username (str): The username to check
        exclude_user (User, optional): User to exclude from uniqueness check
        
    Returns:
        dict: {
            'available': bool,
            'message': str,
            'error_code': str (optional)
        }
    """
    try:
        validate_username_complete(username, exclude_user)
        return {
            'available': True,
            'message': 'Username available.'
        }
    except ValidationError as e:
        return {
            'available': False,
            'message': str(e),
            'error_code': 'validation_error'
        }