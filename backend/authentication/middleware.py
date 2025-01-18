from django.http import JsonResponse
from django.conf import settings
import jwt
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

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
            '/api/v1/course/lesson/<int:lesson_id>/content/',
            
            
            '/favicon.ico',
            '/static/',
            '/_next/',
            '/assets/'
        ]

        # Static files and other common resources
        static_extensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']
        # Check if the path is public
        current_path = urlparse(request.path).path
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

            # Verify token
            payload = jwt.decode(
                token,
                options={"verify_signature": False},  # For Auth0 public key verification
                audience=settings.AUTH0_AUDIENCE,
                issuer=f'https://{settings.AUTH0_DOMAIN}/'
            )

            # Add user info to request
            request.auth0_user = payload

        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired token for path: {current_path}")
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            logger.warning(f"Invalid token for path: {current_path}")
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except Exception as e:
            logger.error(f"JWT error for path {current_path}: {str(e)}")
            return JsonResponse({'error': str(e)}, status=401)

        return self.get_response(request)