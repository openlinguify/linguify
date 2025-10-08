"""
Scheduling models for teacher availability and bookings.
"""
from django.db import models
from django.utils import timezone
from cms.core.models import TimestampedModel
from apps.teachers.models import Teacher

class PrivateLesson(TimestampedModel):
    """Private lesson bookings."""
    
    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Programmé'
        CONFIRMED = 'confirmed', 'Confirmé'
        IN_PROGRESS = 'in_progress', 'En cours'
        COMPLETED = 'completed', 'Terminé'
        CANCELLED = 'cancelled', 'Annulé'
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='private_lessons')
    student_id = models.PositiveIntegerField(help_text="Student ID from backend")
    
    # Scheduling
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    
    # Content
    topic = models.CharField(max_length=200, blank=True)
    language = models.CharField(max_length=10, help_text="Language code")
    level = models.CharField(max_length=10, help_text="Student level")
    
    # Pricing
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Meeting details
    meeting_url = models.URLField(blank=True)
    meeting_id = models.CharField(max_length=100, blank=True)
    
    # Notes
    teacher_notes = models.TextField(blank=True)
    student_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'private_lessons'
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"Lesson: {self.teacher.full_name} - {self.scheduled_date}"
    
    @property
    def is_upcoming(self):
        return self.scheduled_date > timezone.now() and self.status in ['scheduled', 'confirmed']

class TeacherSchedule(TimestampedModel):
    """Teacher's custom schedule overrides."""
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='schedule_overrides')
    date = models.DateField()
    is_available = models.BooleanField(default=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'teacher_schedules'
        unique_together = ['teacher', 'date']
        ordering = ['date']
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.date}"