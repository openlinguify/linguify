# backend/authentication/models.py
import os
import datetime
from uuid import uuid4
from typing import Any, Optional
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import QuerySet, Q
from django.http import Http404
from django.utils import timezone
from django.conf import settings
from PIL import Image

from .storage import ProfileStorage

LANGUAGE_CHOICES = [
    ('EN', 'English'),
    ('FR', 'French'),
    ('NL', 'Dutch'),
    ('DE', 'German'),
    ('ES', 'Spanish'),
    ('IT', 'Italian'),
    ('PT', 'Portuguese'),
]

LEVEL_CHOICES = [
    ('A1', 'A1'),
    ('A2', 'A2'),
    ('B1', 'B1'),
    ('B2', 'B2'),
    ('C1', 'C1'),
    ('C2', 'C2'),
]

OBJECTIVES_CHOICES = [
    ('Travel', 'Travel'),
    ('Business', 'Business'),
    ('Live Abroad', 'Live Abroad'),
    ('Exam', 'Exam'),
    ('For Fun', 'For Fun'),
    ('Work', 'Work'),
    ('School', 'School'),
    ('Study', 'Study'),
    ('Personal', 'Personal'),
]

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('N', 'Non-binary'),
    ('O', 'Other'),
    ('P', 'Prefer not to say'),
]

def validate_profile_picture(file):
    """
    Validates profile picture uploads by checking:
    - File size (max 5MB)
    - File type (only JPEG, PNG)
    - Minimum dimensions (200x200 pixels)
    """
    from django.conf import settings

    # Configure validation parameters
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
    max_size = getattr(settings, 'PROFILE_PICTURE_MAX_SIZE', 5 * 1024 * 1024)  # 5MB default
    min_width = getattr(settings, 'PROFILE_PICTURE_MIN_WIDTH', 200)
    min_height = getattr(settings, 'PROFILE_PICTURE_MIN_HEIGHT', 200)

    # Check file size
    if file.size > max_size:
        raise ValidationError(f"Profile picture file size must be under {max_size // (1024 * 1024)}MB.")

    # Check file type
    if hasattr(file, 'content_type') and file.content_type not in allowed_types:
        raise ValidationError("Only JPEG and PNG images are allowed.")

    # Check dimensions
    try:
        img = Image.open(file)

        # Ensure minimum size for good quality
        if img.width < min_width or img.height < min_height:
            raise ValidationError(f"Profile picture must be at least {min_width}x{min_height} pixels.")

        # Reset file pointer for further use
        file.seek(0)
    except Exception as e:
        raise ValidationError(f"Invalid image file: {str(e)}")
class UserManager(BaseUserManager):
    def get_object_by_public_id(self, public_id: str) -> Any:
        """
        Retrieve a user instance by public_id or raise Http404 if not found.
        """
        try:
            return self.get(public_id=public_id)
        except (ObjectDoesNotExist, ValueError, TypeError):
            raise Http404("User not found.")

    def create_user(
        self,
        username: str,
        email: str,
        password: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Create and return a `User` with an email, phone number, username, and password.
        """
        if not username:
            raise TypeError('Users must have a username.')
        if not email:
            raise TypeError('Users must have an email.')
        if not password:
            raise TypeError('Users must have a password.')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str,
        email: str,
        password: str,
        **kwargs
    ) -> Any:
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if not username:
            raise TypeError('Superusers must have a username.')
        if not email:
            raise TypeError('Superusers must have an email.')
        if not password:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def get_all_coaches(self) -> QuerySet:
        """
        Retrieve all active users who are coaches.

        Returns:
            QuerySet: A QuerySet containing all active users with the `is_coach` flag set to True.
        """
        return self.filter(is_coach=True, is_active=True)

    def search_by_email(self, email: str) -> QuerySet:
        """
        Search for users by email.

        Args:
            email (str): The email to search for.

        Returns:
            QuerySet: A QuerySet containing users whose email contains the given email string.
        """
        return self.filter(email__icontains=email)

    def search_by_username(self, username: str) -> QuerySet:
        """
        Search for users by username.

        Args:
            username (str): The username to search for.

        Returns:
            QuerySet: A QuerySet containing users whose username contains the given username string.
        """
        return self.filter(username__icontains=username)

    def search_by_name(self, name: str) -> QuerySet:
        """
        Search for users by first or last name.

        Args:
            name (str): The name to search for.

        Returns:
            QuerySet: A QuerySet containing users whose first or last name contains the given name string.
        """
        return self.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))

    def search_by_language(self, language: str) -> QuerySet:
        """
        Search for users by native or target language.

        Args:
            language (str): The language to search for.

        Returns:
            QuerySet: A QuerySet containing users whose native or target language matches the given language string.
        """
        return self.filter(Q(native_language=language) | Q(target_language=language))

    def search_by_level(self, level: str) -> QuerySet:
        """
        Search for users by language level.

        Args:
            level (str): The language level to search for.

        Returns:
            QuerySet: A QuerySet containing users whose language level matches the given level string.
        """
        return self.filter(language_level=level)


# Base User Model
class User(AbstractBaseUser, PermissionsMixin):
    # Explicitly set app_label to solve the Django model registration issue
    class Meta:
        app_label = 'authentication'
    
    id = models.AutoField(primary_key=True)
    public_id = models.UUIDField(db_index=True, default=uuid4, editable=False, unique=True)
    username = models.CharField(db_index=True, max_length=255, unique=True, blank=False, null=False)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(db_index=True, unique=True, blank=False, null=False)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    # in order to know if the user is active or not; if the user is not active, he/she can't log in to the platform
    # the user can be deactivated by the admin or by the user himself
    # the user progress will be saved even if the user is deactivated during a certain period of time (e.g. 6 months)
    # if the user is deactivated for more than 6 months, the user progress will be deleted
    is_active = models.BooleanField(null=False, default=True)
    is_subscribed = models.BooleanField(null=False, default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    # Fields for tracking account deletion with 30-day grace period
    is_pending_deletion = models.BooleanField(default=False, help_text="Whether the account is scheduled for deletion")
    deletion_scheduled_at = models.DateTimeField(null=True, blank=True, help_text="When the account deletion was requested")
    deletion_date = models.DateTimeField(null=True, blank=True, help_text="When the account will be permanently deleted")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Common fields for all users
    profile_picture = models.ImageField(
        upload_to='profiles',
        storage=ProfileStorage(),
        null=True,
        blank=True,
        validators=[validate_profile_picture]
    )
    # Supabase storage fields
    profile_picture_url = models.URLField(
        null=True,
        blank=True,
        help_text="URL de la photo de profil stockée dans Supabase"
    )
    profile_picture_filename = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Nom du fichier dans Supabase Storage"
    )
    bio = models.TextField(max_length=500, null=True, blank=True)
    native_language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default=LANGUAGE_CHOICES[0][0],
                                       help_text="Your native language")
    # Fields for language learners
    target_language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default=LANGUAGE_CHOICES[1][0],
                                      help_text="The language you want to learn")
    language_level = models.CharField(max_length=2, choices=LEVEL_CHOICES, default=LEVEL_CHOICES[0][0],
                                      help_text="Your language level")
    objectives = models.CharField(max_length=20, choices=OBJECTIVES_CHOICES, default=OBJECTIVES_CHOICES[0][0],
                                  help_text="Your learning objectives")
    is_coach = models.BooleanField(default=False)
    interface_language = models.CharField(max_length=10, default='en')
    theme = models.CharField(max_length=10, default='light')
    # settings fields
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    weekday_reminders = models.BooleanField(default=True)
    weekend_reminders = models.BooleanField(default=False)
    reminder_time = models.TimeField(default=datetime.time(18, 0))

    # learning settings fields
    speaking_exercises = models.BooleanField(default=True)
    listening_exercises = models.BooleanField(default=True)
    reading_exercises = models.BooleanField(default=True)
    writing_exercises = models.BooleanField(default=True)
    daily_goal = models.IntegerField(default=15, validators=[MinValueValidator(1)])

    # Private settings fields
    public_profile = models.BooleanField(default=True)
    share_progress = models.BooleanField(default=True)
    share_activity = models.BooleanField(default=False)

    # Terms and conditions acceptance fields
    terms_accepted = models.BooleanField(default=False, help_text='Whether the user has accepted the terms and conditions')
    terms_accepted_at = models.DateTimeField(null=True, blank=True, help_text='When the user accepted the terms and conditions')
    terms_version = models.CharField(max_length=10, null=True, blank=True, default='v1.0', help_text='Version of terms that was accepted')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    # Custom manager
    objects = UserManager()

    def update_profile(self, **kwargs):
        allowed_fields = {
            "first_name", "last_name", "bio", "profile_picture", "native_language",
            "target_language", "language_level", "objectives", "interface_language",
            "theme", "email_notifications", "push_notifications", "weekday_reminders",
            "weekend_reminders", "reminder_time", "speaking_exercises", "listening_exercises",
            "reading_exercises", "writing_exercises", "daily_goal", "public_profile",
            "share_progress", "share_activity", "terms_accepted", "terms_accepted_at", "terms_version"
        }
        
        # Check if trying to set target language same as native language
        if ('target_language' in kwargs and 'native_language' in kwargs and 
            kwargs['target_language'] == kwargs['native_language']):
            raise ValidationError('Target language cannot be the same as native language')
        
        # Check if setting only target language to match existing native language
        if ('target_language' in kwargs and 
            kwargs['target_language'] == self.native_language):
            raise ValidationError('Target language cannot be the same as native language')
        
        # Check if setting only native language to match existing target language
        if ('native_language' in kwargs and 
            kwargs['native_language'] == self.target_language):
            raise ValidationError('Native language cannot be the same as target language')
        
        for k, v in kwargs.items():
            if k in allowed_fields:
                setattr(self, k, v)
        
        self.save()

    @property
    def get_profile_picture_url(self):
        """
        Retourne l'URL de la photo de profil en priorisant Supabase sur le stockage local
        """
        # Prioriser Supabase Storage
        if self.profile_picture_url:
            return self.profile_picture_url
        
        # Fallback vers le stockage local Django
        if self.profile_picture:
            try:
                return self.profile_picture.url
            except Exception:
                return None
        
        return None
    
    def get_profile_picture_absolute_url(self, request):
        """
        Retourne l'URL absolue de la photo de profil pour les API
        """
        # Prioriser Supabase Storage (déjà absolu)
        if self.profile_picture_url:
            return self.profile_picture_url
        
        # Fallback vers le stockage local Django avec URL absolue
        if self.profile_picture:
            try:
                return request.build_absolute_uri(self.profile_picture.url)
            except Exception:
                return None
        
        return None

    def deactivate_user(self):
        self.is_active = False
        self.save()

    def reactivate_user(self):
        self.is_active = True
        self.save()
        
    def schedule_account_deletion(self, days_retention=30):
        """
        Schedule account deletion with a grace period.
        Account will be deactivated immediately but only permanently deleted after the grace period.
        """
        import datetime
        from django.utils import timezone
        
        # Calculate scheduled deletion date
        deletion_date = timezone.now() + datetime.timedelta(days=days_retention)
        
        # Mark account for deletion
        self.is_pending_deletion = True
        self.deletion_scheduled_at = timezone.now()
        self.deletion_date = deletion_date
        
        # Deactivate the account immediately
        self.is_active = False
        
        # Save each field individually to avoid update_fields issues
        try:
            # First try the normal way with update_fields
            self.save(update_fields=[
                'is_pending_deletion', 
                'deletion_scheduled_at', 
                'deletion_date', 
                'is_active'
            ])
        except Exception as e:
            # If that fails, fall back to a full save
            self.save()
        
        return {
            'scheduled_at': self.deletion_scheduled_at,
            'deletion_date': self.deletion_date
        }
    
    def cancel_account_deletion(self):
        """
        Cancel a scheduled account deletion and reactivate the account.
        """
        if not self.is_pending_deletion:
            return False
        
        self.is_pending_deletion = False
        self.deletion_scheduled_at = None
        self.deletion_date = None
        self.is_active = True
        
        try:
            # First try the normal way with update_fields
            self.save(update_fields=[
                'is_pending_deletion', 
                'deletion_scheduled_at', 
                'deletion_date', 
                'is_active'
            ])
        except Exception as e:
            # If that fails, fall back to a full save
            self.save()
        
        return True
        
    def delete_user_account(self, anonymize: bool = True, immediate: bool = False):
        """
        Securely delete the user account.
        If anonymize is True, anonymize personal data before deletion for GDPR compliance.
        If immediate is False, the account is scheduled for deletion after 30 days.
        """
        if not immediate:
            return self.schedule_account_deletion()
            
        if anonymize:
            self._anonymize_user_data()
        self._delete_related_objects()
        super().delete()
        
        return True

    def _anonymize_user_data(self):
        self.email = f"deleted_user_{self.public_id}@example.com"
        self.username = f"deleted_user_{self.public_id}"
        self.first_name = ""
        self.last_name = ""
        self.bio = ""
        profile_pic = getattr(self, 'profile_picture', None)
        if profile_pic:
            profile_pic.delete(save=False)
        self.is_active = False
        self.save()

    def _delete_related_objects(self):
        if hasattr(self, 'feedbacks'):
            self.feedbacks.all().delete()
        if hasattr(self, 'given_reviews'):
            self.given_reviews.all().delete()
        if hasattr(self, 'coach_profile'):
            self.coach_profile.delete()
    
    def days_until_deletion(self):
        """
        Calculate days remaining until permanent deletion.
        """
        if not self.is_pending_deletion or not self.deletion_date:
            return None
        
        from django.utils import timezone
        remaining = self.deletion_date - timezone.now()
        return max(0, remaining.days)
    def clean(self, *args, **kwargs):
        if self.native_language == self.target_language:
            raise ValidationError("Native language and target language cannot be the same.")

    def save(self, *args, **kwargs):
        """
        Override the save method to handle validation and update_fields correctly.
        """
        try:
            # If update_fields is specified, use that method to avoid full validation
            if 'update_fields' in kwargs:
                # Ensure all fields in update_fields exist on the model
                valid_fields = []
                for field in kwargs['update_fields']:
                    if hasattr(self, field):
                        valid_fields.append(field)
                
                if valid_fields:
                    kwargs['update_fields'] = valid_fields
                    super().save(*args, **kwargs)
                else:
                    # If no valid fields, fall back to a normal save
                    kwargs.pop('update_fields')
                    super().save(*args, **kwargs)
            else:
                # For new users, do full validation
                if not self.pk:
                    self.full_clean()
                super().save(*args, **kwargs)
        except Exception as e:
            # If save with update_fields fails, try without it
            if 'update_fields' in kwargs:
                kwargs.pop('update_fields')
                super().save(*args, **kwargs)
            else:
                # If it's still failing, re-raise the exception
                raise

    def __str__(self):
        return f"{self.email}"

    def accept_terms(self, version='v1.0'):
        """
        Mark terms and conditions as accepted by the user
        """
        from django.utils import timezone

        self.terms_accepted = True
        self.terms_accepted_at = timezone.now()
        self.terms_version = version
        self.save(update_fields=['terms_accepted', 'terms_accepted_at', 'terms_version'])
        return True

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def get_profile_picture_urls(self):
        """
        Obtient les URLs pour toutes les versions de la photo de profil.

        Returns:
            dict: Dictionnaire avec les URLs pour chaque taille (small, medium, large, optimized, original)
        """
        from .helpers import get_profile_picture_urls
        return get_profile_picture_urls(self)

# Extended Coach Profile Model: the additional fields for a coach profile are added here as a separate model.
# This model has a Many-to-many relationship with the User model.
# this means that a user can have multiple coach profiles and a coach profile can be associated with multiple users.
# the coach profile is prepared in view to develop the coaching app in the future.


class CoachProfile(models.Model):
    """
    Model representing a coach's profile.

    Attributes:
        user (User): One-to-one relationship with the User model.
        coaching_languages (str): Languages the coach can teach, chosen from predefined choices.
        price_per_hour (Decimal): Hourly rate for coaching sessions.
        availability (str): Text field describing the coach's availability.
        description (str): Detailed description of the coach's profile.
    """
    class Meta:
        app_label = 'authentication'
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coach_profile')
    coaching_languages = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default=LANGUAGE_CHOICES[0][0])
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    availability = models.TextField(null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('5.00'), help_text="Commission rate taken by Linguify (in %).")
    commission_override = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Override the default commission rate.")

    class Meta:
        app_label = 'authentication'
        unique_together = ('user', 'coaching_languages')
    # to update the availability of the coach
    def update_availability(self, new_availability):
        self.availability = new_availability
        self.save()

    # to update the price per hour of the coach
    def update_price_per_hour(self, new_price):
        self.price_per_hour = new_price
        self.save()

    def calculate_commission(self):
        commission_to_use = self.commission_override if self.commission_override is not None else self.commission_rate
        return (self.price_per_hour * commission_to_use) / Decimal('100.00')

    def __str__(self):
        """
        String representation of the CoachProfile model.

        Returns:
            str: A string representing the coach's profile.
        """
        return f"Coach Profile of {self.user.username}"

# Review Model lol
class Review(models.Model):
    """
    Model representing a review.

    Attributes:
        reviewer (User): Foreign key to the User model, representing the user who wrote the review.
        rating (Decimal): Rating given by the reviewer, with a maximum of 3 digits and 2 decimal places.
        comment (str): Optional text content of the review.
        review_date (datetime): Date and time when the review was created.
    """
    class Meta:
        app_label = 'authentication'
    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE, related_name='reviews', default=None)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    comment = models.TextField(max_length=500, null=True, blank=True)
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String representation of the Review model.

        Returns:
            str: A string representing the reviewer's username.
        """
        return f"Review by {self.reviewer.username}"

class UserFeedback(models.Model):
    """
    Model representing user feedback to get a little bit of feedback don't u think?.

    Attributes:
        user (User): Foreign key to the User model, representing the user who gave the feedback.
        feedback_type (str): Type of feedback, either 'like' or 'dislike'.
        feedback_content (str): Optional text content of the feedback.
        feedback_date (datetime): Date and time when the feedback was created.
    """
    class Meta:
        app_label = 'authentication'
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=10, choices=[('like', 'Like'), ('dislike', 'Dislike')], default='like')
    feedback_content = models.TextField(null=True, blank=True)
    feedback_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String representation of the UserFeedback model.

        Returns:
            str: A string representing the user's username and the feedback type.
        """
        return f"{self.user.username} - {self.feedback_type}"


# Cookie Consent Management Models

class CookieConsentManager(models.Manager):
    """Manager for CookieConsent model"""
    
    def get_latest_consent(self, user=None, session_id=None, ip_address=None):
        """Get the latest consent for a user, session, or IP"""
        queryset = self.get_queryset()
        
        if user:
            queryset = queryset.filter(user=user)
        elif session_id:
            queryset = queryset.filter(session_id=session_id)
        elif ip_address:
            queryset = queryset.filter(ip_address=ip_address)
        else:
            return None
            
        return queryset.order_by('-created_at').first()
    
    def has_valid_consent(self, user=None, session_id=None, ip_address=None, version="1.0"):
        """Check if there's a valid consent for the given parameters"""
        consent = self.get_latest_consent(user, session_id, ip_address)
        
        if not consent:
            return False
            
        # Check if consent is for current version
        return consent.version == version and not consent.is_expired()
    
    def get_analytics_data(self, days=30):
        """Get consent analytics for the last N days"""
        from django.utils import timezone
        from datetime import timedelta
        
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = self.filter(created_at__gte=start_date)
        
        return {
            'total_consents': queryset.count(),
            'accept_all': queryset.filter(
                essential=True,
                analytics=True,
                functionality=True,
                performance=True
            ).count(),
            'essential_only': queryset.filter(
                essential=True,
                analytics=False,
                functionality=False,
                performance=False
            ).count(),
            'custom': queryset.exclude(
                models.Q(
                    essential=True,
                    analytics=True,
                    functionality=True,
                    performance=True
                ) | models.Q(
                    essential=True,
                    analytics=False,
                    functionality=False,
                    performance=False
                )
            ).count(),
            'by_version': dict(
                queryset.values('version').annotate(
                    count=models.Count('id')
                ).values_list('version', 'count')
            )
        }


class CookieConsent(models.Model):
    """Model to store cookie consent information"""
    
    # Unique identifier for this consent record
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    
    # User identification (can be null for anonymous users)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='cookie_consents',
        help_text="User who gave consent (null for anonymous users)"
    )
    
    # Session and IP tracking for anonymous users
    session_id = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        help_text="Session ID for anonymous users"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address when consent was given"
    )
    
    # User Agent for fraud detection and analytics
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="User agent string when consent was given"
    )
    
    # Consent version (important for GDPR compliance)
    version = models.CharField(
        max_length=10,
        default="1.0",
        help_text="Version of the consent form"
    )
    
    # Cookie categories consent
    essential = models.BooleanField(
        default=True,
        help_text="Essential cookies (always true)"
    )
    
    analytics = models.BooleanField(
        default=False,
        help_text="Analytics cookies (Google Analytics, etc.)"
    )
    
    functionality = models.BooleanField(
        default=False,
        help_text="Functionality cookies (user preferences, etc.)"
    )
    
    performance = models.BooleanField(
        default=False,
        help_text="Performance cookies (caching, optimization, etc.)"
    )
    
    # Additional metadata
    language = models.CharField(
        max_length=10,
        default='fr',
        help_text="Language when consent was given"
    )
    
    # GDPR compliance fields
    consent_method = models.CharField(
        max_length=20,
        choices=[
            ('banner', 'Cookie Banner'),
            ('settings', 'Settings Page'),
            ('api', 'API Call'),
            ('import', 'Data Import'),
        ],
        default='banner',
        help_text="How the consent was obtained"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When consent was given"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When consent was last updated"
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When consent expires (null = never)"
    )
    
    # Revocation tracking
    is_revoked = models.BooleanField(
        default=False,
        help_text="Whether consent has been revoked"
    )
    
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When consent was revoked"
    )
    
    revocation_reason = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=[
            ('user_request', 'User Request'),
            ('expired', 'Expired'),
            ('version_change', 'Version Change'),
            ('admin_action', 'Admin Action'),
            ('data_deletion', 'Account Deletion'),
        ],
        help_text="Reason for revocation"
    )
    
    # Custom manager
    objects = CookieConsentManager()
    
    class Meta:
        app_label = 'authentication'
        verbose_name = "Cookie Consent"
        verbose_name_plural = "Cookie Consents"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['session_id', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
            models.Index(fields=['version']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_revoked']),
        ]
        
        # Unique constraint to prevent duplicate active consents
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_revoked=False, user__isnull=False),
                name='unique_active_user_consent'
            ),
        ]
    
    def __str__(self):
        if self.user:
            identifier = f"User {self.user.id}"
        elif self.session_id:
            identifier = f"Session {self.session_id[:8]}..."
        else:
            identifier = f"IP {self.ip_address}"
            
        status = "Revoked" if self.is_revoked else "Active"
        return f"{identifier} - {status} (v{self.version})"
    
    def save(self, *args, **kwargs):
        """Custom save method"""
        # Essential cookies are always required
        self.essential = True
        
        # If this is a new consent for an existing user, revoke old ones
        if self.user and not self.pk:
            CookieConsent.objects.filter(
                user=self.user,
                is_revoked=False
            ).update(
                is_revoked=True,
                revoked_at=timezone.now(),
                revocation_reason='version_change'
            )
        
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if consent has expired"""
        if not self.expires_at:
            return False
        
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def revoke(self, reason='user_request'):
        """Revoke this consent"""
        from django.utils import timezone
        
        self.is_revoked = True
        self.revoked_at = timezone.now()
        self.revocation_reason = reason
        self.save()
    
    def get_consent_summary(self):
        """Get a summary of consent choices"""
        categories = []
        if self.essential:
            categories.append('essential')
        if self.analytics:
            categories.append('analytics')
        if self.functionality:
            categories.append('functionality')
        if self.performance:
            categories.append('performance')
        
        return {
            'categories': categories,
            'total_accepted': len(categories),
            'consent_level': self._get_consent_level()
        }
    
    def _get_consent_level(self):
        """Determine the level of consent given"""
        if self.analytics and self.functionality and self.performance:
            return 'full'
        elif not self.analytics and not self.functionality and not self.performance:
            return 'minimal'
        else:
            return 'partial'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': str(self.id),
            'user_id': self.user.id if self.user else None,
            'version': self.version,
            'essential': self.essential,
            'analytics': self.analytics,
            'functionality': self.functionality,
            'performance': self.performance,
            'language': self.language,
            'consent_method': self.consent_method,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_revoked': self.is_revoked,
            'revoked_at': self.revoked_at.isoformat() if self.revoked_at else None,
            'summary': self.get_consent_summary()
        }


class CookieConsentLog(models.Model):
    """Audit log for cookie consent changes"""
    
    consent = models.ForeignKey(
        CookieConsent,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    
    action = models.CharField(
        max_length=20,
        choices=[
            ('created', 'Created'),
            ('updated', 'Updated'),
            ('revoked', 'Revoked'),
            ('expired', 'Expired'),
        ]
    )
    
    old_values = models.JSONField(
        null=True,
        blank=True,
        help_text="Previous values before change"
    )
    
    new_values = models.JSONField(
        null=True,
        blank=True,
        help_text="New values after change"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    
    user_agent = models.TextField(
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'authentication'
        verbose_name = "Cookie Consent Log"
        verbose_name_plural = "Cookie Consent Logs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['consent', '-created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.consent} - {self.action} at {self.created_at}"