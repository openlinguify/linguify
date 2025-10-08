"""
Core models for CMS - Base abstract models for other apps to inherit from.
"""
from django.db import models
from django.utils import timezone


class MultilingualMixin(models.Model):
    """
    Mixin for models that need multilingual support.
    Provides language code field for content in different languages.
    """
    language = models.CharField(
        max_length=10,
        default='en',
        help_text='ISO language code (e.g., en, fr, es, nl)'
    )

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    """
    Abstract base model that provides timestamp fields.
    All models should inherit from this to track creation and modification times.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SyncableModel(TimestampedModel):
    """
    Abstract base model for models that need to be synchronized with backend.
    Provides sync tracking fields and timestamp tracking.
    """
    # Sync status tracking
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Sync'),
            ('synced', 'Synced'),
            ('failed', 'Sync Failed'),
            ('manual', 'Manual Entry'),
        ],
        default='pending',
        help_text='Current synchronization status with backend'
    )

    # Backend reference
    backend_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='ID of this object in the backend system'
    )

    # Sync timestamps
    last_sync_attempt = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Last time a sync was attempted'
    )
    last_sync_success = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Last time a sync succeeded'
    )

    # Sync error tracking
    sync_error = models.TextField(
        blank=True,
        null=True,
        help_text='Last sync error message if sync failed'
    )

    class Meta:
        abstract = True

    def mark_sync_pending(self):
        """Mark this object as needing sync."""
        self.sync_status = 'pending'
        self.save(update_fields=['sync_status', 'updated_at'])

    def mark_sync_success(self, backend_id=None):
        """Mark this object as successfully synced."""
        self.sync_status = 'synced'
        self.last_sync_success = timezone.now()
        self.last_sync_attempt = self.last_sync_success
        if backend_id:
            self.backend_id = backend_id
        self.sync_error = None
        self.save(update_fields=[
            'sync_status', 'last_sync_success', 'last_sync_attempt',
            'backend_id', 'sync_error', 'updated_at'
        ])

    def mark_sync_failed(self, error_message):
        """Mark this object's sync as failed."""
        self.sync_status = 'failed'
        self.last_sync_attempt = timezone.now()
        self.sync_error = error_message
        self.save(update_fields=[
            'sync_status', 'last_sync_attempt', 'sync_error', 'updated_at'
        ])
