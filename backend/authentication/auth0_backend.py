# authentication/auth0_backend.py
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
import jwt
import requests
from django.conf import settings
from functools import lru_cache

# Get the custom user model or default Django user model
User = get_user_model()

class Auth0Authentication(authentication.BaseAuthentication):
    """
    Custom authentication class for Auth0 JWT validation.
    Implements Django REST Framework's BaseAuthentication.
    """
    
    def authenticate(self, request):
        """
        Main authentication method called by DRF for each request.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            tuple: (user, None) if authentication successful
            None: if no authentication attempted
            
        Raises:
            AuthenticationFailed: if authentication fails
        """
        # Get the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            # No auth header, skip authentication
            return None

        try:
            # Split "Bearer <token>"
            token = auth_header.split(' ')[1]
            # Verify and decode the JWT
            payload = self.verify_token(token)
            
            # Get or create Django user from Auth0 info
            user = self.get_or_create_user(payload)
            return (user, None)  # Authentication successful

        except (IndexError, jwt.InvalidTokenError) as e:
            # Token format invalid or JWT validation failed
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            # Any other error
            raise exceptions.AuthenticationFailed(str(e))

    @lru_cache(maxsize=1)
    def get_jwks(self):
        """
        Fetch and cache the JWKS (JSON Web Key Set) from Auth0.
        Uses @lru_cache to avoid repeated HTTP requests.
        
        Returns:
            dict: The JWKS from Auth0
        """
        jwks_url = f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
        return requests.get(jwks_url).json()

    def verify_token(self, token):
        """
        Verify the JWT token signature and claims.
        
        Args:
            token: The JWT token string
            
        Returns:
            dict: The decoded token payload
            
        Raises:
            AuthenticationFailed: if token is invalid
        """
        # Get the key set from Auth0
        jwks = self.get_jwks()
        
        # Get the key ID from token header
        unverified_header = jwt.get_unverified_header(token)
        
        # Find the matching signing key
        rsa_key = None
        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                rsa_key = key
                break
        
        if not rsa_key:
            raise exceptions.AuthenticationFailed('No matching key found')

        try:
            # Verify and decode the token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                audience=settings.AUTH0_AUDIENCE,  # API identifier in Auth0
                issuer=f'https://{settings.AUTH0_DOMAIN}/'  # Auth0 domain
            )
            return payload
            
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')

    def get_or_create_user(self, payload):
        """
        Get existing user or create new one from Auth0 info.
        
        Args:
            payload: The decoded JWT payload
            
        Returns:
            User: Django user object
            
        Raises:
            AuthenticationFailed: if email missing from token
        """
        # Get email from token
        email = payload.get('email')
        if not email:
            raise exceptions.AuthenticationFailed('No email in token')

        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': payload.get('nickname', email),
                'first_name': payload.get('given_name', ''),
                'last_name': payload.get('family_name', ''),
                'is_active': True
            }
        )
        
        if created:
            # Set default preferences for new users
            user.native_language = 'EN'  # Default language 
            user.language_level = 'A1'   # Default level
            user.save()
            
        return user