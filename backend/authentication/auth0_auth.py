# authentication/auth0_auth.py
import jwt
import json
import logging
import requests
from django.conf import settings
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header"""
    auth = request.headers.get("Authorization", None)
    if not auth:
        return None

    parts = auth.split()

    if parts[0].lower() != "bearer":
        return None
    elif len(parts) == 1:
        raise exceptions.AuthenticationFailed("Token not found")
    elif len(parts) > 2:
        raise exceptions.AuthenticationFailed("Authorization header must be Bearer token")

    return parts[1]

def get_user_info(token):
    """Get user info from Auth0"""
    try:
        user_info_url = f'https://{settings.AUTH0_DOMAIN}/userinfo'
        response = requests.get(
            user_info_url,
            headers={'Authorization': f'Bearer {token}'}
        )
        if response.ok:
            return response.json()
        logger.error(f"Failed to get user info: {response.status_code}")
        return None
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        return None

class Auth0Authentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        """
        Authenticate request using Auth0 JWT.
        Returns None if authentication should not be attempted.
        """
        try:
            token = get_token_auth_header(request)
            if not token:
                return None

            # Get JWKS
            jwks = requests.get(
                f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
            ).json()
            
            # Get header and verify token
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = next(
                (key for key in jwks['keys'] if key['kid'] == unverified_header['kid']),
                None
            )
            
            if not rsa_key:
                raise exceptions.AuthenticationFailed('No matching key found')

            try:
                payload = jwt.decode(
                    token,
                    jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(rsa_key)),
                    algorithms=['RS256'],
                    audience=settings.AUTH0_AUDIENCE,
                    issuer=f'https://{settings.AUTH0_DOMAIN}/'
                )
            except jwt.ExpiredSignatureError:
                raise exceptions.AuthenticationFailed('Token has expired')
            except jwt.InvalidTokenError as e:
                raise exceptions.AuthenticationFailed(f'Invalid token: {str(e)}')

            # Get additional user info from Auth0
            user_info = get_user_info(token)
            if not user_info or 'email' not in user_info:
                raise exceptions.AuthenticationFailed('Could not get user info')

            # Get or create user
            user, created = User.objects.get_or_create(
                email=user_info['email'],
                defaults={
                    'username': user_info.get('nickname') or user_info['email'].split('@')[0],
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', '')
                }
            )

            # Update user info if needed
            if not created:
                updates = {}
                if user_info.get('nickname') and user.username != user_info['nickname']:
                    updates['username'] = user_info['nickname']
                if user_info.get('given_name') and user.first_name != user_info['given_name']:
                    updates['first_name'] = user_info['given_name']
                if user_info.get('family_name') and user.last_name != user_info['family_name']:
                    updates['last_name'] = user_info['family_name']
                
                if updates:
                    for key, value in updates.items():
                        setattr(user, key, value)
                    user.save(update_fields=list(updates.keys()))

            return (user, token)

        except exceptions.AuthenticationFailed:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None