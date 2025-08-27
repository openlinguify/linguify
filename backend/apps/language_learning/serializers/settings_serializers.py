"""
Serializers pour les paramètres de l'application Language Learning
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class LanguageLearningSettingsSerializer(serializers.Serializer):
    """
    Serializer pour les paramètres généraux d'apprentissage des langues
    """
    
    # Paramètres généraux d'apprentissage
    preferred_study_time = serializers.TimeField(default='18:00')
    daily_goal_minutes = serializers.IntegerField(default=15, min_value=5, max_value=300)
    weekly_goal_days = serializers.IntegerField(default=5, min_value=1, max_value=7)
    
    # Notifications et rappels
    reminder_enabled = serializers.BooleanField(default=True)
    reminder_frequency = serializers.ChoiceField(
        choices=['daily', 'weekdays', 'custom'],
        default='daily'
    )
    streak_notifications = serializers.BooleanField(default=True)
    achievement_notifications = serializers.BooleanField(default=True)
    
    # Paramètres de difficulté
    auto_difficulty_adjustment = serializers.BooleanField(default=True)
    preferred_difficulty = serializers.ChoiceField(
        choices=['easy', 'normal', 'hard', 'adaptive'],
        default='adaptive'
    )
    
    # Interface et expérience utilisateur
    show_pronunciation_hints = serializers.BooleanField(default=True)
    enable_audio_playback = serializers.BooleanField(default=True)
    audio_playback_speed = serializers.FloatField(default=1.0, min_value=0.5, max_value=2.0)
    show_progress_animations = serializers.BooleanField(default=True)
    
    # Méthodes d'apprentissage préférées
    learning_methods = serializers.MultipleChoiceField(
        choices=[
            ('flashcards', 'Cartes mémoire'),
            ('listening', 'Écoute'),
            ('speaking', 'Expression orale'),
            ('reading', 'Lecture'),
            ('writing', 'Écriture'),
            ('grammar', 'Grammaire'),
            ('vocabulary', 'Vocabulaire')
        ],
        default=['flashcards', 'vocabulary', 'listening']
    )
    
    # Paramètres de langue cible
    target_language = serializers.CharField(max_length=10, required=False)
    interface_language = serializers.CharField(max_length=10, required=False)
    
    # Champs calculés pour l'interface
    preset_options = serializers.SerializerMethodField()
    current_preset = serializers.SerializerMethodField()
    
    def get_preset_options(self, obj):
        """Retourne les options de presets disponibles pour l'apprentissage des langues"""
        return [
            {
                'value': 'casual',
                'label': 'Apprentissage décontracté',
                'description': 'Pour apprendre à votre rythme, sans pression',
                'icon': 'bi-clock',
                'settings': {
                    'daily_goal_minutes': 10,
                    'weekly_goal_days': 3,
                    'preferred_difficulty': 'easy',
                    'auto_difficulty_adjustment': True,
                    'reminder_frequency': 'custom'
                }
            },
            {
                'value': 'regular',
                'label': 'Apprentissage régulier',
                'description': 'Progression constante et équilibrée',
                'icon': 'bi-calendar-check',
                'settings': {
                    'daily_goal_minutes': 15,
                    'weekly_goal_days': 5,
                    'preferred_difficulty': 'normal',
                    'auto_difficulty_adjustment': True,
                    'reminder_frequency': 'weekdays'
                }
            },
            {
                'value': 'intensive',
                'label': 'Apprentissage intensif',
                'description': 'Pour progresser rapidement',
                'icon': 'bi-lightning-fill',
                'settings': {
                    'daily_goal_minutes': 30,
                    'weekly_goal_days': 6,
                    'preferred_difficulty': 'hard',
                    'auto_difficulty_adjustment': False,
                    'reminder_frequency': 'daily'
                }
            },
            {
                'value': 'immersion',
                'label': 'Immersion totale',
                'description': 'Apprentissage maximum pour résultats rapides',
                'icon': 'bi-rocket-takeoff',
                'settings': {
                    'daily_goal_minutes': 60,
                    'weekly_goal_days': 7,
                    'preferred_difficulty': 'hard',
                    'auto_difficulty_adjustment': False,
                    'reminder_frequency': 'daily',
                    'learning_methods': ['flashcards', 'listening', 'speaking', 'reading', 'writing']
                }
            }
        ]
    
    def get_current_preset(self, obj):
        """Détermine le preset actuel basé sur les paramètres"""
        presets = self.get_preset_options(obj)
        
        for preset in presets:
            preset_settings = preset['settings']
            match = True
            
            for field, expected_value in preset_settings.items():
                current_value = obj.get(field) if isinstance(obj, dict) else getattr(obj, field, None)
                if current_value != expected_value:
                    match = False
                    break
            
            if match:
                return preset['value']
        
        return 'custom'
    
    def validate_daily_goal_minutes(self, value):
        """Validation pour l'objectif quotidien"""
        if value < 5:
            raise serializers.ValidationError("L'objectif quotidien minimum est de 5 minutes")
        if value > 300:
            raise serializers.ValidationError("L'objectif quotidien maximum est de 300 minutes (5 heures)")
        return value
    
    def validate_audio_playback_speed(self, value):
        """Validation pour la vitesse de lecture audio"""
        if not (0.5 <= value <= 2.0):
            raise serializers.ValidationError("La vitesse de lecture doit être entre 0.5 et 2.0")
        return value
    
    def validate(self, data):
        """Validation globale des paramètres"""
        # Vérifier la cohérence entre les objectifs
        daily_goal = data.get('daily_goal_minutes', 15)
        weekly_days = data.get('weekly_goal_days', 5)
        
        weekly_total = daily_goal * weekly_days
        if weekly_total > 1200:  # Plus de 20 heures par semaine
            raise serializers.ValidationError(
                "L'objectif hebdomadaire total ne peut pas dépasser 20 heures"
            )
        
        return data


class ApplyLanguageLearningPresetSerializer(serializers.Serializer):
    """
    Serializer pour appliquer un preset de configuration d'apprentissage des langues
    """
    preset_name = serializers.ChoiceField(
        choices=['casual', 'regular', 'intensive', 'immersion'],
        help_text="Nom du preset à appliquer"
    )
    
    override_user_settings = serializers.BooleanField(
        default=True,
        help_text="Écraser les paramètres existants de l'utilisateur"
    )
    
    def validate_preset_name(self, value):
        """Valide que le preset existe"""
        valid_presets = ['casual', 'regular', 'intensive', 'immersion']
        if value not in valid_presets:
            raise serializers.ValidationError(f"Preset invalide. Choix: {valid_presets}")
        return value


class LanguageLearningSessionConfigSerializer(serializers.Serializer):
    """
    Serializer pour les configurations de session d'apprentissage
    """
    name = serializers.CharField(max_length=100)
    session_type = serializers.ChoiceField(
        choices=['quick', 'standard', 'extended', 'custom'],
        default='standard'
    )
    duration_minutes = serializers.IntegerField(min_value=5, max_value=120)
    
    # Types d'exercices inclus
    include_vocabulary = serializers.BooleanField(default=True)
    include_grammar = serializers.BooleanField(default=True)
    include_listening = serializers.BooleanField(default=True)
    include_speaking = serializers.BooleanField(default=False)
    include_reading = serializers.BooleanField(default=True)
    include_writing = serializers.BooleanField(default=False)
    
    # Paramètres de difficulté
    difficulty_level = serializers.ChoiceField(
        choices=['easy', 'normal', 'hard', 'mixed'],
        default='mixed'
    )
    adaptive_difficulty = serializers.BooleanField(default=True)
    
    # Filtres
    focus_areas = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Domaines spécifiques sur lesquels se concentrer"
    )
    
    is_default = serializers.BooleanField(default=False)
    
    # Champs calculés
    estimated_exercises = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    
    def get_estimated_exercises(self, obj):
        """Calcule le nombre estimé d'exercices pour cette configuration"""
        base_exercises_per_minute = 2
        duration = obj.get('duration_minutes', 20) if isinstance(obj, dict) else getattr(obj, 'duration_minutes', 20)
        return duration * base_exercises_per_minute
    
    def get_completion_rate(self, obj):
        """Calcule le taux de completion moyen pour cette configuration"""
        # TODO: Calculer basé sur l'historique réel des sessions
        return 85.0  # Placeholder
    
    def validate(self, data):
        """Validation globale"""
        # Vérifier qu'au moins un type d'exercice est inclus
        exercise_types = [
            'include_vocabulary', 'include_grammar', 'include_listening',
            'include_speaking', 'include_reading', 'include_writing'
        ]
        
        if not any(data.get(exercise_type, False) for exercise_type in exercise_types):
            raise serializers.ValidationError(
                "Au moins un type d'exercice doit être inclus dans la session"
            )
        
        return data


class UserLanguagePreferencesSerializer(serializers.Serializer):
    """
    Serializer pour les préférences spécifiques par langue de l'utilisateur
    """
    language_code = serializers.CharField(max_length=10)
    
    # Préférences audio
    audio_enabled = serializers.BooleanField(default=True)
    preferred_voice_gender = serializers.ChoiceField(
        choices=['male', 'female', 'auto'],
        default='auto'
    )
    audio_speed = serializers.FloatField(default=1.0, min_value=0.5, max_value=2.0)
    
    # Préférences visuelles
    show_romanization = serializers.BooleanField(default=True)
    font_size = serializers.ChoiceField(
        choices=['small', 'medium', 'large'],
        default='medium'
    )
    
    # Préférences d'apprentissage
    focus_skills = serializers.MultipleChoiceField(
        choices=[
            ('speaking', 'Expression orale'),
            ('listening', 'Compréhension orale'),
            ('reading', 'Lecture'),
            ('writing', 'Écriture'),
            ('pronunciation', 'Prononciation'),
            ('grammar', 'Grammaire'),
            ('vocabulary', 'Vocabulaire')
        ],
        default=['vocabulary', 'grammar']
    )
    
    # Paramètres de révision
    review_frequency = serializers.ChoiceField(
        choices=['low', 'medium', 'high'],
        default='medium'
    )
    mistake_emphasis = serializers.BooleanField(default=True)
    
    def validate_language_code(self, value):
        """Valide que le code de langue est valide"""
        # Liste des codes de langues supportés
        supported_languages = [
            'en', 'fr', 'es', 'de', 'it', 'pt', 'nl', 'ja', 'ko', 'zh', 'ar', 'ru'
        ]
        
        if value not in supported_languages:
            raise serializers.ValidationError(
                f"Code de langue '{value}' non supporté. Langues disponibles: {supported_languages}"
            )
        
        return value