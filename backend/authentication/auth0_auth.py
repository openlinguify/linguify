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

class Auth0Authentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '').split()
        if not auth_header or auth_header[0].lower() != 'bearer':
            return None

        token = auth_header[1]
        try:
            # Get JWKS from Auth0
            jwks_url = f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json'
            jwks_response = requests.get(jwks_url)
            jwks = jwks_response.json()

            # Get the key
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in jwks['keys']:
                if key['kid'] == unverified_header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'n': key['n'],
                        'e': key['e']
                    }
                    break

            if not rsa_key:
                raise exceptions.AuthenticationFailed('No matching key found')

            # Verify token
            try:
                # Convert the key to proper format
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(rsa_key))
                
                # Decode and verify the token
                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=['RS256'],
                    audience=settings.AUTH0_AUDIENCE,
                    issuer=f'https://{settings.AUTH0_DOMAIN}/'
                )
            except jwt.ExpiredSignatureError:
                raise exceptions.AuthenticationFailed('Token has expired')
            except jwt.JWTClaimsError:
                raise exceptions.AuthenticationFailed('Invalid claims')
            except jwt.JWTError:
                raise exceptions.AuthenticationFailed('Invalid token')

            # Get user info from Auth0
            userinfo_response = requests.get(
                f'https://{settings.AUTH0_DOMAIN}/userinfo',
                headers={'Authorization': f'Bearer {token}'}
            )

            if not userinfo_response.ok:
                raise exceptions.AuthenticationFailed('Failed to get user info')

            user_info = userinfo_response.json()
            if 'email' not in user_info:
                raise exceptions.AuthenticationFailed('Email not found in user info')

            # Get or create user
            user, _ = User.objects.get_or_create(
                email=user_info['email'],
                defaults={
                    'username': user_info.get('nickname', user_info['email'].split('@')[0]),
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', '')
                }
            )

            logger.info(f"Successfully authenticated user: {user.email}")
            return (user, token)

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            raise exceptions.AuthenticationFailed(str(e))

    def authenticate_header(self, request):
        return 'Bearer'
    


