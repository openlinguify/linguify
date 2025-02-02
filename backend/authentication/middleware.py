from django.http import JsonResponse
from django.conf import settings
import jwt
from urllib.parse import urlparse
import logging
from authentication.models import User
import requests
import json

logger = logging.getLogger(__name__)

class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._jwks = None

    def get_jwks(self):
        """Cache and return JWKS from Auth0"""
        if self._jwks is None:
            jwks_url = f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
            self._jwks = requests.get(jwks_url).json()
        return self._jwks

    def get_rsa_key(self, token):
        """Get the RSA key from JWKS matching the token's key ID"""
        try:
            jwks = self.get_jwks()
            unverified_header = jwt.get_unverified_header(token)
            for key in jwks['keys']:
                if key['kid'] == unverified_header['kid']:
                    return {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'n': key['n'],
                        'e': key['e']
                    }
        except Exception as e:
            logger.error(f"Error getting RSA key: {str(e)}")
            return None
        return None

    def process_token(self, request, auth_header):
        """Process the auth token if present"""
        try:
            # Extract token
            token_parts = auth_header.split()
            if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
                return None

            token = token_parts[1]

            # Get the RSA key for verification
            rsa_key = self.get_rsa_key(token)
            if not rsa_key:
                return None

            # Verify token with RSA key
            payload = jwt.decode(
                token,
                jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(rsa_key)),
                algorithms=['RS256'],
                audience=settings.AUTH0_AUDIENCE,
                issuer=f'https://{settings.AUTH0_DOMAIN}/'
            )

            # Create or update user if email is present
            if 'email' in payload:
                user, created = User.objects.get_or_create(
                    email=payload['email'],
                    defaults={
                        'username': payload.get('nickname', payload['email']),
                        'first_name': payload.get('given_name', ''),
                        'last_name': payload.get('family_name', ''),
                        'is_active': True
                    }
                )
                request.user = user

            # Add Auth0 user info to request
            request.auth0_user = payload
            return payload

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception) as e:
            logger.warning(f"Token processing error: {str(e)}")
            return None

    def __call__(self, request):
        # Get the token from the Authorization header if present
        auth_header = request.headers.get('Authorization')
        
        # If there's an auth header, try to process it
        if auth_header:
            self.process_token(request, auth_header)
        
        # Always continue with the request, regardless of auth status
        return self.get_response(request)