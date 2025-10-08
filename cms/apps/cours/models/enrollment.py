# -*- coding: utf-8 -*-
"""
Course Enrollment model
Track student enrollments and progress
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from cms.core.models import TimestampedModel
from .course import Course
from .lesson import CourseLesson


class CourseEnrollment(TimestampedModel):
    """
    Student enrollment in a course.
    Tracks progress, completion, and access.
    """

    STATUS_CHOICES = [
        ('active', '✅ Active'),
        ('completed', '🎓 Completed'),
        ('expired', '⏰ Expired'),
        ('suspended', '🚫 Suspended'),
    ]

    # Student and course
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    # Enrollment metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    # Progress tracking
    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Course completion percentage"
    )
    completed_lessons = models.ManyToManyField(
        CourseLesson,
        related_name='completed_by',
        blank=True
    )
    last_accessed = models.DateTimeField(null=True, blank=True)

    # Completion
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Certificate
    certificate_issued = models.BooleanField(default=False)
    certificate_issued_at = models.DateTimeField(null=True, blank=True)

    # Access control
    has_lifetime_access = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Payment reference (if applicable)
    payment_reference = models.CharField(max_length=100, blank=True)
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    class Meta:
        db_table = 'cms_course_enrollments'
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course', 'status']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.title}"

    def mark_lesson_complete(self, lesson):
        """Mark a lesson as completed."""
        if lesson not in self.completed_lessons.all():
            self.completed_lessons.add(lesson)
            self.last_accessed = timezone.now()
            self.update_progress()

    def update_progress(self):
        """Recalculate course progress percentage."""
        total_lessons = self.course.lessons.filter(is_published=True).count()
        if total_lessons > 0:
            completed_count = self.completed_lessons.filter(is_published=True).count()
            self.progress_percentage = (completed_count / total_lessons) * 100

            # Check if course is completed
            if self.progress_percentage >= 100 and not self.is_completed:
                self.mark_complete()
        else:
            self.progress_percentage = 0

        self.save(update_fields=['progress_percentage', 'last_accessed'])

    def mark_complete(self):
        """Mark the enrollment as completed."""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.status = 'completed'
        self.save(update_fields=['is_completed', 'completed_at', 'status'])

        # Issue certificate if course has one
        if self.course.has_certificate and not self.certificate_issued:
            self.issue_certificate()

    def issue_certificate(self):
        """Issue a certificate for course completion."""
        self.certificate_issued = True
        self.certificate_issued_at = timezone.now()
        self.save(update_fields=['certificate_issued', 'certificate_issued_at'])

    def is_accessible(self):
        """Check if student can still access the course."""
        if self.status == 'suspended':
            return False

        if not self.has_lifetime_access and self.expires_at:
            return timezone.now() < self.expires_at

        return True

    def extend_access(self, days=None, indefinite=False):
        """Extend course access."""
        if indefinite:
            self.has_lifetime_access = True
            self.expires_at = None
        elif days:
            if self.expires_at:
                self.expires_at += timezone.timedelta(days=days)
            else:
                self.expires_at = timezone.now() + timezone.timedelta(days=days)

        self.save(update_fields=['has_lifetime_access', 'expires_at'])
