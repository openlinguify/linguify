# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# backend/authentication/models.py
import os
import datetime
from uuid import uuid4
from typing import Any, Optional
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import models as auth_models
from django.core.validators import MinValueValidator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import re
from django.db.models import QuerySet, Q
from django.db.models.functions import Lower
from django.http import Http404
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from PIL import Image
import secrets
import string
from timezone_field import TimeZoneField

from ..utils.storage import ProfileStorage

class DuplicateEmailError(Exception):
    """Raised when an email is already associated with a pre-existing user."""
    def __init__(self, message=None, email=None):
        self.message = message
        self.email = email
        super().__init__(self.message)

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('N', 'Non-binary'),
    ('O', 'Other'),
    ('P', 'Prefer not to say'),
]

HOW_DID_YOU_HEAR = [
    ('search_engine', 'Search Engine (Google, Bing, etc.)'),
    ('social_media', 'Social Media'),
    ('friend_referral', 'Friend or Family'),
    ('online_ad', 'Online Advertisement'),
    ('blog_article', 'Blog or Article'),
    ('app_store', 'App Store'),
    ('school_university', 'School or University'),
    ('work_colleague', 'Work or Colleague'),
    ('other', 'Other'),
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


# Import centralized validator
from ..utils.validators import validate_username_format as validate_username


class UserManager(BaseUserManager):
    def get_user_by_sub_or_email(self, sub, email=None):
        """Fetch existing user by sub or email."""
        try:
            return self.get(sub=sub)
        except self.model.DoesNotExist as err:
            if not email:
                return None

            if settings.OIDC_FALLBACK_TO_EMAIL_FOR_IDENTIFICATION:
                try:
                    return self.get(email=email)
                except self.model.DoesNotExist:
                    pass
            elif (
                self.filter(email=email).exists()
                and not settings.OIDC_ALLOW_DUPLICATE_EMAILS
            ):
                raise DuplicateEmailError(
                    message=_(
                        "We couldn't find a user with this sub but the email is already "
                        "associated with a registered user."
                    ),
                    email=email  # Ajout du paramètre email ici
                ) from err
        return None

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

        # Vérifier l'unicité case-insensitive du username
        if self.filter(username__iexact=username).exists():
            raise ValidationError(_('This username is already taken'))

        # Vérifier l'unicité de l'email avec DuplicateEmailError
        normalized_email = self.normalize_email(email)
        if self.filter(email__iexact=normalized_email).exists():
            raise DuplicateEmailError(
                message=_('This email address is already registered. Please use a different email or reset your password.'),
                email=normalized_email
            )

        user = self.model(
            username=username,
            email=normalized_email,
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



# Base User Model
class User(AbstractBaseUser, PermissionsMixin):
    # Explicitly set app_label to solve the Django model registration issue
    class Meta:
        app_label = 'authentication'
        # Contrainte d'unicité case-insensitive pour les usernames
        constraints = [
            models.UniqueConstraint(
                Lower('username'),
                name='unique_username_case_insensitive',
                violation_error_message='This username is already taken.'
            )
        ]
    
    id = models.AutoField(primary_key=True)
    public_id = models.UUIDField(db_index=True, default=uuid4, editable=False, unique=True)
    username = models.CharField(db_index=True, max_length=255, unique=True, blank=False, null=False, validators=[validate_username])
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(
        db_index=True, 
        unique=True, 
        blank=False, 
        null=False,
        error_messages={'unique': _('This email address is already associated with an existing account.')}
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Phone number (e.g., +32 123 456 789)")
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    # in order to know if the user is active or not; if the user is not active, he/she can't log in to the platform
    # the user can be deactivated by the admin or by the user himself
    # the user progress will be saved even if the user is deactivated during a certain period of time (e.g. 6 months)
    # if the user is deactivated for more than 6 months, the user progress will be deleted
    is_active = models.BooleanField(null=False, default=False)
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
        upload_to='',  # Empty string since ProfileStorage already points to profiles/
        storage=ProfileStorage(),
        null=True,
        blank=True,
        validators=[validate_profile_picture]
    )
    bio = models.TextField(max_length=500, null=True, blank=True)

    is_coach = models.BooleanField(default=False)
    interface_language = models.CharField(max_length=20, choices=settings.LANGUAGES, default='en', verbose_name=_("language"), help_text=_("The language in which the user wants to see the interface."), null=True, blank=True,)
    timezone = TimeZoneField(choices_display="WITH_GMT_OFFSET", use_pytz=False, default=settings.TIME_ZONE, help_text=_("The timezone in which the user wants to see times."))
    is_device = models.BooleanField(_("device"), default=False, help_text=_("Whether the user is a device or a real user."))
    theme = models.CharField(max_length=10, default='light')
    # settings fields
    email_notifications = models.BooleanField(default=True, verbose_name=_("Receive the notification by emails"))
    push_notifications = models.BooleanField(default=True, verbose_name=_("Receive the push notification"))
    marketing_emails = models.BooleanField(default=True, verbose_name=_("Receive the marketing emails"))

    # Private settings fields
    public_profile = models.BooleanField(default=True)
    share_progress = models.BooleanField(default=True)
    share_activity = models.BooleanField(default=False)

    # Terms and conditions acceptance fields
    terms_accepted = models.BooleanField(default=False, help_text='Whether the user has accepted the terms and conditions')
    terms_accepted_at = models.DateTimeField(null=True, blank=True, help_text='When the user accepted the terms and conditions')
    terms_version = models.CharField(max_length=10, null=True, blank=True, default='v1.0', help_text='Version of terms that was accepted')

    # User acquisition source field - required for new users
    how_did_you_hear = models.CharField(
        max_length=50,
        null=True,  # Keep null=True for existing users in database
        blank=True,  # Keep blank=True for admin interface flexibility
        default='other',  # Default value for existing users
        choices=HOW_DID_YOU_HEAR,
        help_text='How the user heard about the platform'
    )

    # Custom manager
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def update_profile(self, **kwargs):
        """
        Met à jour le profil utilisateur.
        Note: Les champs d'apprentissage des langues ont été déplacés vers
        l'app language_learning et doivent être gérés séparément.
        """
        # Champs autorisés pour le profil utilisateur
        allowed_fields = {
            "first_name", "last_name", "phone_number", "bio", "profile_picture",
            "interface_language", "theme", "email_notifications", "push_notifications",
            "public_profile", "share_progress", "share_activity",
            "terms_accepted", "terms_accepted_at", "terms_version", "how_did_you_hear"
        }

        # Mettre à jour seulement les champs autorisés
        for k, v in kwargs.items():
            if k in allowed_fields:
                setattr(self, k, v)

        self.save()

    # Thoses methodes concern username:
    



    @property
    def get_profile_picture_url(self):
        """
        Retourne l'URL de la photo de profil
        """
        if self.profile_picture:
            # Si c'est une URL complète (Supabase), la retourner directement
            profile_str = str(self.profile_picture)
            if profile_str.startswith(('http://', 'https://')):
                return profile_str
            
            # Sinon, générer l'URL locale Django
            try:
                return self.profile_picture.url
            except Exception:
                pass
        
        return None
    
    def get_preferref_language(self):
        return self.native_language or self.interface_language or 'en'
    
    def get_profile_picture_absolute_url(self, request):
        """
        Retourne l'URL absolue de la photo de profil pour les API
        """
        if self.profile_picture:
            profile_str = str(self.profile_picture)
            
            # Si c'est déjà une URL complète (Supabase), la retourner directement
            if profile_str.startswith(('http://', 'https://')):
                return profile_str
            
            # Sinon, construire l'URL absolue locale
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
        # Validation case-insensitive du username
        if self.username:
            # Exclure l'instance actuelle lors de la mise à jour
            existing_users = User.objects.filter(username__iexact=self.username)
            if self.pk:
                existing_users = existing_users.exclude(pk=self.pk)

            if existing_users.exists():
                raise ValidationError(_('This username is already taken'))

    def save(self, *args, **kwargs):
        """
        Override the save method with proper validation and error handling.
        Ensures data integrity by avoiding dangerous fallback logic.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Validate update_fields if provided
        if 'update_fields' in kwargs:
            update_fields = kwargs['update_fields']
            if not isinstance(update_fields, (list, tuple, set)):
                raise ValueError("update_fields must be a list, tuple, or set")
            
            # Filter valid fields and warn about invalid ones
            valid_fields = []
            invalid_fields = []
            
            for field in update_fields:
                if hasattr(self, field):
                    valid_fields.append(field)
                else:
                    invalid_fields.append(field)
            
            # Log warning for invalid fields
            if invalid_fields:
                logger.warning(
                    f"Invalid fields in update_fields ignored: {invalid_fields} "
                    f"for User {getattr(self, 'username', 'unknown')}"
                )
            
            # If no valid fields, convert to full save
            if not valid_fields:
                kwargs.pop('update_fields')
                logger.info(f"Converted to full save for User {getattr(self, 'username', 'unknown')} - no valid update_fields")
            else:
                kwargs['update_fields'] = valid_fields
        
        # Always validate new users
        if not self.pk:
            try:
                self.full_clean()
            except Exception as e:
                raise ValueError(f"Validation failed for new user: {e}")
        
        # For updates with specific fields, validate only those fields
        elif 'update_fields' in kwargs:
            try:
                # Validate only the fields being updated
                exclude_fields = [
                    f.name for f in self._meta.fields 
                    if f.name not in kwargs['update_fields']
                ]
                self.clean_fields(exclude=exclude_fields)
                self.clean()
            except Exception as e:
                raise ValueError(f"Validation failed for fields {kwargs['update_fields']}: {e}")
        
        # Perform the save operation - no dangerous fallbacks
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            # Log the error but don't attempt dangerous fallbacks
            logger.error(f"Save failed for User {getattr(self, 'username', 'unknown')}: {e}")
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

    # DEPRECATED: Backward compatibility properties - will be removed in future version
    # Use user.learning_profile.target_language instead
    @property
    def target_language(self):
        """DEPRECATED: Use user.learning_profile.target_language instead"""
        import warnings
        warnings.warn(
            "user.target_language is deprecated. Use user.learning_profile.target_language instead.",
            DeprecationWarning,
            stacklevel=2
        )
        try:
            return self.learning_profile.target_language
        except AttributeError:
            return None

    @property
    def native_language(self):
        """DEPRECATED: Use user.learning_profile.native_language instead"""
        import warnings
        warnings.warn(
            "user.native_language is deprecated. Use user.learning_profile.native_language instead.",
            DeprecationWarning,
            stacklevel=2
        )
        try:
            return self.learning_profile.native_language
        except AttributeError:
            return None

    @property
    def language_level(self):
        """DEPRECATED: Use user.learning_profile.language_level instead"""
        import warnings
        warnings.warn(
            "user.language_level is deprecated. Use user.learning_profile.language_level instead.",
            DeprecationWarning,
            stacklevel=2
        )
        try:
            return self.learning_profile.language_level
        except AttributeError:
            return None

    def get_target_language_display(self):
        """DEPRECATED: Use user.learning_profile.get_target_language_display() instead"""
        import warnings
        warnings.warn(
            "user.get_target_language_display() is deprecated. Use user.learning_profile.get_target_language_display() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        try:
            return self.learning_profile.get_target_language_display()
        except AttributeError:
            return None

    def get_native_language_display(self):
        """DEPRECATED: Use user.learning_profile.get_native_language_display() instead"""
        import warnings
        warnings.warn(
            "user.get_native_language_display() is deprecated. Use user.learning_profile.get_native_language_display() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        try:
            return self.learning_profile.get_native_language_display()
        except AttributeError:
            return None

    def get_full_name(self):
        """Return the user's full name"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

    
    @property
    def age(self):
        """Calculate age from birthday"""
        if not self.birthday:
            return None
        
        from datetime import date
        today = date.today()
        age = today.year - self.birthday.year
        
        # Check if birthday hasn't occurred yet this year
        if (today.month, today.day) < (self.birthday.month, self.birthday.day):
            age -= 1
            
        return age

    def get_profile_picture_urls(self):
        """
        Obtient les URLs pour toutes les versions de la photo de profil.

        Returns:
            dict: Dictionnaire avec les URLs pour chaque taille (small, medium, large, optimized, original)
        """
        from ..utils.helpers import get_profile_picture_urls
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
    # Note: Les langues de coaching sont maintenant un simple CharField
    # Les choix de langues sont gérés dans language_learning.models
    coaching_languages = models.CharField(max_length=20, help_text="Language codes (e.g., EN, FR, ES)")
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

# Review Model
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

FEEDBACK_TYPE_CHOICES = [
    ('bug_report', 'Bug Report'),
    ('feature_request', 'Feature Request'),
    ('improvement', 'Improvement Suggestion'),
    ('compliment', 'Compliment'),
    ('complaint', 'Complaint'),
    ('question', 'Question/Help'),
    ('other', 'Other'),
]

FEEDBACK_PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]

FEEDBACK_STATUS_CHOICES = [
    ('new', 'New'),
    ('in_progress', 'In Progress'),
    ('resolved', 'Resolved'),
    ('closed', 'Closed'),
    ('duplicate', 'Duplicate'),
    ('wont_fix', "Won't Fix"),
]

FEEDBACK_CATEGORY_CHOICES = [
    ('ui_ux', 'UI/UX'),
    ('performance', 'Performance'),
    ('functionality', 'Functionality'),
    ('content', 'Content'),
    ('mobile', 'Mobile App'),
    ('desktop', 'Desktop'),
    ('account', 'Account Management'),
    ('payment', 'Payment/Billing'),
    ('language_learning', 'Language Learning'),
    ('other', 'Other'),
]

class UserFeedback(models.Model):
    """
    Enhanced model representing comprehensive user feedback and bug tracking.

    Attributes:
        user (User): Foreign key to the User model, representing the user who gave the feedback.
        title (str): Short title/summary of the feedback.
        feedback_type (str): Type of feedback (bug report, feature request, etc.).
        category (str): Category of the feedback for better organization.
        priority (str): Priority level of the feedback.
        status (str): Current status of the feedback.
        description (str): Detailed description of the feedback.
        steps_to_reproduce (str): For bug reports, steps to reproduce the issue.
        expected_behavior (str): What the user expected to happen.
        actual_behavior (str): What actually happened.
        browser_info (str): Browser and system information.
        page_url (str): URL where the issue occurred.
        screenshot (ImageField): Optional screenshot of the issue.
        admin_notes (str): Internal notes for admins.
        assigned_to (User): Staff member assigned to handle this feedback.
        resolved_at (datetime): When the feedback was resolved.
        created_at (datetime): Date and time when the feedback was created.
        updated_at (datetime): Date and time when the feedback was last updated.
    """
    class Meta:
        app_label = 'authentication'
        verbose_name = "User Feedback"
        verbose_name_plural = "User Feedbacks"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['feedback_type', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['priority', '-created_at']),
            models.Index(fields=['category']),
            models.Index(fields=['user', '-created_at']),
        ]

    # Basic information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    title = models.CharField(max_length=200, help_text="Brief summary of the feedback")
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPE_CHOICES,
        default='other',
        help_text="Type of feedback"
    )
    category = models.CharField(
        max_length=20,
        choices=FEEDBACK_CATEGORY_CHOICES,
        default='other',
        help_text="Category for better organization"
    )

    # Priority and status tracking
    priority = models.CharField(
        max_length=10,
        choices=FEEDBACK_PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level"
    )
    status = models.CharField(
        max_length=15,
        choices=FEEDBACK_STATUS_CHOICES,
        default='new',
        help_text="Current status"
    )

    # Detailed feedback content
    description = models.TextField(help_text="Detailed description of the feedback")
    steps_to_reproduce = models.TextField(
        null=True,
        blank=True,
        help_text="For bug reports: steps to reproduce the issue"
    )
    expected_behavior = models.TextField(
        null=True,
        blank=True,
        help_text="What should have happened"
    )
    actual_behavior = models.TextField(
        null=True,
        blank=True,
        help_text="What actually happened"
    )

    # Technical information
    browser_info = models.TextField(
        null=True,
        blank=True,
        help_text="Browser, OS, and device information"
    )
    page_url = models.URLField(
        null=True,
        blank=True,
        max_length=500,
        help_text="URL where the issue occurred"
    )
    screenshot = models.ImageField(
        upload_to='feedback_screenshots/%Y/%m/',
        null=True,
        blank=True,
        help_text="Optional screenshot of the issue"
    )

    # Admin and tracking fields
    admin_notes = models.TextField(
        null=True,
        blank=True,
        help_text="Internal notes for admins (not visible to users)"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_feedbacks',
        limit_choices_to={'is_staff': True},
        help_text="Staff member assigned to handle this feedback"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the feedback was resolved"
    )

    # Legacy field for backward compatibility
    feedback_content = models.TextField(
        null=True,
        blank=True,
        help_text="Legacy field - use 'description' instead"
    )
    feedback_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Legacy field - use 'created_at' instead"
    )

    def save(self, *args, **kwargs):
        # Auto-resolve timestamp when status changes to resolved
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status != 'resolved' and self.resolved_at:
            self.resolved_at = None

        # Migrate legacy data if needed
        if self.feedback_content and not self.description:
            self.description = self.feedback_content
        if self.feedback_date and not self.created_at:
            self.created_at = self.feedback_date

        super().save(*args, **kwargs)

    def get_status_display_with_color(self):
        """Return status with appropriate color coding"""
        colors = {
            'new': '#007bff',
            'in_progress': '#ffc107',
            'resolved': '#28a745',
            'closed': '#6c757d',
            'duplicate': '#fd7e14',
            'wont_fix': '#dc3545',
        }
        return {
            'status': self.get_status_display(),
            'color': colors.get(self.status, '#6c757d')
        }

    def get_priority_display_with_color(self):
        """Return priority with appropriate color coding"""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'critical': '#dc3545',
        }
        return {
            'priority': self.get_priority_display(),
            'color': colors.get(self.priority, '#6c757d')
        }

    def is_bug_report(self):
        """Check if this feedback is a bug report"""
        return self.feedback_type == 'bug_report'

    def is_feature_request(self):
        """Check if this feedback is a feature request"""
        return self.feedback_type == 'feature_request'

    def days_since_created(self):
        """Calculate days since feedback was created"""
        return (timezone.now() - self.created_at).days

    def days_since_updated(self):
        """Calculate days since feedback was last updated"""
        return (timezone.now() - self.updated_at).days

    def __str__(self):
        """
        String representation of the UserFeedback model.

        Returns:
            str: A string representing the feedback title and type.
        """
        return f"[{self.get_feedback_type_display()}] {self.title[:50]}..."


class FeedbackAttachment(models.Model):
    """
    Model for storing additional attachments to feedback (multiple files support)
    """
    class Meta:
        app_label = 'authentication'
        verbose_name = "Feedback Attachment"
        verbose_name_plural = "Feedback Attachments"
        ordering = ['-uploaded_at']

    feedback = models.ForeignKey(
        UserFeedback,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(
        upload_to='feedback_attachments/%Y/%m/',
        help_text="Additional file attachment (images, logs, etc.)"
    )
    filename = models.CharField(
        max_length=255,
        help_text="Original filename"
    )
    file_size = models.PositiveIntegerField(
        help_text="File size in bytes"
    )
    content_type = models.CharField(
        max_length=100,
        help_text="MIME type of the file"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file:
            self.filename = self.file.name
            self.file_size = self.file.size
            # Content type would be set by the form/view
        super().save(*args, **kwargs)

    def get_file_size_display(self):
        """Return human-readable file size"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"

    def __str__(self):
        return f"{self.filename} ({self.get_file_size_display()})"


class FeedbackResponse(models.Model):
    """
    Model for admin responses to user feedback
    """
    class Meta:
        app_label = 'authentication'
        verbose_name = "Feedback Response"
        verbose_name_plural = "Feedback Responses"
        ordering = ['-created_at']

    feedback = models.ForeignKey(
        UserFeedback,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'is_staff': True},
        help_text="Staff member who wrote the response"
    )
    message = models.TextField(
        help_text="Response message to the user"
    )
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal note (not visible to user)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        visibility = "Internal" if self.is_internal else "Public"
        return f"{visibility} response by {self.author.username} on {self.created_at.date()}"


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


class EmailVerificationToken(models.Model):
    """
    Model for storing email verification tokens
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='email_verification_tokens'
    )
    token = models.CharField(
        max_length=64, 
        unique=True,
        help_text="Unique verification token"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="Token expiration time"
    )
    is_used = models.BooleanField(
        default=False,
        help_text="Whether the token has been used"
    )
    
    class Meta:
        app_label = 'authentication'
        verbose_name = "Email Verification Token"
        verbose_name_plural = "Email Verification Tokens"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        if not self.expires_at:
            # Token expires in 24 hours
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))
    
    def is_expired(self):
        """Check if the token is expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if the token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()
    
    def use_token(self):
        """Mark the token as used"""
        self.is_used = True
        self.save()
    
    def __str__(self):
        status = "Used" if self.is_used else ("Expired" if self.is_expired() else "Active")
        return f"{self.user.email} - {status} - {self.created_at}"