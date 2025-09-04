"""
Teaching models for private lesson booking and management.
Synced with CMS teacher data and scheduling.
"""
from django.db import models
from django.utils import timezone as django_timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta
from apps.authentication.models import User as LinguifyUser

class Teacher(models.Model):
    """Backend teacher model synced from CMS."""
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        SUSPENDED = 'suspended', 'Suspended'
    
    # Synced from CMS
    cms_teacher_id = models.PositiveIntegerField(unique=True, help_text="Teacher ID from CMS")
    user_id = models.PositiveIntegerField(help_text="User ID from CMS")
    
    # Profile data
    full_name = models.CharField(max_length=200)
    bio_en = models.TextField(blank=True)
    bio_fr = models.TextField(blank=True)
    bio_es = models.TextField(blank=True)
    bio_nl = models.TextField(blank=True)
    
    profile_picture_url = models.URLField(blank=True)
    
    # Teaching info
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    years_experience = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_hours_taught = models.PositiveIntegerField(default=0)
    
    # Availability
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    teacher_timezone = models.CharField(max_length=50, default='Europe/Paris')
    available_for_individual = models.BooleanField(default=True)
    max_students_per_class = models.PositiveIntegerField(default=1)
    
    # Sync info
    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teaching_teachers'
        ordering = ['-average_rating', 'full_name']
    
    def __str__(self):
        return f"{self.full_name} (${self.hourly_rate}/hr)"
    
    @property
    def is_available_for_booking(self):
        """Check if teacher is available for new bookings."""
        return (self.status == self.Status.ACTIVE and 
                self.available_for_individual)
    
    @property 
    def total_lessons(self):
        """Get total number of completed lessons."""
        return self.teaching_sessions.filter(status='completed').count()
    
    def get_bio(self, language='fr'):
        """Get bio in specified language with fallback."""
        bio_field = f"bio_{language}"
        if hasattr(self, bio_field):
            bio = getattr(self, bio_field)
            if bio:
                return bio
        return self.bio_en or "No biography available"

class TeacherLanguage(models.Model):
    """Languages taught by teacher."""
    
    class Proficiency(models.TextChoices):
        NATIVE = 'native', 'Native Speaker'
        FLUENT = 'fluent', 'Fluent'
        INTERMEDIATE = 'intermediate', 'Intermediate'
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teaching_languages')
    language_code = models.CharField(max_length=10)
    language_name = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=20, choices=Proficiency.choices)
    can_teach = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'teacher_teaching_languages'
        unique_together = ['teacher', 'language_code']
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.language_name}"

class TeacherAvailability(models.Model):
    """Teacher weekly availability schedule."""
    
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 1, 'Monday'
        TUESDAY = 2, 'Tuesday'
        WEDNESDAY = 3, 'Wednesday'
        THURSDAY = 4, 'Thursday'
        FRIDAY = 5, 'Friday'
        SATURDAY = 6, 'Saturday'
        SUNDAY = 7, 'Sunday'
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='availability_schedule')
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teacher_availability_schedule'
        unique_together = ['teacher', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

class PrivateLesson(models.Model):
    """Private lesson booking between student and teacher."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Confirmation'
        CONFIRMED = 'confirmed', 'Confirmed'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED_STUDENT = 'cancelled_student', 'Cancelled by Student'
        CANCELLED_TEACHER = 'cancelled_teacher', 'Cancelled by Teacher'
        NO_SHOW_STUDENT = 'no_show_student', 'Student No-Show'
        NO_SHOW_TEACHER = 'no_show_teacher', 'Teacher No-Show'
    
    class MeetingType(models.TextChoices):
        VIDEO_CALL = 'video_call', 'Video Call'
        PHONE_CALL = 'phone_call', 'Phone Call'
        IN_PERSON = 'in_person', 'In Person'
    
    # Participants
    student = models.ForeignKey(LinguifyUser, on_delete=models.CASCADE, related_name='private_lessons')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teaching_sessions')
    
    # Scheduling
    scheduled_datetime = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60, validators=[MinValueValidator(30), MaxValueValidator(180)])
    timezone_used = models.CharField(max_length=50, default='Europe/Paris')
    
    # Lesson details
    language = models.CharField(max_length=10, help_text="Language code being taught")
    level = models.CharField(max_length=10, help_text="Student level (A1, A2, etc.)")
    topic = models.CharField(max_length=200, blank=True, help_text="Lesson topic or focus")
    student_goals = models.TextField(blank=True, help_text="What student wants to learn")
    
    # Meeting info
    meeting_type = models.CharField(max_length=20, choices=MeetingType.choices, default=MeetingType.VIDEO_CALL)
    meeting_url = models.URLField(blank=True)
    meeting_id = models.CharField(max_length=100, blank=True)
    meeting_password = models.CharField(max_length=50, blank=True)
    
    # Status and management
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    booking_reference = models.CharField(max_length=20, unique=True)
    
    # Pricing
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    
    # Payment info
    payment_status = models.CharField(max_length=20, default='pending')
    payment_transaction_id = models.CharField(max_length=100, blank=True)
    
    # Session notes
    teacher_preparation_notes = models.TextField(blank=True)
    session_notes = models.TextField(blank=True)
    student_feedback = models.TextField(blank=True)
    teacher_feedback = models.TextField(blank=True)
    
    # Timestamps
    booked_at = models.DateTimeField(default=django_timezone.now)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'private_lessons'
        ordering = ['-scheduled_datetime']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['teacher', 'status']),
            models.Index(fields=['scheduled_datetime']),
        ]
    
    def __str__(self):
        return f"{self.student.username} <-> {self.teacher.full_name} on {self.scheduled_datetime}"
    
    @property
    def is_upcoming(self):
        """Check if lesson is upcoming."""
        return (self.scheduled_datetime > django_timezone.now() and 
                self.status in ['pending', 'confirmed'])
    
    @property
    def can_be_cancelled(self):
        """Check if lesson can still be cancelled."""
        cancellation_deadline = self.scheduled_datetime - timedelta(hours=12)
        return (django_timezone.now() < cancellation_deadline and 
                self.status in ['pending', 'confirmed'])
    
    @property
    def can_be_started(self):
        """Check if lesson can be started now."""
        start_window = self.scheduled_datetime - timedelta(minutes=10)
        end_window = self.scheduled_datetime + timedelta(minutes=30)
        now = django_timezone.now()
        return (start_window <= now <= end_window and 
                self.status == 'confirmed')
    
    def generate_meeting_url(self):
        """Generate meeting URL for the lesson."""
        # This would integrate with Zoom, Google Meet, etc.
        # For now, return a placeholder
        if self.meeting_type == self.MeetingType.VIDEO_CALL:
            self.meeting_url = f"https://meet.linguify.com/room/{self.booking_reference}"
            self.meeting_id = self.booking_reference
            self.save(update_fields=['meeting_url', 'meeting_id'])
    
    def confirm_lesson(self):
        """Confirm the lesson booking."""
        self.status = self.Status.CONFIRMED
        self.confirmed_at = django_timezone.now()
        self.generate_meeting_url()
        self.save()
    
    def start_lesson(self):
        """Start the lesson session."""
        self.status = self.Status.IN_PROGRESS
        self.started_at = django_timezone.now()
        self.save()
    
    def complete_lesson(self, session_notes="", teacher_feedback=""):
        """Complete the lesson session."""
        self.status = self.Status.COMPLETED
        self.ended_at = django_timezone.now()
        self.session_notes = session_notes
        self.teacher_feedback = teacher_feedback
        
        # Update teacher's total hours
        actual_duration = (self.ended_at - self.started_at).total_seconds() / 3600
        self.teacher.total_hours_taught += int(actual_duration)
        self.teacher.save(update_fields=['total_hours_taught'])
        
        self.save()
    
    def cancel_lesson(self, cancelled_by='student', reason=""):
        """Cancel the lesson."""
        self.status = (self.Status.CANCELLED_STUDENT if cancelled_by == 'student' 
                      else self.Status.CANCELLED_TEACHER)
        self.cancelled_at = django_timezone.now()
        self.session_notes = f"Cancelled by {cancelled_by}: {reason}"
        self.save()

class LessonRating(models.Model):
    """Student rating and review for completed lessons."""
    
    lesson = models.OneToOneField(PrivateLesson, on_delete=models.CASCADE, related_name='rating')
    
    # Ratings (1-5 stars)
    overall_rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    teaching_quality = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    communication = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    punctuality = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Review text
    review_title = models.CharField(max_length=200, blank=True)
    review_text = models.TextField(blank=True)
    
    # Metadata
    would_recommend = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    
    class Meta:
        db_table = 'lesson_ratings'
    
    def __str__(self):
        return f"{self.lesson.student.username} -> {self.lesson.teacher.full_name} ({self.overall_rating}⭐)"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update teacher's average rating
        self.update_teacher_rating()
    
    def update_teacher_rating(self):
        """Update teacher's average rating."""
        teacher = self.lesson.teacher
        ratings = LessonRating.objects.filter(lesson__teacher=teacher)
        
        if ratings.exists():
            avg_rating = sum(r.overall_rating for r in ratings) / ratings.count()
            teacher.average_rating = round(avg_rating, 2)
            teacher.save(update_fields=['average_rating'])

class TeacherScheduleOverride(models.Model):
    """Teacher schedule overrides for specific dates."""
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='schedule_overrides')
    date = models.DateField()
    is_available = models.BooleanField(default=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    reason = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teacher_schedule_overrides'
        unique_together = ['teacher', 'date']
        ordering = ['date']
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.date} ({'Available' if self.is_available else 'Unavailable'})"

class TeachingAnalytics(models.Model):
    """Daily teaching analytics for teachers."""
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='daily_analytics')
    date = models.DateField()
    
    # Session metrics
    lessons_scheduled = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    lessons_cancelled = models.PositiveIntegerField(default=0)
    no_shows = models.PositiveIntegerField(default=0)
    
    # Time metrics
    total_teaching_minutes = models.PositiveIntegerField(default=0)
    average_session_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    # Financial metrics
    gross_earnings = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    net_earnings = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teaching_analytics'
        unique_together = ['teacher', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.date}"