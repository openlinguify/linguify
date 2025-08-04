# Serializers pour les modèles de profil
from rest_framework import serializers
from ..models import User

class ProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'profile_picture', 'phone_number', 'bio', 'birthday', 'gender',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'created_at', 'updated_at']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour du profil"""
    
    class Meta:
        model = User
        fields = [
            'bio', 'profile_picture', 'phone_number',
            'birthday', 'gender'
        ]
    
    def validate_profile_picture(self, value):
        if value and value.size > 5 * 1024 * 1024:  # 5MB max
            raise serializers.ValidationError("L'image est trop volumineuse (max 5MB)")
        return value