"""
Serializers pour l'API Django REST Framework de l'application Language Learning
"""
from rest_framework import serializers
from ..models import *


class LanguageSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle Language"""
    class Meta:
        model = Language
        fields = ['id', 'code', 'name', 'native_name', 'is_active', 'flag_emoji']


class UserLearningProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil d'apprentissage utilisateur"""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserLearningProfile
        fields = [
            'id', 'user', 'native_language', 'target_language', 'language_level',
            'objectives', 'total_time_spent', 'streak_count', 'last_activity_date',
            'xp_points', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class CourseUnitSerializer(serializers.ModelSerializer):
    """Serializer pour les unités de cours"""
    language = LanguageSerializer(read_only=True)
    modules_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseUnit
        fields = [
            'id', 'language', 'unit_number', 'title', 'description',
            'icon', 'color', 'order', 'is_active', 'modules_count'
        ]

    def get_modules_count(self, obj):
        return obj.modules.count()


class CourseModuleSerializer(serializers.ModelSerializer):
    """Serializer pour les modules de cours"""
    unit = CourseUnitSerializer(read_only=True)
    module_type_display = serializers.CharField(source='get_module_type_display', read_only=True)

    class Meta:
        model = CourseModule
        fields = [
            'id', 'unit', 'module_number', 'title', 'description', 'module_type',
            'module_type_display', 'estimated_duration', 'xp_reward', 'order',
            'is_active', 'created_at'
        ]


class ModuleProgressSerializer(serializers.ModelSerializer):
    """Serializer pour la progression des modules"""
    user = serializers.StringRelatedField(read_only=True)
    module = CourseModuleSerializer(read_only=True)

    class Meta:
        model = ModuleProgress
        fields = [
            'id', 'user', 'module', 'is_completed', 'score', 'attempts',
            'time_spent', 'completed_at', 'started_at'
        ]
        read_only_fields = ['user', 'completed_at', 'started_at']


class UserCourseProgressSerializer(serializers.ModelSerializer):
    """Serializer pour la progression utilisateur dans un cours"""
    user = serializers.StringRelatedField(read_only=True)
    language = LanguageSerializer(read_only=True)
    current_unit = CourseUnitSerializer(read_only=True)
    completion_percentage = serializers.SerializerMethodField()

    class Meta:
        model = UserCourseProgress
        fields = [
            'id', 'user', 'language', 'current_unit', 'current_module',
            'total_xp', 'level', 'started_date', 'last_activity_date',
            'completion_percentage'
        ]
        read_only_fields = ['user', 'started_date']

    def get_completion_percentage(self, obj):
        return getattr(obj, 'get_completion_percentage', lambda: 0)()


class UserLanguageSerializer(serializers.ModelSerializer):
    """Serializer pour les langues d'un utilisateur"""
    user = serializers.StringRelatedField(read_only=True)
    language = LanguageSerializer(read_only=True)
    target_level_display = serializers.CharField(source='get_target_level_display', read_only=True)

    class Meta:
        model = UserLanguage
        fields = [
            'id', 'user', 'language', 'target_level', 'target_level_display',
            'current_level', 'streak_count', 'total_time_studied',
            'last_study_date', 'is_active', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']


# Serializers pour les vues d'interface utilisateur
class LearningInterfaceSerializer(serializers.Serializer):
    """Serializer pour l'interface d'apprentissage principale"""
    selected_language = serializers.CharField()
    selected_language_name = serializers.CharField()
    course_units = serializers.JSONField()
    active_unit = serializers.JSONField(required=False)
    active_unit_modules = serializers.JSONField(required=False)
    user_progress = UserCourseProgressSerializer(required=False)
    user_streak = serializers.IntegerField(default=0)
    view_type = serializers.CharField(default='home')


class ModuleStartSerializer(serializers.Serializer):
    """Serializer pour démarrer un module"""
    module_id = serializers.IntegerField()


class ModuleCompleteSerializer(serializers.Serializer):
    """Serializer pour compléter un module"""
    module_id = serializers.IntegerField()
    score = serializers.IntegerField(min_value=0, max_value=100, default=100)


class ProgressRefreshSerializer(serializers.Serializer):
    """Serializer pour rafraîchir les données de progression"""
    selected_language = serializers.CharField(default='EN')
    user_progress = serializers.JSONField()
    user_streak = serializers.IntegerField(default=0)