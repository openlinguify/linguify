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

    def __call__(self, request):
        # URLs that don't need authentication
        public_paths = [
            '/admin/',
            '/api/v1/auth/login/',
            '/api/v1/auth/callback/',
            '/api/v1/auth/logout/',
            '/api/v1/auth/user/',
            '/api/v1/course/units/',
            '/api/v1/course/lesson/',
            '/api/v1/course/content-lesson/',
            '/api/v1/course/content-lesson/<int:lesson_id>/',
            'api/v1/revision/flashcards/',

            '/favicon.ico',
            '/static/',
            '/_next/',
            '/assets/'
        ]

        private_paths = [
            '/api/v1/chat/',
            'api/v1/settings/',
            '/api/v1/auth/users/profile/',
        ]

        # Check if the path is public
        current_path = urlparse(request.path).path
        
        # Allow public paths without authentication
        if any(current_path.startswith(path) for path in public_paths):
            return self.get_response(request)

        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.debug(f'No authorization header for path: {current_path}')
            return JsonResponse({'error': 'No authorization header'}, status=401)

        try:
            # Extract token
            token_parts = auth_header.split()
            if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
                return JsonResponse({'error': 'Invalid authorization header'}, status=401)

            token = token_parts[1]

            # Get the RSA key for verification
            rsa_key = self.get_rsa_key(token)
            if not rsa_key:
                return JsonResponse({'error': 'Unable to find appropriate key'}, status=401)

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

        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired token for path: {current_path}")
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token for path: {current_path}")
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except Exception as e:
            logger.error(f"JWT error for path {current_path}: {str(e)}")
            return JsonResponse({'error': str(e)}, status=401)

        # Check if path requires authentication
        if any(current_path.startswith(path) for path in private_paths):
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required for this resource'}, status=401)

        return self.get_response(request)