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
    
    # Paramètres audio et voix
    audio_enabled = models.BooleanField(
        default=True,
        help_text="Activer la synthèse vocale"
    )
    
    audio_speed = models.FloatField(
        default=0.9,
        validators=[MinValueValidator(0.5), MaxValueValidator(2.0)],
        help_text="Vitesse de la synthèse vocale (0.5 à 2.0)"
    )
    
    # Choix de genre pour la synthèse vocale
    VOICE_GENDER_CHOICES = [
        ('male', 'Masculin'),
        ('female', 'Féminin'),
        ('auto', 'Automatique'),
    ]
    
    # Genres préférés par langue
    preferred_gender_french = models.CharField(
        max_length=10,
        choices=VOICE_GENDER_CHOICES,
        default='auto',
        help_text="Genre de voix préféré pour le français"
    )
    
    preferred_gender_english = models.CharField(
        max_length=10,
        choices=VOICE_GENDER_CHOICES,
        default='auto',
        help_text="Genre de voix préféré pour l'anglais"
    )
    
    preferred_gender_spanish = models.CharField(
        max_length=10,
        choices=VOICE_GENDER_CHOICES,
        default='auto',
        help_text="Genre de voix préféré pour l'espagnol"
    )
    
    preferred_gender_italian = models.CharField(
        max_length=10,
        choices=VOICE_GENDER_CHOICES,
        default='auto',
        help_text="Genre de voix préféré pour l'italien"
    )
    
    preferred_gender_german = models.CharField(
        max_length=10,
        choices=VOICE_GENDER_CHOICES,
        default='auto',
        help_text="Genre de voix préféré pour l'allemand"
    )
    
    keyboard_shortcuts_enabled = models.BooleanField(
        default=True,
        help_text="Activer les raccourcis clavier"
    )
    
    # Paramètres de statistiques de mots
    show_word_stats = models.BooleanField(
        default=True,
        help_text="Afficher les statistiques de mots"
    )
    
    stats_display_mode = models.CharField(
        max_length=20,
        choices=[
            ('detailed', 'Détaillé'),
            ('summary', 'Résumé'),
            ('minimal', 'Minimal'),
        ],
        default='detailed',
        help_text="Mode d'affichage des statistiques"
    )
    
    hide_learned_words = models.BooleanField(
        default=False,
        help_text="Masquer les mots déjà appris dans les statistiques"
    )
    
    group_by_deck = models.BooleanField(
        default=False,
        help_text="Grouper les statistiques par deck"
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
    
    def clean(self):
        """
        Validation des paramètres de révision
        """
        from django.core.exceptions import ValidationError
        
        # Vérifier que les intervalles de répétition espacée sont cohérents
        if self.spaced_repetition_enabled:
            if self.initial_interval_easy < self.initial_interval_normal:
                raise ValidationError(
                    "L'intervalle facile doit être supérieur ou égal à l'intervalle normal"
                )
            if self.initial_interval_normal < self.initial_interval_hard:
                raise ValidationError(
                    "L'intervalle normal doit être supérieur ou égal à l'intervalle difficile"
                )
        
        # Vérifier la cohérence des paramètres de session
        if self.cards_per_session > 100:
            raise ValidationError("Le nombre de cartes par session ne peut pas dépasser 100")
        
        # Vérifier la vitesse audio
        if not (0.5 <= self.audio_speed <= 2.0):
            raise ValidationError("La vitesse audio doit être entre 0.5 et 2.0")
    
    def save(self, *args, **kwargs):
        """
        Sauvegarde avec validation et logging
        """
        self.full_clean()  # Appelle clean() pour validation
        
        # Log les changements importants
        if self.pk:  # Mise à jour existante
            try:
                old_instance = RevisionSettings.objects.get(pk=self.pk)
                if old_instance.default_study_mode != self.default_study_mode:
                    logger.info(f"Study mode changed for user {self.user.username}: {old_instance.default_study_mode} -> {self.default_study_mode}")
                if old_instance.default_difficulty != self.default_difficulty:
                    logger.info(f"Difficulty changed for user {self.user.username}: {old_instance.default_difficulty} -> {self.default_difficulty}")
            except RevisionSettings.DoesNotExist:
                pass  # Première création
        else:
            logger.info(f"Creating new revision settings for user {self.user.username}")
        
        super().save(*args, **kwargs)
    
    def reset_to_defaults(self):
        """
        Remet tous les paramètres aux valeurs par défaut
        """
        logger.info(f"Resetting revision settings to defaults for user {self.user.username}")
        
        # Récupérer les valeurs par défaut du modèle
        for field in self._meta.fields:
            if hasattr(field, 'default') and field.default is not None and field.name != 'user':
                if callable(field.default):
                    setattr(self, field.name, field.default())
                else:
                    setattr(self, field.name, field.default)
        
        self.save()
        return self
    
    def get_audio_settings(self):
        """
        Retourne uniquement les paramètres audio
        """
        return {
            'audio_enabled': self.audio_enabled,
            'audio_speed': self.audio_speed,
            'auto_play_audio': self.auto_play_audio,
            'preferred_gender_french': self.preferred_gender_french,
            'preferred_gender_english': self.preferred_gender_english,
            'preferred_gender_spanish': self.preferred_gender_spanish,
            'preferred_gender_italian': self.preferred_gender_italian,
            'preferred_gender_german': self.preferred_gender_german,
        }
    
    def update_audio_settings(self, audio_data):
        """
        Met à jour uniquement les paramètres audio
        """
        audio_fields = [
            'audio_enabled', 'audio_speed', 'auto_play_audio',
            'preferred_gender_french', 'preferred_gender_english', 
            'preferred_gender_spanish', 'preferred_gender_italian', 'preferred_gender_german'
        ]
        
        updated_fields = []
        for field in audio_fields:
            if field in audio_data:
                old_value = getattr(self, field)
                new_value = audio_data[field]
                if old_value != new_value:
                    setattr(self, field, new_value)
                    updated_fields.append(field)
        
        if updated_fields:
            logger.info(f"Updated audio settings for user {self.user.username}: {updated_fields}")
            self.save(update_fields=updated_fields + ['updated_at'])
        
        return self


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
        default=20,
        validators=[MinValueValidator(5), MaxValueValidator(120)]
    )
    
    target_cards = models.PositiveIntegerField(
        default=20,
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
    
    def clean(self):
        """
        Validation des configurations de session
        """
        from django.core.exceptions import ValidationError
        
        # Vérifier qu'au moins un type de carte est inclus
        if not any([self.include_new_cards, self.include_review_cards, self.include_difficult_cards]):
            raise ValidationError("Au moins un type de carte doit être inclus dans la session")
        
        # Vérifier la cohérence durée/nombre de cartes
        if self.duration_minutes > 0 and self.target_cards > 0:
            time_per_card = self.duration_minutes / self.target_cards
            if time_per_card < 0.2:  # Moins de 12 secondes par carte
                raise ValidationError(
                    "Trop de cartes pour la durée prévue (minimum 12 secondes par carte)"
                )
            elif time_per_card > 5:  # Plus de 5 minutes par carte
                raise ValidationError(
                    "Pas assez de cartes pour la durée prévue (maximum 5 minutes par carte)"
                )
        
        # Vérifier l'unicité du nom par utilisateur
        if RevisionSessionConfig.objects.filter(
            user=self.user, 
            name=self.name
        ).exclude(pk=self.pk).exists():
            raise ValidationError("Une configuration avec ce nom existe déjà pour cet utilisateur")
    
    def save(self, *args, **kwargs):
        """
        Sauvegarde avec validation et gestion des configurations par défaut
        """
        self.full_clean()
        
        # Si c'est marqué comme défaut, retirer le défaut des autres configs
        if self.is_default:
            RevisionSessionConfig.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
            logger.info(f"Set {self.name} as default session config for user {self.user.username}")
        
        # Si c'est la première config de l'utilisateur, la marquer comme défaut
        if not self.pk and not RevisionSessionConfig.objects.filter(user=self.user).exists():
            self.is_default = True
            logger.info(f"Setting first session config {self.name} as default for user {self.user.username}")
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_default_for_user(cls, user):
        """
        Récupère la configuration par défaut pour un utilisateur
        """
        try:
            return cls.objects.get(user=user, is_default=True)
        except cls.DoesNotExist:
            # Si aucune config par défaut, prendre la première
            first_config = cls.objects.filter(user=user).first()
            if first_config:
                first_config.is_default = True
                first_config.save()
                return first_config
            return None
    
    def duplicate(self, new_name=None):
        """
        Duplique cette configuration avec un nouveau nom
        """
        if not new_name:
            new_name = f"{self.name} (copie)"
        
        # S'assurer que le nom est unique
        counter = 1
        original_new_name = new_name
        while RevisionSessionConfig.objects.filter(user=self.user, name=new_name).exists():
            new_name = f"{original_new_name} ({counter})"
            counter += 1
        
        new_config = RevisionSessionConfig.objects.create(
            user=self.user,
            name=new_name,
            session_type=self.session_type,
            duration_minutes=self.duration_minutes,
            target_cards=self.target_cards,
            include_new_cards=self.include_new_cards,
            include_review_cards=self.include_review_cards,
            include_difficult_cards=self.include_difficult_cards,
            tags_filter=self.tags_filter.copy() if self.tags_filter else [],
            difficulty_filter=self.difficulty_filter.copy() if self.difficulty_filter else [],
            is_default=False  # Les copies ne sont jamais par défaut
        )
        
        logger.info(f"Duplicated session config {self.name} -> {new_name} for user {self.user.username}")
        return new_config
    
    def get_estimated_time(self):
        """
        Calcule le temps estimé pour cette session
        """
        if self.target_cards == 0:
            return 0
        
        # Temps de base par carte selon le type de session
        base_time_per_card = {
            'quick': 0.35,      # 21 secondes par carte
            'standard': 0.5,    # 30 secondes par carte  
            'extended': 0.75,   # 45 secondes par carte
            'custom': 0.5       # 30 secondes par défaut
        }
        
        time_per_card = base_time_per_card.get(self.session_type, 0.5)
        estimated_minutes = self.target_cards * time_per_card
        
        return round(estimated_minutes, 1)
    
    def get_card_distribution(self):
        """
        Retourne la distribution prévue des types de cartes
        """
        total_types = sum([
            self.include_new_cards,
            self.include_review_cards, 
            self.include_difficult_cards
        ])
        
        if total_types == 0:
            return {}
        
        distribution = {}
        cards_per_type = self.target_cards // total_types
        remaining_cards = self.target_cards % total_types
        
        if self.include_new_cards:
            distribution['new_cards'] = cards_per_type + (1 if remaining_cards > 0 else 0)
            remaining_cards = max(0, remaining_cards - 1)
        
        if self.include_review_cards:
            distribution['review_cards'] = cards_per_type + (1 if remaining_cards > 0 else 0)
            remaining_cards = max(0, remaining_cards - 1)
        
        if self.include_difficult_cards:
            distribution['difficult_cards'] = cards_per_type + (1 if remaining_cards > 0 else 0)
        
        return distribution