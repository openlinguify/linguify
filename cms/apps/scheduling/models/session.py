# -*- coding: utf-8 -*-
"""
Session models
Notes and feedback after appointments
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import TimestampedModel
from .appointment import Appointment


class SessionNote(TimestampedModel):
    """Teacher's notes after a session."""

    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='session_note')

    # Content covered
    topics_covered = models.TextField(help_text="Topics/content covered in session")
    homework_assigned = models.TextField(blank=True)

    # Student performance
    student_performance = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)

    # Next session planning
    next_session_focus = models.TextField(blank=True)
    recommended_resources = models.TextField(blank=True)

    # Private notes
    private_notes = models.TextField(blank=True, help_text="Only visible to teacher")

    # Visibility
    is_shared_with_student = models.BooleanField(default=True)

    class Meta:
        db_table = 'cms_session_notes'

    def __str__(self):
        return f"Notes for {self.appointment.title}"


class SessionFeedback(TimestampedModel):
    """Student feedback and rating after session."""

    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='feedback')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_feedbacks')

    # Rating (1-5 stars)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    # Detailed ratings
    teaching_quality = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    communication = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    knowledge = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    # Written feedback
    comment = models.TextField(blank=True)
    what_went_well = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)

    # Would book again
    would_recommend = models.BooleanField(default=True)

    # Moderation
    is_published = models.BooleanField(default=True)

    class Meta:
        db_table = 'cms_session_feedbacks'

    def __str__(self):
        return f"Feedback: {self.appointment.title} ({self.rating}★)"
