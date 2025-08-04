"""
Serializers pour les paramètres de l'application Révision
"""
from rest_framework import serializers
from ..models.settings_models import RevisionSettings, RevisionSessionConfig
import logging

logger = logging.getLogger(__name__)

class RevisionSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer pour les paramètres généraux de révision
    """
    
    # Champs calculés pour l'interface
    preset_options = serializers.SerializerMethodField()
    current_preset = serializers.SerializerMethodField()
    
    class Meta:
        model = RevisionSettings
        fields = [
            # Identifiants
            'id', 'user',
            
            # Paramètres généraux
            'default_study_mode', 'default_difficulty',
            'default_session_duration', 'cards_per_session', 'auto_advance',
            
            # Répétition espacée
            'spaced_repetition_enabled', 'initial_interval_easy',
            'initial_interval_normal', 'initial_interval_hard',
            
            # Performance
            'required_reviews_to_learn', 'reset_on_wrong_answer', 'show_progress_stats',
            
            # Notifications
            'daily_reminder_enabled', 'reminder_time', 'notification_frequency',
            
            # Interface
            'enable_animations', 'auto_play_audio', 'keyboard_shortcuts_enabled',
            
            # Statistiques de mots
            'show_word_stats', 'stats_display_mode', 'hide_learned_words', 'group_by_deck',
            
            # Métadonnées
            'created_at', 'updated_at',
            
            # Champs calculés
            'preset_options', 'current_preset'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_preset_options(self, obj):
        """Retourne les options de presets disponibles"""
        return [
            {
                'value': 'beginner',
                'label': 'Débutant',
                'description': 'Configuration facile pour commencer',
                'icon': 'bi-star',
                'settings': {
                    'default_difficulty': 'easy',
                    'cards_per_session': 10,
                    'default_session_duration': 15,
                    'required_reviews_to_learn': 2,
                }
            },
            {
                'value': 'intermediate',
                'label': 'Intermédiaire',
                'description': 'Configuration équilibrée',
                'icon': 'bi-lightning',
                'settings': {
                    'default_difficulty': 'normal',
                    'cards_per_session': 20,
                    'default_session_duration': 20,
                    'required_reviews_to_learn': 3,
                }
            },
            {
                'value': 'advanced',
                'label': 'Avancé',
                'description': 'Configuration intensive',
                'icon': 'bi-fire',
                'settings': {
                    'default_difficulty': 'hard',
                    'cards_per_session': 30,
                    'default_session_duration': 30,
                    'required_reviews_to_learn': 4,
                }
            },
            {
                'value': 'intensive',
                'label': 'Intensif',
                'description': 'Maximum de révision',
                'icon': 'bi-rocket',
                'settings': {
                    'default_study_mode': 'intensive',
                    'cards_per_session': 50,
                    'default_session_duration': 45,
                    'spaced_repetition_enabled': False,
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
                current_value = getattr(obj, field, None)
                if current_value != expected_value:
                    match = False
                    break
            
            if match:
                return preset['value']
        
        return 'custom'
    
    def validate_cards_per_session(self, value):
        """Validation pour le nombre de cartes par session"""
        if value < 5:
            raise serializers.ValidationError("Minimum 5 cartes par session")
        if value > 100:
            raise serializers.ValidationError("Maximum 100 cartes par session")
        return value
    
    def validate_default_session_duration(self, value):
        """Validation pour la durée de session"""
        if value < 5:
            raise serializers.ValidationError("Durée minimum 5 minutes")
        if value > 120:
            raise serializers.ValidationError("Durée maximum 120 minutes")
        return value
    
    def update(self, instance, validated_data):
        """Mise à jour avec logging"""
        old_values = {
            'study_mode': instance.default_study_mode,
            'difficulty': instance.default_difficulty,
            'cards_per_session': instance.cards_per_session,
        }
        
        updated_instance = super().update(instance, validated_data)
        
        logger.info(f"Revision settings updated for user {instance.user.username}")
        logger.debug(f"Old values: {old_values}")
        logger.debug(f"New values: {validated_data}")
        
        return updated_instance


class RevisionSessionConfigSerializer(serializers.ModelSerializer):
    """
    Serializer pour les configurations de session
    """
    
    # Champs calculés
    estimated_completion_time = serializers.SerializerMethodField()
    difficulty_distribution = serializers.SerializerMethodField()
    
    class Meta:
        model = RevisionSessionConfig
        fields = [
            'id', 'user', 'name', 'session_type',
            'duration_minutes', 'target_cards',
            'include_new_cards', 'include_review_cards', 'include_difficult_cards',
            'tags_filter', 'difficulty_filter', 'is_default',
            'created_at', 'updated_at',
            'estimated_completion_time', 'difficulty_distribution'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_estimated_completion_time(self, obj):
        """Calcule le temps estimé pour terminer cette configuration"""
        # Estimation basée sur 30 secondes par carte en moyenne
        base_time_per_card = 0.5  # minutes
        
        if obj.session_type == 'quick':
            time_per_card = base_time_per_card * 0.7
        elif obj.session_type == 'extended':
            time_per_card = base_time_per_card * 1.3
        else:
            time_per_card = base_time_per_card
        
        estimated_time = obj.target_cards * time_per_card
        return round(estimated_time, 1)
    
    def get_difficulty_distribution(self, obj):
        """Retourne la distribution prévue des difficultés"""
        if obj.difficulty_filter:
            return {level: 100//len(obj.difficulty_filter) for level in obj.difficulty_filter}
        
        # Distribution par défaut
        return {
            'easy': 30,
            'normal': 50,
            'hard': 20
        }
    
    def validate_name(self, value):
        """Valide que le nom de configuration est unique pour l'utilisateur"""
        user = self.context['request'].user
        existing = RevisionSessionConfig.objects.filter(
            user=user, 
            name=value
        ).exclude(pk=self.instance.pk if self.instance else None)
        
        if existing.exists():
            raise serializers.ValidationError("Une configuration avec ce nom existe déjà")
        
        return value
    
    def validate(self, data):
        """Validation globale"""
        # Vérifier qu'au moins un type de carte est inclus
        card_types = ['include_new_cards', 'include_review_cards', 'include_difficult_cards']
        if not any(data.get(card_type, False) for card_type in card_types):
            raise serializers.ValidationError(
                "Au moins un type de carte doit être inclus dans la session"
            )
        
        # Vérifier la cohérence durée/nombre de cartes
        duration = data.get('duration_minutes', 0)
        target_cards = data.get('target_cards', 0)
        
        if duration > 0 and target_cards > 0:
            time_per_card = duration / target_cards
            if time_per_card < 0.2:  # Moins de 12 secondes par carte
                raise serializers.ValidationError(
                    "Trop de cartes pour la durée prévue (minimum 12 secondes par carte)"
                )
            elif time_per_card > 5:  # Plus de 5 minutes par carte
                raise serializers.ValidationError(
                    "Pas assez de cartes pour la durée prévue (maximum 5 minutes par carte)"
                )
        
        return data


class ApplyPresetSerializer(serializers.Serializer):
    """
    Serializer pour appliquer un preset de configuration
    """
    preset_name = serializers.ChoiceField(
        choices=['beginner', 'intermediate', 'advanced', 'intensive'],
        help_text="Nom du preset à appliquer"
    )
    
    override_user_settings = serializers.BooleanField(
        default=True,
        help_text="Écraser les paramètres existants de l'utilisateur"
    )
    
    def validate_preset_name(self, value):
        """Valide que le preset existe"""
        valid_presets = ['beginner', 'intermediate', 'advanced', 'intensive']
        if value not in valid_presets:
            raise serializers.ValidationError(f"Preset invalide. Choix: {valid_presets}")
        return value


class RevisionStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques de révision
    """
    total_cards = serializers.IntegerField(read_only=True)
    cards_learned = serializers.IntegerField(read_only=True)
    cards_in_progress = serializers.IntegerField(read_only=True)
    daily_streak = serializers.IntegerField(read_only=True)
    total_study_time = serializers.IntegerField(read_only=True)  # en minutes
    average_session_duration = serializers.FloatField(read_only=True)
    success_rate = serializers.FloatField(read_only=True)
    last_study_date = serializers.DateTimeField(read_only=True)
    
    # Statistiques détaillées
    cards_by_difficulty = serializers.DictField(read_only=True)
    performance_trend = serializers.ListField(read_only=True)
    upcoming_reviews = serializers.IntegerField(read_only=True)