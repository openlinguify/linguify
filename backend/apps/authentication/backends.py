# backend/apps/authentication/backends.py
"""
Custom Authentication Backend for Linguify

This module provides a flexible authentication backend that allows users to log in
using either their email address or username, improving user experience by accepting
both authentication methods.

Purpose:
- Extends Django's default ModelBackend to support dual login methods
- Maintains security best practices (timing attack prevention)
- Provides case-insensitive authentication for better UX

Usage in settings.py:
AUTHENTICATION_BACKENDS = [
    'apps.authentication.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',  # Fallback
]
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

# Get the User model (supports custom user models)
User = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login with either
    their email address or username.
    
    This backend extends Django's ModelBackend to provide flexible login options:
    - Users can authenticate with their username
    - Users can authenticate with their email address
    - Case-insensitive matching for better user experience
    - Maintains security against timing attacks
    
    Example usage:
        # Both of these will work for the same user:
        authenticate(username='john@example.com', password='secret')
        authenticate(username='johnsmith', password='secret')
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user using either username or email.
        
        Args:
            request: The HTTP request object
            username: The username or email provided by the user
            password: The password provided by the user
            **kwargs: Additional keyword arguments
            
        Returns:
            User object if authentication succeeds, None otherwise
            
        Security considerations:
        - Uses case-insensitive matching (iexact) for better UX
        - Prevents timing attacks by running password hasher even for non-existent users
        - Handles edge cases like multiple users with same email (shouldn't happen)
        """
        # Extract username from kwargs if not provided directly
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
            
        # Both username and password are required
        if username is None or password is None:
            return None
        
        try:
            # Search for user by username OR email (case-insensitive)
            # Q object allows complex database queries with OR conditions
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            # Security: Run password hasher even when user doesn't exist
            # This prevents timing attacks where attackers could determine
            # if a username/email exists by measuring response time
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Edge case: Multiple users found (shouldn't happen with proper constraints)
            # This could occur if database constraints are missing or corrupted
            return None
        else:
            # Verify password and check if user can authenticate
            # user_can_authenticate() checks if user is active, not staff-only, etc.
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
                
        # Authentication failed
        return None