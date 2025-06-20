# backend/django_apps/authentication/serializers.py
from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)
# REMOVED: rest_framework_simplejwt - Using Django+Supabase authentication now
from .models import CoachProfile, Review, UserFeedback, CookieConsent, CookieConsentLog
from django.contrib.auth import get_user_model

User = get_user_model()
from django.contrib.auth.password_validation import validate_password
from decimal import Decimal
from django.core.validators import validate_email
from apps.authentication.models import User
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(read_only=True, format='hex')
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    name = serializers.SerializerMethodField()
    picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        # Expose only necessary fields for viewing
        fields = [
            'public_id', 'username', 'first_name', 'last_name', 'email', 'birthday', 'gender',
            'profile_picture', 'picture', 'bio', 'native_language', 'target_language',
            'language_level', 'objectives', 'is_active', 'is_coach', 'is_subscribed',
            'is_superuser', 'is_staff', 'created_at', 'updated_at', 'name'
        ]
        # Mark sensitive fields as read-only
        read_only_fields = [
            'public_id', 'is_active', 'is_superuser', 'is_staff',
            'created_at', 'updated_at', 'name'
        ]

    def get_name(self, obj):
        """Generate full name from first_name and last_name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username or obj.email
    
    def get_picture(self, obj):
        """Get profile picture URL, prioritizing Supabase Storage"""
        # Priority: Supabase URL first, then local file
        if obj.profile_picture_url:
            return obj.profile_picture_url
        elif obj.profile_picture:
            try:
                return obj.profile_picture.url
            except Exception:
                return None
        return None

    def update(self, instance, validated_data):
        "To make an update to the user profile"
        for i in self.Meta.fields:
            if i not in self.Meta.read_only_fields and i in validated_data:
                setattr(instance, i, validated_data[i])
        instance.save()
        return instance

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'birthday', 'gender',
            'profile_picture', 'bio', 'native_language', 'target_language',
            'language_level', 'objectives', 'password', 'password2'
        ]


    def validate(self, attrs):
        """
        Validate the password and target language fields.

        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Your passwords must be the same."})
        if attrs['native_language'] == attrs['target_language']:
            raise serializers.ValidationError({"target_language": "Your target language must be different from your native language."})
        return attrs

    def create(self, validated_data):
        """
        Create a new user instance.

        """
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            birthday=validated_data.get('birthday'),
            gender=validated_data.get('gender'),
            profile_picture=validated_data.get('profile_picture'),
            bio=validated_data.get('bio'),
            native_language=validated_data.get('native_language'),
            target_language=validated_data.get('target_language'),
            language_level=validated_data.get('language_level'),
            objectives=validated_data.get('objectives'),
        )
        return user


class MeSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving basic user profile information
    """
    # Custom fields or transformations can be added here
    birthday = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'public_id',  # UUID
            'username',
            'email',
            'first_name',
            'last_name',
            'name',  # Full name
            'birthday',
            'gender',
            'native_language',
            'target_language',
            'language_level',
            'objectives',
            'is_coach',
            'is_active',
            'is_subscribed',
            'profile_picture',
            'bio',
            'created_at',
            'updated_at',
            'terms_accepted',
            'terms_accepted_at',
            'terms_version'
        ]
        read_only_fields = [
            'public_id',
            'email',
            'is_active',
            'is_coach',
            'is_subscribed',
            'created_at',
            'updated_at',
            'terms_accepted_at'
        ]

    def get_name(self, obj):
        """Generate full name"""
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_birthday(self, obj):
        """Retrieve user's birthday"""
        return obj.birthday

class TermsAcceptanceSerializer(serializers.Serializer):
    """
    Serializer for accepting terms and conditions
    """
    accept = serializers.BooleanField(required=True)
    version = serializers.CharField(required=False, default='v1.0')

    def validate_accept(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the terms and conditions to continue.")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        version = self.validated_data.get('version', 'v1.0')

        print(f"Saving terms acceptance for user: {user.email}")

        try:
            # Mark terms as accepted
            user.terms_accepted = True
            user.terms_accepted_at = timezone.now()
            user.terms_version = version
            user.save()
            print(f"Terms acceptance saved successfully for {user.email}")
            return user
        except Exception as e:
            print(f"Error saving terms acceptance: {str(e)}")
            raise


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'bio',
                 'birthday', 'native_language', 'target_language',
                 'language_level', 'objectives', 'gender']
        
    def update(self, instance, validated_data):
        logger.info(f"Updating user profile with data: {validated_data}")
        
        # Don't try to use "update_fields" that might be passed from the view
        # It should be a parameter to save(), not a field in the model
        if 'update_fields' in validated_data:
            validated_data.pop('update_fields')
        
        # Standard update logic - set each attribute
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Simply save without trying to specify update_fields
        instance.save()
        
        return instance
    def validate(self, data):
        """
        Custom validation
        """
        logger.info(f"Validating profile update data: {data}")

        # Vérification complète des langues qui prend en compte toutes les situations
        native_lang = data.get('native_language', getattr(self.instance, 'native_language', None))
        target_lang = data.get('target_language', getattr(self.instance, 'target_language', None))
        
        if native_lang and target_lang and native_lang == target_lang:
            raise serializers.ValidationError({
                'target_language': 'Target language cannot be the same as native language'
            })

        return data


# Cookie Consent Serializers

class CookieConsentSerializer(serializers.ModelSerializer):
    """Serializer for cookie consent"""
    
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    consent_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = CookieConsent
        fields = [
            'id', 'user_id', 'session_id', 'ip_address', 'version',
            'essential', 'analytics', 'functionality', 'performance',
            'language', 'consent_method', 'created_at', 'updated_at',
            'expires_at', 'is_revoked', 'revoked_at', 'revocation_reason',
            'consent_summary'
        ]
        read_only_fields = [
            'id', 'user_id', 'ip_address', 'user_agent', 'created_at', 
            'updated_at', 'is_revoked', 'revoked_at', 'revocation_reason'
        ]
    
    def get_consent_summary(self, obj):
        """Get consent summary"""
        return obj.get_consent_summary()
    
    def create(self, validated_data):
        """Create new consent record"""
        request = self.context.get('request')
        
        if request:
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            # Get user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Get session ID
            session_id = request.session.session_key
            
            validated_data.update({
                'ip_address': ip_address,
                'user_agent': user_agent,
                'session_id': session_id,
            })
            
            # Add user if authenticated
            if request.user.is_authenticated:
                validated_data['user'] = request.user
        
        return super().create(validated_data)


class CookieConsentCreateSerializer(serializers.Serializer):
    """Serializer for creating cookie consent via API"""
    
    essential = serializers.BooleanField(default=True, read_only=True)  # Always true
    analytics = serializers.BooleanField(default=False)
    functionality = serializers.BooleanField(default=False)
    performance = serializers.BooleanField(default=False)
    language = serializers.CharField(max_length=10, default='fr')
    version = serializers.CharField(max_length=10, default='1.0')
    consent_method = serializers.ChoiceField(
        choices=CookieConsent._meta.get_field('consent_method').choices,
        default='api'
    )
    
    def create(self, validated_data):
        """Create consent record"""
        request = self.context.get('request')
        
        # Get request metadata
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            session_id = request.session.session_key
            
            consent_data = {
                'essential': True,  # Always true
                'analytics': validated_data.get('analytics', False),
                'functionality': validated_data.get('functionality', False),
                'performance': validated_data.get('performance', False),
                'language': validated_data.get('language', 'fr'),
                'version': validated_data.get('version', '1.0'),
                'consent_method': validated_data.get('consent_method', 'api'),
                'ip_address': ip_address,
                'user_agent': user_agent,
                'session_id': session_id,
            }
            
            # Add user if authenticated
            if request.user.is_authenticated:
                consent_data['user'] = request.user
            
            consent = CookieConsent.objects.create(**consent_data)
            
            # Log the creation
            CookieConsentLog.objects.create(
                consent=consent,
                action='created',
                new_values=consent_data,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return consent
        
        raise serializers.ValidationError("Request context is required")


class CookieConsentLogSerializer(serializers.ModelSerializer):
    """Serializer for cookie consent logs"""
    
    consent_id = serializers.UUIDField(source='consent.id', read_only=True)
    
    class Meta:
        model = CookieConsentLog
        fields = [
            'id', 'consent_id', 'action', 'old_values', 'new_values',
            'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CookieConsentStatsSerializer(serializers.Serializer):
    """Serializer for cookie consent statistics"""
    
    total_consents = serializers.IntegerField()
    accept_all = serializers.IntegerField()
    essential_only = serializers.IntegerField()
    custom = serializers.IntegerField()
    by_version = serializers.DictField()
    
    # Additional calculated fields
    accept_all_percentage = serializers.SerializerMethodField()
    essential_only_percentage = serializers.SerializerMethodField()
    custom_percentage = serializers.SerializerMethodField()
    
    def get_accept_all_percentage(self, obj):
        total = obj.get('total_consents', 0)
        if total == 0:
            return 0
        return round((obj.get('accept_all', 0) / total) * 100, 2)
    
    def get_essential_only_percentage(self, obj):
        total = obj.get('total_consents', 0)
        if total == 0:
            return 0
        return round((obj.get('essential_only', 0) / total) * 100, 2)
    
    def get_custom_percentage(self, obj):
        total = obj.get('total_consents', 0)
        if total == 0:
            return 0
        return round((obj.get('custom', 0) / total) * 100, 2)


# === SETTINGS SERIALIZERS ===

class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences"""
    
    class Meta:
        model = User
        fields = [
            'email_notifications',
            'push_notifications', 
            'achievement_notifications',
            'lesson_notifications',
            'flashcard_notifications',
            'system_notifications',
        ]


class LearningSettingsSerializer(serializers.ModelSerializer):
    """Serializer for learning preferences"""
    
    class Meta:
        model = User
        fields = [
            'daily_goal',
            'weekday_reminders',
            'weekend_reminders', 
            'reminder_time',
            'speaking_exercises',
            'listening_exercises',
            'reading_exercises',
            'writing_exercises',
            'native_language',
            'target_language',
            'language_level',
            'objectives',
        ]
        
    def validate(self, data):
        """Validate that native and target languages are different"""
        native_lang = data.get('native_language', self.instance.native_language if self.instance else None)
        target_lang = data.get('target_language', self.instance.target_language if self.instance else None)
        
        if native_lang and target_lang and native_lang == target_lang:
            raise serializers.ValidationError(
                "Native language and target language must be different"
            )
        
        return data


class PrivacySettingsSerializer(serializers.ModelSerializer):
    """Serializer for privacy preferences"""
    
    class Meta:
        model = User
        fields = [
            'public_profile',
            'share_progress',
            'share_activity',
        ]


class AppearanceSettingsSerializer(serializers.ModelSerializer):
    """Serializer for appearance preferences"""
    
    class Meta:
        model = User
        fields = [
            'theme',
            'interface_language',
        ]


class GeneralSettingsSerializer(serializers.ModelSerializer):
    """Serializer for general user settings"""
    
    class Meta:
        model = User
        fields = [
            # Profile basics
            'username',
            'first_name', 
            'last_name',
            'bio',
            'gender',
            'birthday',
            
            # Language settings
            'native_language',
            'target_language',
            'language_level',
            'objectives',
            'interface_language',
            
            # Notification settings
            'email_notifications',
            'push_notifications',
            
            # Learning settings  
            'daily_goal',
            'reminder_time',
            
            # Appearance
            'theme',
            
            # Privacy
            'public_profile',
        ]
        
    def validate(self, data):
        """Validate settings data"""
        # Validate language differences
        native_lang = data.get('native_language', self.instance.native_language if self.instance else None)
        target_lang = data.get('target_language', self.instance.target_language if self.instance else None)
        
        if native_lang and target_lang and native_lang == target_lang:
            raise serializers.ValidationError({
                'target_language': "Target language and native language must be different"
            })
        
        return data


class SettingsStatsSerializer(serializers.Serializer):
    """Serializer for settings statistics"""
    
    total_users = serializers.IntegerField()
    notification_enabled_users = serializers.IntegerField()
    public_profile_users = serializers.IntegerField()
    daily_goal_average = serializers.FloatField()
    most_common_native_language = serializers.CharField()
    most_common_target_language = serializers.CharField()
    most_common_level = serializers.CharField()
    
    
class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, data):
        """Validate password change data"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': "New passwords don't match"
            })
        
        return data
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
