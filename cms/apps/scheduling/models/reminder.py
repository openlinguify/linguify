# -*- coding: utf-8 -*-
"""
Appointment reminder models
Automated email/SMS reminders
"""
from django.db import models
from django.utils import timezone

from cms.core.models import TimestampedModel
from .appointment import Appointment


class AppointmentReminder(TimestampedModel):
    """Scheduled reminders for appointments."""

    REMINDER_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Programmé'),
        ('sent', 'Envoyé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ]

    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')

    # Reminder configuration
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES)
    minutes_before = models.PositiveIntegerField(help_text="Send X minutes before appointment")

    # Scheduling
    scheduled_for = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    error_message = models.TextField(blank=True)

    # Retry
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)

    class Meta:
        db_table = 'cms_appointment_reminders'
        ordering = ['scheduled_for']

    def __str__(self):
        return f"Reminder: {self.appointment.title} - {self.minutes_before}min before"

    def mark_sent(self):
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])

    def mark_failed(self, error=''):
        self.status = 'failed'
        self.error_message = error
        self.retry_count += 1
        self.save(update_fields=['status', 'error_message', 'retry_count'])

    def can_retry(self):
        return self.retry_count < self.max_retries
