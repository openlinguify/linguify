# django_apps/authentication/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'user_type')
        extra_kwargs = {
            'email': {'required': True},
            'user_type': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            user_type=validated_data['user_type']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(
        max_length=128, write_only=True
    )

    def validate(self, attrs):
        username = attrs.get('username', None)
        password = attrs.get('password', None)

        if username is None:
            raise serializers.ValidationError(
                'An username is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = User.objects.filter(username=username).first()

        if user is None:
            raise serializers.ValidationError(
                'A user with this username was not found.'
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                'The provided password is incorrect.'
            )

        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

