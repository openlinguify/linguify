"""
Learning models for student course consumption.
Tracks student progress, purchases, and interactions with teacher content.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.course.models.core import Unit, Lesson, ContentLesson
from apps.authentication.models import User as LinguifyUser

class StudentCourse(models.Model):
    """Student course enrollment and purchase record."""
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        EXPIRED = 'expired', 'Expired'
        SUSPENDED = 'suspended', 'Suspended'
    
    student = models.ForeignKey(LinguifyUser, on_delete=models.CASCADE, related_name='enrolled_courses')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='student_enrollments')
    
    # Purchase info
    purchased_at = models.DateTimeField(default=timezone.now)
    price_paid = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True)
    
    # Access control
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    access_expires_at = models.DateTimeField(null=True, blank=True, help_text="Lifetime access if null")
    
    # Progress tracking
    progress_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    last_accessed = models.DateTimeField(default=timezone.now)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    
    # Teacher info (denormalized for performance)
    teacher_name = models.CharField(max_length=200)
    teacher_id = models.PositiveIntegerField(help_text="Teacher ID from CMS")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_courses'
        unique_together = ['student', 'unit']
        ordering = ['-last_accessed']
    
    def __str__(self):
        return f"{self.student.username} - {self.unit.title}"
    
    @property
    def is_accessible(self):
        """Check if course is accessible to student."""
        if self.status != self.Status.ACTIVE:
            return False
        if self.access_expires_at and self.access_expires_at < timezone.now():
            return False
        return True
    
    def update_progress(self):
        """Recalculate progress based on completed lessons."""
        total_lessons = self.unit.lessons.count()
        if total_lessons == 0:
            self.progress_percentage = 0
        else:
            completed_lessons = StudentLessonProgress.objects.filter(
                student_course=self,
                status=StudentLessonProgress.Status.COMPLETED
            ).count()
            self.progress_percentage = int((completed_lessons / total_lessons) * 100)
        self.save(update_fields=['progress_percentage'])

class StudentLessonProgress(models.Model):
    """Individual lesson progress for students."""
    
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', 'Not Started'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        LOCKED = 'locked', 'Locked'
    
    student_course = models.ForeignKey(StudentCourse, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    progress_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    
    # Time tracking
    time_spent_minutes = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(default=timezone.now)
    
    # Attempt tracking
    attempts_count = models.PositiveIntegerField(default=0)
    best_score = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_lesson_progress'
        unique_together = ['student_course', 'lesson']
        ordering = ['lesson__order']
    
    def __str__(self):
        return f"{self.student_course.student.username} - {self.lesson.title} ({self.status})"
    
    def start_lesson(self):
        """Mark lesson as started."""
        if self.status == self.Status.NOT_STARTED:
            self.status = self.Status.IN_PROGRESS
            self.started_at = timezone.now()
            self.save()
    
    def complete_lesson(self, score=100):
        """Mark lesson as completed."""
        self.status = self.Status.COMPLETED
        self.progress_percentage = 100
        self.completed_at = timezone.now()
        self.best_score = max(self.best_score, score)
        self.save()
        
        # Update course progress
        self.student_course.update_progress()

class StudentContentProgress(models.Model):
    """Progress on individual content pieces within lessons."""
    
    lesson_progress = models.ForeignKey(StudentLessonProgress, on_delete=models.CASCADE, related_name='content_progress')
    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE)
    
    is_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    attempts = models.PositiveIntegerField(default=0)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    
    # Store student responses/answers
    user_answers = models.JSONField(default=dict, blank=True)
    correct_answers = models.JSONField(default=dict, blank=True)
    
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_content_progress'
        unique_together = ['lesson_progress', 'content_lesson']
    
    def __str__(self):
        return f"{self.lesson_progress.student_course.student.username} - {self.content_lesson.title}"

class LearningSession(models.Model):
    """Track active learning sessions for analytics."""
    
    student = models.ForeignKey(LinguifyUser, on_delete=models.CASCADE, related_name='learning_sessions')
    student_course = models.ForeignKey(StudentCourse, on_delete=models.CASCADE, related_name='sessions')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    
    # Session data
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    
    # Activity tracking
    interactions_count = models.PositiveIntegerField(default=0)
    exercises_completed = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'learning_sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.started_at}"
    
    def end_session(self):
        """End the learning session."""
        self.ended_at = timezone.now()
        self.duration_seconds = int((self.ended_at - self.started_at).total_seconds())
        self.save()

class StudentReview(models.Model):
    """Student reviews and ratings for courses."""
    
    student = models.ForeignKey(LinguifyUser, on_delete=models.CASCADE, related_name='course_reviews')
    student_course = models.ForeignKey(StudentCourse, on_delete=models.CASCADE, related_name='reviews')
    
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    review_text = models.TextField(blank=True)
    
    # Review metadata
    is_verified_purchase = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    helpful_votes = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_reviews'
        unique_together = ['student', 'student_course']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.student_course.unit.title} ({self.rating}⭐)"

class LearningAnalytics(models.Model):
    """Daily aggregated learning analytics."""
    
    student = models.ForeignKey(LinguifyUser, on_delete=models.CASCADE, related_name='learning_analytics')
    date = models.DateField()
    
    # Time metrics
    total_time_minutes = models.PositiveIntegerField(default=0)
    lessons_started = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    exercises_completed = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    average_score = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    streak_days = models.PositiveIntegerField(default=0)
    
    # Engagement metrics
    sessions_count = models.PositiveIntegerField(default=0)
    unique_courses_accessed = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_analytics'
        unique_together = ['student', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.username} - {self.date}"