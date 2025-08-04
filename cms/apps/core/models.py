"""
Core models for Teacher CMS.
Base models shared across the application.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TimestampedModel(models.Model):
    """Base model with timestamps."""
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class MultilingualMixin(models.Model):
    """Mixin for multilingual content support."""
    
    class Meta:
        abstract = True
    
    def get_localized_field(self, field_name, language='fr'):
        """Get localized field value with fallback."""
        localized_field = f"{field_name}_{language}"
        if hasattr(self, localized_field):
            value = getattr(self, localized_field)
            if value:
                return value
        
        # Fallback to English
        english_field = f"{field_name}_en"
        if hasattr(self, english_field):
            return getattr(self, english_field)
        
        # Fallback to base field
        if hasattr(self, field_name):
            return getattr(self, field_name)
        
        return ""

class SyncStatus(models.TextChoices):
    """Status for content synchronization."""
    DRAFT = 'draft', 'Draft'
    PENDING = 'pending', 'Pending Sync'
    SYNCED = 'synced', 'Synced'
    FAILED = 'failed', 'Sync Failed'

class SyncableModel(TimestampedModel):
    """Base model for content that can be synced to backend."""
    sync_status = models.CharField(
        max_length=20,
        choices=SyncStatus.choices,
        default=SyncStatus.DRAFT
    )
    backend_id = models.PositiveIntegerField(null=True, blank=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_error = models.TextField(blank=True)
    
    class Meta:
        abstract = True
    
    def mark_for_sync(self):
        """Mark content as needing sync."""
        self.sync_status = SyncStatus.PENDING
        self.save(update_fields=['sync_status'])
    
    def mark_synced(self, backend_id=None):
        """Mark content as successfully synced."""
        self.sync_status = SyncStatus.SYNCED
        self.last_sync = timezone.now()
        if backend_id:
            self.backend_id = backend_id
        self.sync_error = ""
        self.save(update_fields=['sync_status', 'last_sync', 'backend_id', 'sync_error'])
    
    def mark_sync_failed(self, error_message):
        """Mark sync as failed with error message."""
        self.sync_status = SyncStatus.FAILED
        self.sync_error = error_message
        self.save(update_fields=['sync_status', 'sync_error'])