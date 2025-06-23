# -*- coding: utf-8 -*-
"""User Progress Models for tracking learning progress."""

from django.db import models
from django.contrib.auth import get_user_model
from .core import Unit, Chapter, Lesson

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