# -*- coding: utf-8 -*-
"""
Teacher Availability models
Manage when teachers are available for appointments
"""
from django.db import models
from django.utils import timezone
import uuid

from cms.core.models import TimestampedModel
from apps.teachers.models import Teacher


class RecurringAvailability(TimestampedModel):
    """Recurring availability patterns (e.g., Every Monday 9am-5pm)."""

    WEEKDAY_CHOICES = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='recurring_availabilities')
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    valid_from = models.DateField(default=timezone.now)
    valid_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'cms_recurring_availability'
        ordering = ['weekday', 'start_time']

    def __str__(self):
        return f"{self.teacher.full_name} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"


class TeacherAvailability(TimestampedModel):
    """Specific availability slots for booking."""

    availability_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    recurring_pattern = models.ForeignKey(RecurringAvailability, on_delete=models.SET_NULL, null=True, blank=True)
    is_manual = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    is_booked = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'cms_teacher_availability'
        ordering = ['date', 'start_time']
        unique_together = ['teacher', 'date', 'start_time']

    def __str__(self):
        return f"{self.teacher.full_name} - {self.date} {self.start_time}-{self.end_time}"

    def mark_booked(self):
        self.is_booked = True
        self.is_available = False
        self.save(update_fields=['is_booked', 'is_available'])


class TimeSlot(TimestampedModel):
    """Individual bookable time slots (30min, 60min, etc.)."""

    slot_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='time_slots')
    availability = models.ForeignKey(TeacherAvailability, on_delete=models.CASCADE, related_name='time_slots')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    is_booked = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    buffer_before = models.PositiveIntegerField(default=0)
    buffer_after = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'cms_time_slots'
        ordering = ['start_datetime']

    def __str__(self):
        return f"{self.teacher.full_name} - {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"

    def is_available_for_booking(self):
        return not (self.is_booked or self.is_blocked) and self.start_datetime > timezone.now()
