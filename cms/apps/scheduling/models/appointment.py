# -*- coding: utf-8 -*-
"""
Appointment models
Book and manage appointments with teachers
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

from cms.core.models import TimestampedModel
from apps.teachers.models import Teacher
from .availability import TimeSlot


class AppointmentType(TimestampedModel):
    """Different types of appointments (trial, regular, group, etc.)."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    default_duration_minutes = models.PositiveIntegerField(default=60)
    color = models.CharField(max_length=7, default='#2196F3', help_text="Hex color for calendar")
    is_active = models.BooleanField(default=True)
    max_students = models.PositiveIntegerField(default=1, help_text="1 for one-on-one, >1 for group")

    class Meta:
        db_table = 'cms_appointment_types'

    def __str__(self):
        return self.name


class Appointment(TimestampedModel):
    """Booked appointments between teachers and students."""

    STATUS_CHOICES = [
        ('pending', '⏳ En attente'),
        ('confirmed', '✅ Confirmé'),
        ('in_progress', '▶️ En cours'),
        ('completed', '✔️ Terminé'),
        ('cancelled', '❌ Annulé'),
        ('no_show', '👻 Absent'),
    ]

    appointment_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Participants
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='appointments')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')

    # Type and timing
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.SET_NULL, null=True)
    time_slot = models.OneToOneField(TimeSlot, on_delete=models.SET_NULL, null=True, blank=True)

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Content
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=10, blank=True)
    level = models.CharField(max_length=20, blank=True)

    # Meeting details
    meeting_url = models.URLField(blank=True, help_text="Zoom, Google Meet, etc.")
    meeting_id = models.CharField(max_length=100, blank=True)
    meeting_password = models.CharField(max_length=50, blank=True)

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, blank=True)

    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_appointments')
    cancellation_reason = models.TextField(blank=True)

    # Completion
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'cms_appointments'
        ordering = ['-start_datetime']
        indexes = [
            models.Index(fields=['teacher', 'status', 'start_datetime']),
            models.Index(fields=['student', 'status', 'start_datetime']),
        ]

    def __str__(self):
        return f"{self.title} - {self.teacher.full_name} & {self.student.get_full_name()}"

    def confirm(self):
        self.status = 'confirmed'
        self.save(update_fields=['status'])

    def start(self):
        self.status = 'in_progress'
        self.save(update_fields=['status'])

    def complete(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

    def cancel(self, user, reason=''):
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.cancelled_by = user
        self.cancellation_reason = reason
        self.save(update_fields=['status', 'cancelled_at', 'cancelled_by', 'cancellation_reason'])

        # Free up the time slot
        if self.time_slot:
            self.time_slot.unbook()

    def is_upcoming(self):
        return self.start_datetime > timezone.now() and self.status in ['pending', 'confirmed']


class BookingRequest(TimestampedModel):
    """Pending booking requests that need teacher approval."""

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('declined', 'Refusé'),
        ('expired', 'Expiré'),
    ]

    request_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='booking_requests')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booking_requests')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.SET_NULL, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, help_text="Student's message to teacher")

    # Response
    responded_at = models.DateTimeField(null=True, blank=True)
    response_message = models.TextField(blank=True)

    # Expiry
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'cms_booking_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Request: {self.student.get_full_name()} → {self.teacher.full_name}"

    def approve(self, response_message=''):
        self.status = 'approved'
        self.responded_at = timezone.now()
        self.response_message = response_message
        self.save()

        # Create appointment
        Appointment.objects.create(
            teacher=self.teacher,
            student=self.student,
            appointment_type=self.appointment_type,
            time_slot=self.time_slot,
            start_datetime=self.time_slot.start_datetime,
            end_datetime=self.time_slot.end_datetime,
            duration_minutes=self.time_slot.duration_minutes,
            status='confirmed',
            title=f"{self.appointment_type.name} with {self.teacher.full_name}"
        )

    def decline(self, response_message=''):
        self.status = 'declined'
        self.responded_at = timezone.now()
        self.response_message = response_message
        self.save()
