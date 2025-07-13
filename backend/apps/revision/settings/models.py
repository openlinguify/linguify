"""
Modèles pour les paramètres de l'application Révision
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class RevisionSettings(models.Model):
    """
    Paramètres généraux pour l'application Révision par utilisateur
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Facile'),
        ('normal', 'Normal'),
        ('hard', 'Difficile'),
        ('expert', 'Expert'),
    ]
    
    STUDY_MODE_CHOICES = [
        ('spaced', 'Répétition espacée'),
        ('intensive', 'Révision intensive'),
        ('mixed', 'Mode mixte'),
        ('custom', 'Personnalisé'),
    ]
    
    NOTIFICATION_FREQUENCY_CHOICES = [
        ('daily', 'Quotidienne'),
        ('weekly', 'Hebdomadaire'),
        ('custom', 'Personnalisée'),
        ('disabled', 'Désactivée'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='revision_settings'
    )
    
    # Paramètres généraux d'apprentissage
    default_study_mode = models.CharField(
        max_length=20,
        choices=STUDY_MODE_CHOICES,
        default='spaced',
        help_text="Mode d'étude par défaut pour les nouvelles sessions"
    )
    
    default_difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='normal',
        help_text="Niveau de difficulté par défaut"
    )
    
    # Paramètres de session
    default_session_duration = models.PositiveIntegerField(
        default=20,
        validators=[MinValueValidator(5), MaxValueValidator(120)],
        help_text="Durée par défaut d'une session en minutes"
    )
    
    cards_per_session = models.PositiveIntegerField(
        default=20,
        validators=[MinValueValidator(5), MaxValueValidator(100)],
        help_text="Nombre de cartes par session par défaut"
    )
    
    auto_advance = models.BooleanField(
        default=True,
        help_text="Passer automatiquement à la carte suivante après validation"
    )
    
    # Paramètres de révision espacée
    spaced_repetition_enabled = models.BooleanField(
        default=True,
        help_text="Activer l'algorithme de répétition espacée"
    )
    
    initial_interval_easy = models.PositiveIntegerField(
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(30)],
        help_text="Intervalle initial en jours pour les cartes faciles"
    )
    
    initial_interval_normal = models.PositiveIntegerField(
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(30)],
        help_text="Intervalle initial en jours pour les cartes normales"
    )
    
    initial_interval_hard = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(30)],
        help_text="Intervalle initial en jours pour les cartes difficiles"
    )
    
    # Paramètres de performance
    required_reviews_to_learn = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Nombre de révisions correctes pour marquer une carte comme apprise"
    )
    
    reset_on_wrong_answer = models.BooleanField(
        default=False,
        help_text="Remettre le compteur à zéro si mauvaise réponse"
    )
    
    show_progress_stats = models.BooleanField(
        default=True,
        help_text="Afficher les statistiques de progression"
    )
    
    # Paramètres de notifications
    daily_reminder_enabled = models.BooleanField(
        default=True,
        help_text="Activer les rappels quotidiens"
    )
    
    reminder_time = models.TimeField(
        default='18:00',
        help_text="Heure des rappels quotidiens"
    )
    
    notification_frequency = models.CharField(
        max_length=20,
        choices=NOTIFICATION_FREQUENCY_CHOICES,
        default='daily',
        help_text="Fréquence des notifications"
    )
    
    # Paramètres d'interface
    enable_animations = models.BooleanField(
        default=True,
        help_text="Activer les animations dans l'interface"
    )
    
    auto_play_audio = models.BooleanField(
        default=False,
        help_text="Lecture automatique de l'audio (si disponible)"
    )
    
    keyboard_shortcuts_enabled = models.BooleanField(
        default=True,
        help_text="Activer les raccourcis clavier"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'revision'
        verbose_name = "Paramètres de révision"
        verbose_name_plural = "Paramètres de révision"
        
    def __str__(self):
        return f"Paramètres de révision - {self.user.username}"
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """
        Récupère ou crée les paramètres de révision pour un utilisateur
        """
        logger.info(f"Getting or creating revision settings for user {user.username}")
        settings_obj, created = cls.objects.get_or_create(user=user)
        if created:
            logger.info(f"Created new revision settings for user {user.username}")
        return settings_obj
    
    def apply_preset(self, preset_name):
        """
        Applique un preset de configuration prédéfini
        """
        logger.info(f"Applying preset '{preset_name}' for user {self.user.username}")
        
        presets = {
            'beginner': {
                'default_difficulty': 'easy',
                'cards_per_session': 10,
                'default_session_duration': 15,
                'required_reviews_to_learn': 2,
                'initial_interval_easy': 2,
                'reset_on_wrong_answer': False,
            },
            'intermediate': {
                'default_difficulty': 'normal',
                'cards_per_session': 20,
                'default_session_duration': 20,
                'required_reviews_to_learn': 3,
                'initial_interval_normal': 2,
                'reset_on_wrong_answer': False,
            },
            'advanced': {
                'default_difficulty': 'hard',
                'cards_per_session': 30,
                'default_session_duration': 30,
                'required_reviews_to_learn': 4,
                'initial_interval_hard': 1,
                'reset_on_wrong_answer': True,
            },
            'intensive': {
                'default_study_mode': 'intensive',
                'cards_per_session': 50,
                'default_session_duration': 45,
                'spaced_repetition_enabled': False,
                'auto_advance': True,
            },
        }
        
        if preset_name in presets:
            preset_data = presets[preset_name]
            for field, value in preset_data.items():
                if hasattr(self, field):
                    setattr(self, field, value)
            self.save()
            logger.info(f"Applied preset '{preset_name}' successfully")
            return True
        else:
            logger.warning(f"Unknown preset '{preset_name}'")
            return False
    
    def get_session_config(self):
        """
        Retourne une configuration pour une session de révision
        """
        return {
            'study_mode': self.default_study_mode,
            'difficulty': self.default_difficulty,
            'session_duration': self.default_session_duration,
            'cards_per_session': self.cards_per_session,
            'auto_advance': self.auto_advance,
            'spaced_repetition': self.spaced_repetition_enabled,
            'required_reviews': self.required_reviews_to_learn,
            'reset_on_wrong': self.reset_on_wrong_answer,
        }


class RevisionSessionConfig(models.Model):
    """
    Configuration spécifique pour une session de révision
    """
    SESSION_TYPE_CHOICES = [
        ('quick', 'Session rapide'),
        ('standard', 'Session standard'),
        ('extended', 'Session étendue'),
        ('custom', 'Session personnalisée'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='revision_session_configs'
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Nom de cette configuration"
    )
    
    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPE_CHOICES,
        default='standard'
    )
    
    # Configuration spécifique
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(5), MaxValueValidator(120)]
    )
    
    target_cards = models.PositiveIntegerField(
        validators=[MinValueValidator(5), MaxValueValidator(200)]
    )
    
    include_new_cards = models.BooleanField(default=True)
    include_review_cards = models.BooleanField(default=True)
    include_difficult_cards = models.BooleanField(default=True)
    
    # Filtres
    tags_filter = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags à inclure dans cette session"
    )
    
    difficulty_filter = models.JSONField(
        default=list,
        blank=True,
        help_text="Niveaux de difficulté à inclure"
    )
    
    is_default = models.BooleanField(
        default=False,
        help_text="Configuration par défaut pour cet utilisateur"
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'revision'
        unique_together = ['user', 'name']
        verbose_name = "Configuration de session"
        verbose_name_plural = "Configurations de sessions"
        
    def __str__(self):
        return f"{self.name} ({self.user.username})"