"""
Calendar provider models for external calendar synchronization
Support for Google Calendar, Outlook, Apple Calendar, etc.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
import uuid
import json
from cryptography.fernet import Fernet
import base64

User = get_user_model()


class CalendarProvider(models.Model):
    """
    External calendar provider configuration
    Stores credentials and sync settings for external calendars
    """
    
    # Provider types
    PROVIDER_TYPES = [
        ('google', 'Google Calendar'),
        ('outlook', 'Microsoft Outlook'),
        ('office365', 'Office 365'),
        ('apple', 'Apple iCloud'),
        ('caldav', 'CalDAV'),
        ('exchange', 'Microsoft Exchange'),
        ('zimbra', 'Zimbra'),
        ('yahoo', 'Yahoo Calendar'),
    ]
    
    # Sync directions
    SYNC_DIRECTIONS = [
        ('import_only', 'Import Only (External → Linguify)'),
        ('export_only', 'Export Only (Linguify → External)'),
        ('bidirectional', 'Bidirectional Sync'),
    ]
    
    # Sync frequencies
    SYNC_FREQUENCIES = [
        ('manual', 'Manual'),
        ('15min', 'Every 15 minutes'),
        ('30min', 'Every 30 minutes'),
        ('1hour', 'Every hour'),
        ('6hours', 'Every 6 hours'),
        ('daily', 'Daily'),
    ]
    
    # Basic identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Provider configuration
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calendar_providers',
        help_text="User who owns this provider configuration"
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Display name for this provider (e.g., 'Work Calendar')"
    )
    
    provider_type = models.CharField(
        max_length=20,
        choices=PROVIDER_TYPES,
        help_text="Type of calendar provider"
    )
    
    # Authentication and connection
    client_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="OAuth client ID or application ID"
    )
    
    encrypted_credentials = models.TextField(
        blank=True,
        help_text="Encrypted OAuth tokens, passwords, etc."
    )
    
    server_url = models.URLField(
        blank=True,
        help_text="Server URL for CalDAV, Exchange, etc."
    )
    
    username = models.CharField(
        max_length=255,
        blank=True,
        help_text="Username for basic auth providers"
    )
    
    # External calendar identification
    external_calendar_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="External calendar ID (e.g., Google Calendar ID)"
    )
    
    external_calendar_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of the external calendar"
    )
    
    # Sync configuration
    sync_direction = models.CharField(
        max_length=20,
        choices=SYNC_DIRECTIONS,
        default='bidirectional',
        help_text="Direction of synchronization"
    )
    
    sync_frequency = models.CharField(
        max_length=10,
        choices=SYNC_FREQUENCIES,
        default='1hour',
        help_text="How often to synchronize"
    )
    
    auto_sync_enabled = models.BooleanField(
        default=True,
        help_text="Enable automatic synchronization"
    )
    
    # Sync filters
    sync_past_days = models.IntegerField(
        default=30,
        help_text="Number of past days to sync"
    )
    
    sync_future_days = models.IntegerField(
        default=365,
        help_text="Number of future days to sync"
    )
    
    sync_only_busy = models.BooleanField(
        default=False,
        help_text="Only sync events marked as 'busy'"
    )
    
    exclude_all_day_events = models.BooleanField(
        default=False,
        help_text="Exclude all-day events from sync"
    )
    
    # Status and monitoring
    active = models.BooleanField(
        default=True,
        help_text="Is this provider active?"
    )
    
    last_sync_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last successful synchronization time"
    )
    
    last_sync_status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('error', 'Error'),
            ('warning', 'Warning'),
            ('never', 'Never Synced'),
        ],
        default='never',
        help_text="Status of last sync attempt"
    )
    
    last_sync_error = models.TextField(
        blank=True,
        help_text="Error message from last sync attempt"
    )
    
    sync_count = models.IntegerField(
        default=0,
        help_text="Total number of successful syncs"
    )
    
    # Connection validation
    connection_verified = models.BooleanField(
        default=False,
        help_text="Has the connection been verified?"
    )
    
    verification_error = models.TextField(
        blank=True,
        help_text="Error message from connection verification"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Provider-specific configuration (JSON)
    provider_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider-specific configuration options"
    )
    
    class Meta:
        db_table = 'calendar_provider'
        verbose_name = 'Calendar Provider'
        verbose_name_plural = 'Calendar Providers'
        unique_together = [
            ('user', 'name'),  # User can't have duplicate provider names
        ]
        indexes = [
            models.Index(fields=['user', 'active']),
            models.Index(fields=['provider_type', 'active']),
            models.Index(fields=['auto_sync_enabled', 'sync_frequency']),
            models.Index(fields=['last_sync_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()}) - {self.user.username}"
    
    def clean(self):
        """Validate provider configuration"""
        if self.provider_type in ['google', 'outlook', 'office365'] and not self.client_id:
            raise ValidationError(f"{self.get_provider_type_display()} requires a client ID")
        
        if self.provider_type in ['caldav', 'exchange'] and not self.server_url:
            raise ValidationError(f"{self.get_provider_type_display()} requires a server URL")
        
        if self.sync_past_days < 0:
            raise ValidationError("Past days must be non-negative")
        
        if self.sync_future_days < 1:
            raise ValidationError("Future days must be at least 1")
    
    def save(self, *args, **kwargs):
        """Save with validation"""
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def credentials(self):
        """Decrypt and return credentials"""
        if not self.encrypted_credentials:
            return {}
        
        try:
            fernet = self._get_fernet()
            decrypted = fernet.decrypt(self.encrypted_credentials.encode())
            return json.loads(decrypted.decode())
        except Exception:
            return {}
    
    @credentials.setter
    def credentials(self, value):
        """Encrypt and store credentials"""
        if not value:
            self.encrypted_credentials = ''
            return
        
        try:
            fernet = self._get_fernet()
            json_str = json.dumps(value)
            encrypted = fernet.encrypt(json_str.encode())
            self.encrypted_credentials = encrypted.decode()
        except Exception as e:
            raise ValidationError(f"Failed to encrypt credentials: {str(e)}")
    
    def _get_fernet(self):
        """Get Fernet encryption instance"""
        secret_key = getattr(settings, 'CALENDAR_ENCRYPTION_KEY', None)
        if not secret_key:
            # Generate a key for development (in production, this should be in settings)
            secret_key = Fernet.generate_key()
        
        if isinstance(secret_key, str):
            secret_key = secret_key.encode()
        
        return Fernet(secret_key)
    
    def test_connection(self):
        """Test connection to external calendar provider"""
        from ..services.provider_service import ProviderService
        
        try:
            service = ProviderService.get_service(self)
            result = service.test_connection()
            
            if result['success']:
                self.connection_verified = True
                self.verification_error = ''
            else:
                self.connection_verified = False
                self.verification_error = result.get('error', 'Unknown error')
            
            self.save(update_fields=['connection_verified', 'verification_error', 'updated_at'])
            return result
            
        except Exception as e:
            self.connection_verified = False
            self.verification_error = str(e)
            self.save(update_fields=['connection_verified', 'verification_error', 'updated_at'])
            return {'success': False, 'error': str(e)}
    
    def sync_now(self, force=False):
        """Trigger immediate synchronization"""
        from ..services.sync_service import SyncService
        
        if not self.active and not force:
            return {'success': False, 'error': 'Provider is not active'}
        
        if not self.connection_verified and not force:
            return {'success': False, 'error': 'Connection not verified'}
        
        try:
            sync_service = SyncService(self)
            result = sync_service.sync()
            
            # Update sync status
            self.last_sync_at = timezone.now()
            if result['success']:
                self.last_sync_status = 'success'
                self.last_sync_error = ''
                self.sync_count += 1
            else:
                self.last_sync_status = 'error'
                self.last_sync_error = result.get('error', 'Unknown error')
            
            self.save(update_fields=[
                'last_sync_at', 'last_sync_status', 'last_sync_error', 
                'sync_count', 'updated_at'
            ])
            
            return result
            
        except Exception as e:
            self.last_sync_at = timezone.now()
            self.last_sync_status = 'error'
            self.last_sync_error = str(e)
            self.save(update_fields=['last_sync_at', 'last_sync_status', 'last_sync_error', 'updated_at'])
            return {'success': False, 'error': str(e)}
    
    def get_sync_frequency_minutes(self):
        """Get sync frequency in minutes"""
        frequency_map = {
            'manual': 0,
            '15min': 15,
            '30min': 30,
            '1hour': 60,
            '6hours': 360,
            'daily': 1440,
        }
        return frequency_map.get(self.sync_frequency, 60)
    
    def needs_sync(self):
        """Check if provider needs synchronization"""
        if not self.auto_sync_enabled or not self.active:
            return False
        
        if self.sync_frequency == 'manual':
            return False
        
        if not self.last_sync_at:
            return True
        
        frequency_minutes = self.get_sync_frequency_minutes()
        if frequency_minutes == 0:
            return False
        
        from datetime import timedelta
        next_sync = self.last_sync_at + timedelta(minutes=frequency_minutes)
        return timezone.now() >= next_sync
    
    def get_status_display(self):
        """Get human-readable status"""
        if not self.active:
            return "Inactive"
        
        if not self.connection_verified:
            return "Connection Error"
        
        if self.last_sync_status == 'never':
            return "Never Synced"
        
        if self.last_sync_status == 'success':
            if self.last_sync_at:
                time_ago = timezone.now() - self.last_sync_at
                if time_ago.days > 0:
                    return f"Synced {time_ago.days} days ago"
                elif time_ago.seconds > 3600:
                    hours = time_ago.seconds // 3600
                    return f"Synced {hours} hours ago"
                else:
                    minutes = time_ago.seconds // 60
                    return f"Synced {minutes} minutes ago"
            return "Recently Synced"
        
        return "Sync Error"
    
    def disable(self, reason=""):
        """Disable the provider"""
        self.active = False
        if reason:
            self.verification_error = reason
        self.save(update_fields=['active', 'verification_error', 'updated_at'])
    
    def enable(self):
        """Enable the provider"""
        self.active = True
        self.save(update_fields=['active', 'updated_at'])
    
    @classmethod
    def get_supported_providers(cls):
        """Get list of supported provider types with metadata"""
        return [
            {
                'type': provider_type,
                'name': provider_name,
                'auth_type': 'oauth' if provider_type in ['google', 'outlook', 'office365'] else 'basic',
                'supports_multiple_calendars': provider_type in ['google', 'outlook', 'office365', 'caldav'],
            }
            for provider_type, provider_name in cls.PROVIDER_TYPES
        ]
    
    @classmethod
    def create_google_provider(cls, user, name, credentials):
        """Create Google Calendar provider"""
        provider = cls.objects.create(
            user=user,
            name=name,
            provider_type='google',
            client_id=credentials.get('client_id', ''),
        )
        provider.credentials = credentials
        provider.save()
        return provider
    
    @classmethod
    def create_outlook_provider(cls, user, name, credentials):
        """Create Outlook provider"""
        provider = cls.objects.create(
            user=user,
            name=name,
            provider_type='outlook',
            client_id=credentials.get('client_id', ''),
        )
        provider.credentials = credentials
        provider.save()
        return provider
    
    @classmethod
    def create_caldav_provider(cls, user, name, server_url, username, password):
        """Create CalDAV provider"""
        provider = cls.objects.create(
            user=user,
            name=name,
            provider_type='caldav',
            server_url=server_url,
            username=username,
        )
        provider.credentials = {'password': password}
        provider.save()
        return provider


class CalendarProviderSync(models.Model):
    """
    Track synchronization history and statistics
    """
    
    # Sync types
    SYNC_TYPES = [
        ('auto', 'Automatic'),
        ('manual', 'Manual'),
        ('initial', 'Initial Setup'),
    ]
    
    # Basic identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Provider and sync info
    provider = models.ForeignKey(
        CalendarProvider,
        on_delete=models.CASCADE,
        related_name='sync_history'
    )
    
    sync_type = models.CharField(
        max_length=10,
        choices=SYNC_TYPES,
        default='auto'
    )
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    # Results
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    # Statistics
    events_imported = models.IntegerField(default=0)
    events_exported = models.IntegerField(default=0)
    events_updated = models.IntegerField(default=0)
    events_deleted = models.IntegerField(default=0)
    events_skipped = models.IntegerField(default=0)
    
    # Sync details (JSON)
    sync_details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'calendar_provider_sync'
        verbose_name = 'Calendar Provider Sync'
        verbose_name_plural = 'Calendar Provider Syncs'
        indexes = [
            models.Index(fields=['provider', 'started_at']),
            models.Index(fields=['success', 'started_at']),
        ]
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.provider.name} - {self.get_sync_type_display()} - {status}"
    
    def mark_completed(self, success=True, error_message=""):
        """Mark sync as completed"""
        self.completed_at = timezone.now()
        self.success = success
        self.error_message = error_message
        
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = delta.total_seconds()
        
        self.save(update_fields=['completed_at', 'success', 'error_message', 'duration_seconds'])
    
    def get_summary(self):
        """Get sync summary"""
        total_events = (
            self.events_imported + self.events_exported + 
            self.events_updated + self.events_deleted
        )
        
        return {
            'total_events': total_events,
            'imported': self.events_imported,
            'exported': self.events_exported,
            'updated': self.events_updated,
            'deleted': self.events_deleted,
            'skipped': self.events_skipped,
            'duration': self.duration_seconds,
            'success': self.success,
        }