from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Exemple de modèle pour Language Learning
class LanguagelearningItem(models.Model):
    """Modèle de base pour Language Learning"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='language_learning_items')
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Language Learning Item"
        verbose_name_plural = "Language Learning Items"
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title

LANGUAGE_CHOICES = [
    ('en', 'English'),
    ('fr', 'French'),
    ('es', 'Spanish'),
    ('de', 'German'),
    ('it', 'Italian'),
    ('pt', 'Portuguese'),
    ('nl', 'Dutch'),
    ('ja', 'Japanese'),
    ('ko', 'Korean'),
    ('zh', 'Chinese'),
]

PROFICIENCY_LEVELS = [
    ('beginner', 'Beginner'),
    ('elementary', 'Elementary'),
    ('intermediate', 'Intermediate'),
    ('upper_intermediate', 'Upper Intermediate'),
    ('advanced', 'Advanced'),
    ('proficient', 'Proficient'),
]

class Language(models.Model):
    """Model representing a language that can be learned"""
    code = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, unique=True)
    name = models.CharField(max_length=50)
    native_name = models.CharField(max_length=50, blank=True)
    flag_emoji = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Language"
        verbose_name_plural = "Languages"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class UserLanguage(models.Model):
    """Model representing a user's language learning journey"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_languages')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    proficiency_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS, default='beginner')
    target_level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS, default='intermediate')
    daily_goal = models.PositiveIntegerField(default=15, help_text="Minutes per day")
    streak_count = models.PositiveIntegerField(default=0)
    total_time_spent = models.PositiveIntegerField(default=0, help_text="Total minutes spent")
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "User Language"
        verbose_name_plural = "User Languages"
        unique_together = ['user', 'language']
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.username} learning {self.language.name}"

class Lesson(models.Model):
    """Model representing a language lesson"""
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS)
    order = models.PositiveIntegerField(default=0)
    estimated_duration = models.PositiveIntegerField(default=10, help_text="Minutes")
    content = models.JSONField(default=dict, blank=True, help_text="Lesson content and exercises")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
        ordering = ['language', 'level', 'order']
        unique_together = ['language', 'level', 'order']
    
    def __str__(self):
        return f"{self.language.name} - {self.title}"

class UserLessonProgress(models.Model):
    """Model tracking user progress through lessons"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True, help_text="Lesson score (0-100)")
    time_spent = models.PositiveIntegerField(default=0, help_text="Minutes spent")
    completed_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Lesson Progress"
        verbose_name_plural = "User Lesson Progress"
        unique_together = ['user', 'lesson']
        ordering = ['-updated_at']
    
    def __str__(self):
        status = "✅" if self.is_completed else "🔄"
        return f"{status} {self.user.username} - {self.lesson.title}"