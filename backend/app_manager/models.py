# app_manager/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class App(models.Model):
    """
    Represents an application available in the Linguify platform.
    The 4 main apps: learning, memory, notes, conversation_ai
    """
    APP_CHOICES = [
        ('learning', 'Learning'),
        ('memory', 'Memory'), 
        ('notes', 'Notes'),
        ('conversation_ai', 'Conversation AI'),
    ]
    
    # Technical identifier of the application
    code = models.CharField(
        max_length=50, 
        unique=True, 
        choices=APP_CHOICES,
        help_text="Technical code of the application"
    )
    
    # Display name for users
    display_name = models.CharField(
        max_length=100,
        help_text="Name displayed in the user interface"
    )
    
    # Application description
    description = models.TextField(
        help_text="Description of the application for users"
    )
    
    # Icon for interface
    icon_name = models.CharField(
        max_length=50,
        help_text="Icon name (Lucide React)"
    )
    
    # App theme color
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text="Hexadecimal color for the app (#RRGGBB)"
    )
    
    # Frontend routing URL
    route_path = models.CharField(
        max_length=100,
        help_text="Frontend routing path (e.g., /learning)"
    )
    
    # Globally enabled application
    is_enabled = models.BooleanField(
        default=True,
        help_text="Application available on the platform"
    )
    
    # Display order
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order in the interface"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'app_manager'
        ordering = ['order', 'display_name']
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
    
    def __str__(self):
        return self.display_name
    
    def clean(self):
        if self.color and not self.color.startswith('#'):
            raise ValidationError({'color': 'Color must start with #'})


class UserAppSettings(models.Model):
    """
    User application settings.
    Determines which applications are enabled for each user.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='app_settings'
    )
    
    # Applications enabled by the user
    enabled_apps = models.ManyToManyField(
        App,
        blank=True,
        related_name='enabled_users',
        help_text="Applications enabled by this user"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'app_manager'
        verbose_name = 'User App Settings'
        verbose_name_plural = 'User App Settings'
    
    def __str__(self):
        return f"{self.user.username}'s Apps"
    
    def get_enabled_app_codes(self):
        """Returns the list of enabled application codes"""
        return list(self.enabled_apps.values_list('code', flat=True))
    
    def is_app_enabled(self, app_code):
        """Checks if an application is enabled for this user"""
        return self.enabled_apps.filter(code=app_code, is_enabled=True).exists()
    
    def enable_app(self, app_code):
        """Enables an application for this user"""
        try:
            app = App.objects.get(code=app_code, is_enabled=True)
            self.enabled_apps.add(app)
            
            # If there's an existing data retention record for this app, remove it
            # since the user is re-enabling the app before the 30-day period
            try:
                AppDataRetention.objects.filter(
                    user=self.user,
                    app=app,
                    data_deleted=False
                ).delete()
            except Exception as e:
                # Log the error but don't fail the app enabling process
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to delete AppDataRetention records: {e}")
            
            return True
        except App.DoesNotExist:
            return False
    
    def disable_app(self, app_code):
        """Disables an application for this user"""
        try:
            app = App.objects.get(code=app_code)
            self.enabled_apps.remove(app)
            
            # Create a record for data retention when disabling an app
            try:
                AppDataRetention.objects.create(
                    user=self.user,
                    app=app,
                    disabled_at=timezone.now(),
                    data_expires_at=timezone.now() + timedelta(days=30)
                )
            except Exception as e:
                # Log the error but don't fail the app disabling process
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to create AppDataRetention record: {e}")
            
            return True
        except App.DoesNotExist:
            return False


class AppDataRetention(models.Model):
    """
    Tracks data retention for disabled applications.
    Ensures user data is preserved for 30 days after app is disabled.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='app_data_retentions',
        help_text="User who disabled the app"
    )
    
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
        related_name='data_retentions',
        help_text="Application that was disabled"
    )
    
    disabled_at = models.DateTimeField(
        help_text="When the app was disabled"
    )
    
    data_expires_at = models.DateTimeField(
        help_text="When the user data will be permanently deleted"
    )
    
    data_deleted = models.BooleanField(
        default=False,
        help_text="Whether the data has been permanently deleted"
    )
    
    data_deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the data was permanently deleted"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'app_manager'
        ordering = ['-disabled_at']
        verbose_name = 'App Data Retention'
        verbose_name_plural = 'App Data Retentions'
        # Prevent multiple retention records for the same user/app combination
        unique_together = ['user', 'app']
    
    def __str__(self):
        return f"{self.user.username} - {self.app.display_name} (expires: {self.data_expires_at.date()})"
    
    @property
    def days_until_deletion(self):
        """Returns the number of days until data deletion"""
        if self.data_deleted:
            return 0
        
        delta = self.data_expires_at - timezone.now()
        return max(0, delta.days)
    
    @property
    def is_expired(self):
        """Checks if the retention period has expired"""
        return timezone.now() >= self.data_expires_at
    
    def mark_data_deleted(self):
        """Marks the data as permanently deleted"""
        self.data_deleted = True
        self.data_deleted_at = timezone.now()
        self.save()
    
    @classmethod
    def get_expired_retentions(cls):
        """Returns all retention records that have expired"""
        return cls.objects.filter(
            data_expires_at__lte=timezone.now(),
            data_deleted=False
        )
    
    @classmethod
    def cleanup_expired_data(cls):
        """
        Cleanup method to be called by a scheduled task.
        Marks expired retention records as deleted.
        """
        expired_retentions = cls.get_expired_retentions()
        count = expired_retentions.count()
        
        for retention in expired_retentions:
            retention.mark_data_deleted()
        
        return count
