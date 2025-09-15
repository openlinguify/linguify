from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import logging

# Les imports des modèles de cours se feront via __init__.py pour éviter l'import cyclique

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
    ('nl', 'Dutch'),
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


# =============================================================================
# MODÈLES DE COURS
# =============================================================================

class CourseUnit(models.Model):
    """
    Représente une unité dans un cours de langue (ex: Unité 1, Unité 2, etc.)
    """
    language = models.ForeignKey('Language', on_delete=models.CASCADE, related_name='units')
    unit_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-book')
    color = models.CharField(max_length=7, default='#10b981')  # Couleur hex
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Course Unit"
        verbose_name_plural = "Course Units"
        ordering = ['language', 'order', 'unit_number']
        unique_together = ['language', 'unit_number']

    def __str__(self):
        return f"{self.language.name} - Unité {self.unit_number}: {self.title}"

    def get_modules_count(self):
        return self.modules.count()

    def get_completed_modules_for_user(self, user):
        return self.modules.filter(
            progress_records__user=user,
            progress_records__is_completed=True
        ).count()


class CourseModule(models.Model):
    """
    Représente un module dans une unité (ex: Vocabulaire, Grammaire, etc.)
    """
    MODULE_TYPE_CHOICES = [
        ('vocabulary', 'Vocabulaire'),
        ('grammar', 'Grammaire'),
        ('listening', 'Écoute'),
        ('speaking', 'Expression orale'),
        ('reading', 'Lecture'),
        ('writing', 'Écriture'),
        ('culture', 'Culture'),
        ('review', 'Révision'),
    ]

    unit = models.ForeignKey(CourseUnit, on_delete=models.CASCADE, related_name='modules')
    module_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    module_type = models.CharField(max_length=20, choices=MODULE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    content = models.JSONField(default=dict, blank=True)  # Contenu structuré du module
    estimated_duration = models.PositiveIntegerField(default=10, help_text="Durée en minutes")
    xp_reward = models.PositiveIntegerField(default=10)
    is_locked = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Course Module"
        verbose_name_plural = "Course Modules"
        ordering = ['unit', 'order', 'module_number']
        unique_together = ['unit', 'module_number']

    def __str__(self):
        return f"{self.unit} - Module {self.module_number}: {self.title}"

    def is_available_for_user(self, user):
        """Vérifie si le module est disponible pour l'utilisateur"""
        if not self.is_locked:
            return True

        # Vérifier si les modules précédents sont complétés
        previous_modules = self.unit.modules.filter(order__lt=self.order)
        for module in previous_modules:
            if not ModuleProgress.objects.filter(
                user=user,
                module=module,
                is_completed=True
            ).exists():
                return False
        return True


class ModuleProgress(models.Model):
    """
    Suivi de la progression d'un utilisateur sur un module
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='progress_records')
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)
    attempts = models.PositiveIntegerField(default=0)
    time_spent = models.PositiveIntegerField(default=0, help_text="Temps en secondes")
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Module Progress"
        verbose_name_plural = "Module Progress Records"
        unique_together = ['user', 'module']

    def __str__(self):
        return f"{self.user.username} - {self.module.title} ({'Complété' if self.is_completed else 'En cours'})"

    def complete(self, score=None):
        """Marque le module comme complété"""
        self.is_completed = True
        self.completion_date = timezone.now()
        if score:
            self.score = score
        self.save()


class UserCourseProgress(models.Model):
    """
    Progression globale d'un utilisateur dans un cours de langue
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='language_course_progress')
    language = models.ForeignKey('Language', on_delete=models.CASCADE)
    current_unit = models.ForeignKey(CourseUnit, on_delete=models.SET_NULL, null=True, blank=True)
    current_module = models.ForeignKey(CourseModule, on_delete=models.SET_NULL, null=True, blank=True)
    total_xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    started_date = models.DateTimeField(auto_now_add=True)
    last_activity_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Course Progress"
        verbose_name_plural = "User Course Progress Records"
        unique_together = ['user', 'language']

    def __str__(self):
        return f"{self.user.username} - {self.language.name} (Niveau {self.level})"

    def get_completion_percentage(self):
        """Calcule le pourcentage de complétion du cours"""
        total_modules = CourseModule.objects.filter(unit__language=self.language).count()
        completed_modules = ModuleProgress.objects.filter(
            user=self.user,
            module__unit__language=self.language,
            is_completed=True
        ).count()

        if total_modules == 0:
            return 0
        return int((completed_modules / total_modules) * 100)