from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


# Exemple de modèle pour Language Learning
class LanguagelearningItem(models.Model):
    """Modèle de base pour Language Learning"""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Facile'),
        ('normal', 'Normal'),
        ('hard', 'Difficile'),
    ]
    
    ITEM_TYPE_CHOICES = [
        ('lesson', 'Leçon'),
        ('exercise', 'Exercice'),
        ('vocabulary', 'Vocabulaire'),
        ('grammar', 'Grammaire'),
        ('listening', 'Écoute'),
        ('speaking', 'Expression orale'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='language_learning_items')
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    content = models.TextField(blank=True, verbose_name="Contenu")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='normal')
    item_type = models.CharField(max_length=15, choices=ITEM_TYPE_CHOICES, default='lesson')
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True, blank=True)
    estimated_duration = models.PositiveIntegerField(default=10, help_text="Durée estimée en minutes")
    order_index = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    def get_difficulty_display(self):
        """Retourne l'affichage de la difficulté"""
        return dict(self.DIFFICULTY_CHOICES).get(self.difficulty, self.difficulty)
    
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
    lessons_completed = models.PositiveIntegerField(default=0)
    progress_percentage = models.FloatField(default=0.0, help_text="Overall progress percentage")
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


# =============================================================================
# PARAMÈTRES ET CONFIGURATION
# =============================================================================

class LanguageLearningSettings(models.Model):
    """
    Paramètres généraux d'apprentissage des langues pour un utilisateur
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Facile'),
        ('normal', 'Normal'),
        ('hard', 'Difficile'),
        ('adaptive', 'Adaptatif')
    ]
    
    REMINDER_FREQUENCY_CHOICES = [
        ('daily', 'Quotidien'),
        ('weekdays', 'Jours de semaine'),
        ('custom', 'Personnalisé')
    ]
    
    FONT_SIZE_CHOICES = [
        ('small', 'Petit'),
        ('medium', 'Moyen'),
        ('large', 'Grand')
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='language_learning_settings'
    )
    
    # Paramètres généraux d'apprentissage
    preferred_study_time = models.TimeField(default='18:00', help_text="Heure préférée pour étudier")
    daily_goal_minutes = models.PositiveIntegerField(
        default=15,
        validators=[MinValueValidator(5), MaxValueValidator(300)],
        help_text="Objectif quotidien en minutes"
    )
    weekly_goal_days = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        help_text="Nombre de jours par semaine"
    )
    
    # Notifications et rappels
    reminder_enabled = models.BooleanField(default=True)
    reminder_frequency = models.CharField(
        max_length=10,
        choices=REMINDER_FREQUENCY_CHOICES,
        default='daily'
    )
    streak_notifications = models.BooleanField(default=True)
    achievement_notifications = models.BooleanField(default=True)
    
    # Paramètres de difficulté
    auto_difficulty_adjustment = models.BooleanField(default=True)
    preferred_difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='adaptive'
    )
    
    # Interface et expérience utilisateur
    show_pronunciation_hints = models.BooleanField(default=True)
    enable_audio_playback = models.BooleanField(default=True)
    audio_playback_speed = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.5), MaxValueValidator(2.0)]
    )
    show_progress_animations = models.BooleanField(default=True)
    font_size = models.CharField(
        max_length=10,
        choices=FONT_SIZE_CHOICES,
        default='medium'
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paramètres d'apprentissage des langues"
        verbose_name_plural = "Paramètres d'apprentissage des langues"
    
    def __str__(self):
        return f"Paramètres de {self.user.username}"
    
    def apply_preset(self, preset_name):
        """Applique un preset de configuration"""
        presets = {
            'casual': {
                'daily_goal_minutes': 10,
                'weekly_goal_days': 3,
                'preferred_difficulty': 'easy',
                'auto_difficulty_adjustment': True,
                'reminder_frequency': 'custom'
            },
            'regular': {
                'daily_goal_minutes': 15,
                'weekly_goal_days': 5,
                'preferred_difficulty': 'normal',
                'auto_difficulty_adjustment': True,
                'reminder_frequency': 'weekdays'
            },
            'intensive': {
                'daily_goal_minutes': 30,
                'weekly_goal_days': 6,
                'preferred_difficulty': 'hard',
                'auto_difficulty_adjustment': False,
                'reminder_frequency': 'daily'
            },
            'immersion': {
                'daily_goal_minutes': 60,
                'weekly_goal_days': 7,
                'preferred_difficulty': 'hard',
                'auto_difficulty_adjustment': False,
                'reminder_frequency': 'daily'
            }
        }
        
        preset_settings = presets.get(preset_name)
        if preset_settings:
            for field, value in preset_settings.items():
                setattr(self, field, value)
            self.save()
            logger.info(f"Applied preset '{preset_name}' for user {self.user.username}")
            return True
        
        return False