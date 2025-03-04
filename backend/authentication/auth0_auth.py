# authentication/auth0_authentication.py
import jwt
import json
import requests
from django.conf import settings
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model

User = get_user_model()

class Auth0Authentication(authentication.BaseAuthentication):
    """
    Simplified Authentication for DRF using Auth0 JWT tokens.
    """
    
    def authenticate(self, request):
        # Get the auth header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None

        # Extract the token
        token = auth_header.split(' ')[1]
        
        try:
            # Get the user info directly from Auth0
            userinfo_response = requests.get(
                f'https://{settings.AUTH0_DOMAIN}/userinfo',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if not userinfo_response.ok:
                raise exceptions.AuthenticationFailed('Failed to get user info')
            
            user_info = userinfo_response.json()
            if 'email' not in user_info:
                raise exceptions.AuthenticationFailed('Email not found in user info')
            
            # Get or create the user
            user, created = User.objects.get_or_create(
                email=user_info['email'],
                defaults={
                    'username': user_info.get('nickname', user_info['email'].split('@')[0]),
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', '')
                }
            )
            
            # Update user data if it changed
            if not created:
                update_fields = []
                if 'nickname' in user_info and user.username != user_info['nickname']:
                    user.username = user_info['nickname']
                    update_fields.append('username')
                if 'given_name' in user_info and user.first_name != user_info['given_name']:
                    user.first_name = user_info['given_name']
                    update_fields.append('first_name')
                if 'family_name' in user_info and user.last_name != user_info['family_name']:
                    user.last_name = user_info['family_name']
                    update_fields.append('last_name')
                
                if update_fields:
                    user.save(update_fields=update_fields)
            
            return (user, token)
        
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            raise exceptions.AuthenticationFailed(str(e))
    
    def authenticate_header(self, request):
        return 'Bearer'