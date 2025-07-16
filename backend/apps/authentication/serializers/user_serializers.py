# Serializers pour le modèle User
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import User

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer principal pour le modèle User"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'native_language', 'target_language', 'language_level',
            'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'utilisateur"""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'native_language', 'target_language'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour d'utilisateur"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email',
            'native_language', 'target_language', 'language_level'
        ]