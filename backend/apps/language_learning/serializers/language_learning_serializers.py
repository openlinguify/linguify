"""
Serializers pour l'application Language Learning
"""
from rest_framework import serializers
from ..models import LanguagelearningItem, Language, UserLanguage
import logging

logger = logging.getLogger(__name__)


class LanguageSerializer(serializers.ModelSerializer):
    """
    Serializer pour les langues disponibles
    """
    is_learning = serializers.SerializerMethodField()
    progress_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Language
        fields = [
            'id', 'code', 'name', 'native_name', 'flag_emoji', 'is_active',
            'is_learning', 'progress_stats'
        ]
        read_only_fields = ['id']
    
    def get_is_learning(self, obj):
        """Détermine si l'utilisateur apprend cette langue"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserLanguage.objects.filter(
                user=request.user, 
                language=obj, 
                is_active=True
            ).exists()
        return False
    
    def get_progress_stats(self, obj):
        """Retourne les statistiques de progression pour cette langue"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_language = UserLanguage.objects.filter(
                user=request.user,
                language=obj,
                is_active=True
            ).first()
            
            if user_language:
                return {
                    'proficiency_level': user_language.proficiency_level,
                    'progress_percentage': user_language.progress_percentage,
                    'streak_count': user_language.streak_count,
                    'total_time_spent': user_language.total_time_spent,
                    'lessons_completed': user_language.lessons_completed,
                    'daily_goal': user_language.daily_goal
                }
        return None


class UserLanguageSerializer(serializers.ModelSerializer):
    """
    Serializer pour les langues que l'utilisateur apprend
    """
    language = LanguageSerializer(read_only=True)
    language_code = serializers.CharField(write_only=True)
    proficiency_level_display = serializers.CharField(source='get_proficiency_level_display', read_only=True)
    target_level_display = serializers.CharField(source='get_target_level_display', read_only=True)
    time_display = serializers.SerializerMethodField()
    daily_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = UserLanguage
        fields = [
            'id', 'language', 'language_code', 'proficiency_level', 'proficiency_level_display',
            'target_level', 'target_level_display', 'daily_goal', 'progress_percentage',
            'streak_count', 'total_time_spent', 'time_display', 'lessons_completed',
            'is_active', 'last_activity', 'started_at', 'daily_progress'
        ]
        read_only_fields = ['id', 'user', 'started_at', 'last_activity']
    
    def get_time_display(self, obj):
        """Formate le temps d'étude de manière lisible"""
        total_minutes = obj.total_time_spent or 0
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes:02d}m"
        else:
            return f"{minutes}m"
    
    def get_daily_progress(self, obj):
        """Calcule le progrès quotidien de l'utilisateur"""
        from django.utils import timezone
        today = timezone.now().date()
        
        # Pour l'instant, retourner des données simulées
        # TODO: Implémenter le calcul basé sur les sessions d'apprentissage réelles
        return {
            'goal': obj.daily_goal,
            'completed': min(obj.daily_goal, obj.streak_count),  # Simulation
            'percentage': min(100, (obj.streak_count / obj.daily_goal * 100)) if obj.daily_goal > 0 else 0
        }
    
    def validate_language_code(self, value):
        """Valide que le code de langue existe"""
        try:
            Language.objects.get(code=value, is_active=True)
            return value
        except Language.DoesNotExist:
            raise serializers.ValidationError(f"Langue avec le code '{value}' non trouvée ou inactive")
    
    def validate_daily_goal(self, value):
        """Valide l'objectif quotidien"""
        if value < 1:
            raise serializers.ValidationError("L'objectif quotidien doit être d'au moins 1 minute")
        if value > 300:  # 5 heures max
            raise serializers.ValidationError("L'objectif quotidien ne peut pas dépasser 300 minutes")
        return value
    
    def create(self, validated_data):
        """Crée une nouvelle association utilisateur-langue"""
        language_code = validated_data.pop('language_code')
        language = Language.objects.get(code=language_code, is_active=True)
        
        user_language = UserLanguage.objects.create(
            user=self.context['request'].user,
            language=language,
            **validated_data
        )
        
        logger.info(f"User {user_language.user.username} started learning {language.name}")
        return user_language


class LanguagelearningItemSerializer(serializers.ModelSerializer):
    """
    Serializer pour les éléments d'apprentissage des langues
    """
    language = LanguageSerializer(read_only=True)
    language_code = serializers.CharField(write_only=True, required=False)
    user_progress = serializers.SerializerMethodField()
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    
    class Meta:
        model = LanguagelearningItem
        fields = [
            'id', 'title', 'description', 'content', 'difficulty', 'difficulty_display',
            'item_type', 'language', 'language_code', 'estimated_duration', 'order_index',
            'is_active', 'created_at', 'updated_at', 'user_progress'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_user_progress(self, obj):
        """Retourne le progrès de l'utilisateur pour cet élément"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # TODO: Implémenter le système de progression par élément
            return {
                'completed': False,
                'completion_date': None,
                'score': None,
                'attempts': 0
            }
        return None
    
    def validate_language_code(self, value):
        """Valide le code de langue si fourni"""
        if value:
            try:
                Language.objects.get(code=value, is_active=True)
                return value
            except Language.DoesNotExist:
                raise serializers.ValidationError(f"Langue avec le code '{value}' non trouvée")
        return value
    
    def validate_estimated_duration(self, value):
        """Valide la durée estimée"""
        if value < 1:
            raise serializers.ValidationError("La durée estimée doit être d'au moins 1 minute")
        if value > 180:  # 3 heures max
            raise serializers.ValidationError("La durée estimée ne peut pas dépasser 180 minutes")
        return value
    
    def create(self, validated_data):
        """Crée un nouvel élément d'apprentissage"""
        language_code = validated_data.pop('language_code', None)
        
        if language_code:
            language = Language.objects.get(code=language_code, is_active=True)
            validated_data['language'] = language
        
        validated_data['user'] = self.context['request'].user
        
        item = LanguagelearningItem.objects.create(**validated_data)
        logger.info(f"Created learning item '{item.title}' for user {item.user.username}")
        
        return item


class StartLanguageLearningSerializer(serializers.Serializer):
    """
    Serializer pour démarrer l'apprentissage d'une langue
    """
    language_code = serializers.CharField()
    proficiency_level = serializers.ChoiceField(
        choices=['beginner', 'intermediate', 'advanced'],
        default='beginner'
    )
    target_level = serializers.ChoiceField(
        choices=['intermediate', 'advanced', 'native'],
        default='intermediate'
    )
    daily_goal = serializers.IntegerField(default=15, min_value=1, max_value=300)
    
    def validate_language_code(self, value):
        """Valide que la langue existe et est active"""
        try:
            Language.objects.get(code=value, is_active=True)
            return value
        except Language.DoesNotExist:
            raise serializers.ValidationError(f"Langue '{value}' non disponible")
    
    def validate(self, data):
        """Validation globale"""
        # Vérifier que target_level > proficiency_level
        levels = ['beginner', 'intermediate', 'advanced', 'native']
        current_idx = levels.index(data['proficiency_level'])
        target_idx = levels.index(data['target_level'])
        
        if target_idx <= current_idx:
            raise serializers.ValidationError(
                "Le niveau cible doit être supérieur au niveau actuel"
            )
        
        return data
    
    def create(self, validated_data):
        """Crée ou met à jour l'apprentissage de la langue"""
        user = self.context['request'].user
        language = Language.objects.get(code=validated_data['language_code'], is_active=True)
        
        user_language, created = UserLanguage.objects.get_or_create(
            user=user,
            language=language,
            defaults=validated_data
        )
        
        if not created:
            # Mettre à jour et réactiver si nécessaire
            for field, value in validated_data.items():
                if field != 'language_code':
                    setattr(user_language, field, value)
            user_language.is_active = True
            user_language.save()
        
        return user_language


class LanguageLearningStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques d'apprentissage des langues
    """
    total_languages = serializers.IntegerField(read_only=True)
    active_languages = serializers.IntegerField(read_only=True)
    total_study_time = serializers.IntegerField(read_only=True)  # en minutes
    longest_streak = serializers.IntegerField(read_only=True)
    total_lessons_completed = serializers.IntegerField(read_only=True)
    average_daily_time = serializers.FloatField(read_only=True)
    
    # Statistiques par langue
    languages_progress = serializers.ListField(read_only=True)
    recent_activity = serializers.ListField(read_only=True)
    
    # Objectifs
    daily_goal_completion_rate = serializers.FloatField(read_only=True)
    weekly_progress = serializers.DictField(read_only=True)