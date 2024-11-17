# backend/django_apps/auth/serializers/login.py

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from django_apps.authentication.serializers import UserSerializer


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        # Include user details in the response
        user_data = UserSerializer(self.user).data
        # Removing sensitive information
        user_data.pop('is_superuser', None)
        user_data.pop('is_staff', None)
        data.update(user_data)

        # Update last login if setting is enabled
        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data

    @classmethod
    def get_token(cls, user):
        # Override get_token to ensure the correct token is created
        return super().get_token(user)
