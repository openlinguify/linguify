# backend/authentication/middleware.py
import json
import jwt
import logging
import requests
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()
logger = logging.getLogger(__name__)

def get_user_info(token):
    """Get user info from Auth0"""
    try:
        user_info_url = f'https://{settings.AUTH0_DOMAIN}/userinfo'
        response = requests.get(
            user_info_url,
            headers={'Authorization': f'Bearer {token}'}
        )
        if response.status_code == 200:
            return response.json()
        logger.error(f"Failed to get user info: {response.status_code}")
        return None
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        return None

class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwks = None

    def fetch_jwks(self):
        if not self.jwks:
            jwks_url = f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
            response = requests.get(jwks_url)
            self.jwks = response.json()
        return self.jwks

    def authenticate_token(self, token):
        try:
            jwks = self.fetch_jwks()
            header = jwt.get_unverified_header(token)
            key = next(k for k in jwks['keys'] if k['kid'] == header['kid'])
            
            return jwt.decode(
                token,
                jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key)),
                algorithms=['RS256'],
                audience=settings.AUTH0_AUDIENCE,
                issuer=f'https://{settings.AUTH0_DOMAIN}/'
            )
        except Exception as e:
            logger.error(f"JWT Error: {str(e)}")
            return None

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            try:
                token = auth_header.split()[1]
                payload = self.authenticate_token(token)
                
                if payload:
                    # Get user info from Auth0 for complete profile
                    user_info = get_user_info(token)
                    
                    if user_info and user_info.get('email'):
                        user, created = User.objects.get_or_create(
                            email=user_info['email'],
                            defaults={
                                'username': user_info.get('nickname') or user_info['email'].split('@')[0],
                                'first_name': user_info.get('given_name', ''),
                                'last_name': user_info.get('family_name', '')
                            }
                        )
                        
                        # Update user info if it has changed
                        if not created:
                            update_fields = []
                            if user_info.get('nickname') and user.username != user_info['nickname']:
                                user.username = user_info['nickname']
                                update_fields.append('username')
                            if user_info.get('given_name') and user.first_name != user_info['given_name']:
                                user.first_name = user_info['given_name']
                                update_fields.append('first_name')
                            if user_info.get('family_name') and user.last_name != user_info['family_name']:
                                user.last_name = user_info['family_name']
                                update_fields.append('last_name')
                            
                            if update_fields:
                                user.save(update_fields=update_fields)
                        
                        request.user = user
                    else:
                        logger.error("No email found in user info")
                else:
                    logger.error("Invalid token")
            except Exception as e:
                logger.error(f"Error in JWT middleware: {str(e)}")

        return self.get_response(request)