# authentication/auth0_auth.py
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
import jwt
import requests

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

    token = parts[1]
    return token

class Auth0Authentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        """
        Authenticate request using Auth0 JWT.
        Returns None if authentication should not be attempted.
        """
        token = get_token_auth_header(request)
        if not token:
            return None

        try:
            jwks = requests.get(f'https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json').json()
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

            if rsa_key:
                try:
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms=['RS256'],
                        audience=settings.AUTH0_AUDIENCE,
                        issuer=f'https://{settings.AUTH0_DOMAIN}/'
                    )
                    return (payload, None)
                except jwt.ExpiredSignatureError:
                    raise exceptions.AuthenticationFailed('Token has expired')
                except Exception as e:
                    raise exceptions.AuthenticationFailed(f'Invalid token: {str(e)}')

            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception:
            return None