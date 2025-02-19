# backend/authentication/middleware.py
import json
import jwt
import requests
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

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
            print(f"JWT Error: {str(e)}")
            return None

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            token = auth_header.split()[1]
            payload = self.authenticate_token(token)
            
            if payload:
                user, _ = User.objects.get_or_create(
                    email=payload['email'],
                    defaults={
                        'username': payload.get('nickname', payload['email']),
                        'first_name': payload.get('given_name', ''),
                        'last_name': payload.get('family_name', '')
                    }
                )
                request.user = user

        return self.get_response(request)