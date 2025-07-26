# -*- coding: utf-8 -*-
"""User Progress Models for tracking learning progress."""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from .core import Unit, Chapter, Lesson, ContentLesson

User = get_user_model()


class UserProgress(models.Model):
    """Track overall user progress."""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='course_progress'
    )
    
    # Progress tracking
    total_xp = models.PositiveIntegerField(default=0)
    streak_days = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(auto_now=True)
    
    # Level tracking
    current_level = models.CharField(
        max_length=10, 
        choices=[
            ('A1', 'Débutant A1'),
            ('A2', 'Élémentaire A2'),
            ('B1', 'Intermédiaire B1'),
            ('B2', 'Intermédiaire supérieur B2'),
            ('C1', 'Avancé C1'),
            ('C2', 'Maîtrise C2'),
        ],
        default='A1'
    )
    
    # Time tracking
    total_study_time = models.PositiveIntegerField(default=0)  # in minutes
    
    # Overall completion percentage
    overall_progress = models.PositiveIntegerField(default=0)  # 0-100
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        db_table = 'course_user_progress'
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress'
    
    def __str__(self):
        return f"{self.user.username} - {self.current_level} ({self.overall_progress}%)"
    
    @property
    def completed_lessons_count(self):
        """Count of completed lessons."""
        return LessonProgress.objects.filter(
            user=self.user,
            status='completed'
        ).count()
    
    def calculate_overall_progress(self):
        """Calculate overall progress percentage."""
        total_lessons = Lesson.objects.count()
        if total_lessons == 0:
            return 0
        
        completed_lessons = self.completed_lessons_count
        return min(100, int((completed_lessons / total_lessons) * 100))
    
    def update_progress(self):
        """Update calculated fields."""
        self.overall_progress = self.calculate_overall_progress()
        self.save()


class UnitProgress(models.Model):
    """Track progress within a specific unit."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    
    # Progress status
    status = models.CharField(
        max_length=20,
        choices=[
            ('not_started', 'Not Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('locked', 'Locked'),
        ],
        default='not_started'
    )
    
    # Progress tracking
    progress_percentage = models.PositiveIntegerField(default=0)  # 0-100
    chapters_completed = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_unit_progress'
        unique_together = ['user', 'unit']
        verbose_name = 'Unit Progress'
        verbose_name_plural = 'Unit Progress'
    
    def __str__(self):
        return f"{self.user.username} - {self.unit.title} ({self.progress_percentage}%)"
    
    @property
    def is_current(self):
        """Check if this is the user's current unit."""
        return self.status == 'in_progress'
    
    @property
    def is_completed(self):
        """Check if unit is completed."""
        return self.status == 'completed'
    
    @property
    def is_locked(self):
        """Check if unit is locked."""
        return self.status == 'locked'
    
    def calculate_progress(self):
        """Calculate progress percentage based on completed lessons."""
        total_lessons = self.unit.get_total_lessons_count()
        if total_lessons == 0:
            return 100
        
        # Count completed lessons that are either:
        # 1. Linked to chapters in this unit, OR
        # 2. Linked directly to this unit with no chapter
        from django.db.models import Q
        completed_lessons = LessonProgress.objects.filter(
            user=self.user,
            status='completed'
        ).filter(
            Q(lesson__chapter__unit=self.unit) | Q(lesson__unit=self.unit, lesson__chapter__isnull=True)
        ).count()
        
        return min(100, int((completed_lessons / total_lessons) * 100))
    
    def update_progress(self):
        """Update progress fields."""
        self.progress_percentage = self.calculate_progress()
        
        # Count completed lessons that are either:
        # 1. Linked to chapters in this unit, OR
        # 2. Linked directly to this unit with no chapter
        from django.db.models import Q
        self.lessons_completed = LessonProgress.objects.filter(
            user=self.user,
            status='completed'
        ).filter(
            Q(lesson__chapter__unit=self.unit) | Q(lesson__unit=self.unit, lesson__chapter__isnull=True)
        ).count()
        self.chapters_completed = ChapterProgress.objects.filter(
            user=self.user,
            chapter__unit=self.unit,
            status='completed'
        ).count()
        
        # Update status based on progress
        if self.progress_percentage == 100:
            self.status = 'completed'
            if not self.completed_at:
                from django.utils import timezone
                self.completed_at = timezone.now()
        elif self.progress_percentage > 0:
            self.status = 'in_progress'
            if not self.started_at:
                from django.utils import timezone
                self.started_at = timezone.now()
        
        self.save()


class ChapterProgress(models.Model):
    """Track progress within a specific chapter."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    
    # Progress status
    status = models.CharField(
        max_length=20,
        choices=[
            ('not_started', 'Not Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('locked', 'Locked'),
        ],
        default='not_started'
    )
    
    # Progress tracking
    progress_percentage = models.PositiveIntegerField(default=0)  # 0-100
    lessons_completed = models.PositiveIntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_chapter_progress'
        unique_together = ['user', 'chapter']
        verbose_name = 'Chapter Progress'
        verbose_name_plural = 'Chapter Progress'
    
    def __str__(self):
        return f"{self.user.username} - {self.chapter.title} ({self.progress_percentage}%)"


class LessonProgress(models.Model):
    """Track progress within a specific lesson."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    
    # Progress status
    status = models.CharField(
        max_length=20,
        choices=[
            ('not_started', 'Not Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('locked', 'Locked'),
        ],
        default='not_started'
    )
    
    # Progress tracking
    progress_percentage = models.PositiveIntegerField(default=0)  # 0-100
    attempts = models.PositiveIntegerField(default=0)
    best_score = models.PositiveIntegerField(default=0)  # 0-100
    
    # XP and rewards
    xp_earned = models.PositiveIntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_lesson_progress'
        unique_together = ['user', 'lesson']
        verbose_name = 'Lesson Progress'
        verbose_name_plural = 'Lesson Progress'
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} ({self.status})"
    
    @property
    def is_completed(self):
        """Check if lesson is completed."""
        return self.status == 'completed'
    
    def mark_completed(self, score=100):
        """Mark lesson as completed with a score."""
        from django.utils import timezone
        
        self.status = 'completed'
        self.progress_percentage = 100
        self.best_score = max(self.best_score, score)
        
        if not self.completed_at:
            self.completed_at = timezone.now()
        if not self.started_at:
            self.started_at = timezone.now()
        
        # Award XP (can be customized based on lesson difficulty)
        base_xp = 50
        bonus_xp = int((score / 100) * 25)  # Up to 25 bonus XP for perfect score
        self.xp_earned = base_xp + bonus_xp
        
        self.save()
        
        # Update user's total XP
        user_progress, created = UserProgress.objects.get_or_create(user=self.user)
        user_progress.total_xp += self.xp_earned
        user_progress.save()
        
        # Update chapter progress only if lesson has a chapter
        if self.lesson.chapter:
            chapter_progress, _ = ChapterProgress.objects.get_or_create(
                user=self.user, 
                chapter=self.lesson.chapter
            )
            chapter_progress.update_progress()
        
        # Update unit progress (get unit directly from lesson)
        unit_progress, _ = UnitProgress.objects.get_or_create(
            user=self.user, 
            unit=self.lesson.unit
        )
        unit_progress.update_progress()
        
        # Update overall user progress
        user_progress.update_progress()


class UserActivity(models.Model):
    """Track user learning activities for analytics and gamification."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Activity details
    activity_type = models.CharField(
        max_length=30,
        choices=[
            ('lesson_completed', 'Lesson Completed'),
            ('chapter_completed', 'Chapter Completed'),
            ('unit_completed', 'Unit Completed'),
            ('streak_milestone', 'Streak Milestone'),
            ('level_up', 'Level Up'),
            ('perfect_score', 'Perfect Score'),
        ]
    )
    
    # Related objects
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True)
    
    # Activity metadata
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    xp_earned = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=50, default='book')
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        db_table = 'course_user_activity'
        ordering = ['-created_at']
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


# =============================================================================
# STUDENT COURSE MODELS (from Learning app)
# =============================================================================

class StudentCourse(models.Model):
    """Student course enrollment and purchase record."""
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        EXPIRED = 'expired', 'Expired'
        SUSPENDED = 'suspended', 'Suspended'
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrolled_courses')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='student_enrollments')
    
    # Purchase info
    purchased_at = models.DateTimeField(default=timezone.now)
    price_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True, default=None)
    
    # Access control
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    access_expires_at = models.DateTimeField(null=True, blank=True, help_text="Lifetime access if null")
    
    # Progress tracking
    progress_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    last_accessed = models.DateTimeField(default=timezone.now)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    
    # Teacher info (denormalized for performance)
    teacher_name = models.CharField(max_length=200, blank=True)
    teacher_id = models.PositiveIntegerField(null=True, blank=True, help_text="Teacher ID from CMS")
    
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
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_sessions')
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
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
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
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_analytics')
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