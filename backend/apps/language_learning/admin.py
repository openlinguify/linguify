from django.contrib import admin
from .models import (
    LanguagelearningItem, 
    Language, 
    UserLanguage, 
    Lesson, 
    UserLessonProgress, 
    LanguageLearningSettings
)


@admin.register(LanguagelearningItem)
class LanguagelearningItemAdmin(admin.ModelAdmin):
    """Administration des items Language Learning"""
    
    list_display = ['title', 'user', 'item_type', 'difficulty', 'language', 'is_active', 'created_at']
    list_filter = ['is_active', 'item_type', 'difficulty', 'language', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'description', 'item_type', 'difficulty', 'language', 'is_active')
        }),
        ('Détails', {
            'fields': ('content', 'estimated_duration', 'order_index'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'language')


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """Administration des langues"""
    
    list_display = ['name', 'code', 'native_name', 'flag_emoji', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'native_name', 'code']
    ordering = ['name']
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'native_name', 'flag_emoji', 'is_active')
        }),
    )


@admin.register(UserLanguage)
class UserLanguageAdmin(admin.ModelAdmin):
    """Administration des langues utilisateur"""
    
    list_display = ['user', 'language', 'proficiency_level', 'target_level', 'progress_percentage', 'is_active']
    list_filter = ['proficiency_level', 'target_level', 'is_active', 'started_at']
    search_fields = ['user__username', 'language__name']
    readonly_fields = ['started_at', 'last_activity']
    date_hierarchy = 'started_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'language', 'proficiency_level', 'target_level', 'is_active')
        }),
        ('Objectifs', {
            'fields': ('daily_goal', 'progress_percentage')
        }),
        ('Statistiques', {
            'fields': ('streak_count', 'total_time_spent', 'lessons_completed'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('started_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'language')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Administration des leçons"""
    
    list_display = ['title', 'language', 'level', 'order', 'estimated_duration', 'is_published']
    list_filter = ['language', 'level', 'is_published', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['language', 'level', 'order']
    
    fieldsets = (
        (None, {
            'fields': ('language', 'title', 'description', 'level', 'order', 'is_published')
        }),
        ('Contenu', {
            'fields': ('content', 'estimated_duration'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('language')


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    """Administration du progrès des leçons"""
    
    list_display = ['user', 'lesson', 'is_completed', 'score', 'time_spent', 'attempts', 'updated_at']
    list_filter = ['is_completed', 'lesson__language', 'completed_at', 'updated_at']
    search_fields = ['user__username', 'lesson__title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'updated_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'lesson', 'is_completed', 'score', 'attempts')
        }),
        ('Statistiques', {
            'fields': ('time_spent', 'completed_at')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'lesson', 'lesson__language')


@admin.register(LanguageLearningSettings)
class LanguageLearningSettingsAdmin(admin.ModelAdmin):
    """Administration des paramètres d'apprentissage des langues"""
    
    list_display = ['user', 'daily_goal_minutes', 'preferred_difficulty', 'reminder_enabled', 'updated_at']
    list_filter = ['preferred_difficulty', 'reminder_enabled', 'auto_difficulty_adjustment', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Objectifs', {
            'fields': ('daily_goal_minutes', 'weekly_goal_days', 'preferred_study_time')
        }),
        ('Notifications', {
            'fields': ('reminder_enabled', 'reminder_frequency', 'streak_notifications', 'achievement_notifications'),
            'classes': ('collapse',)
        }),
        ('Difficulté', {
            'fields': ('preferred_difficulty', 'auto_difficulty_adjustment'),
            'classes': ('collapse',)
        }),
        ('Interface', {
            'fields': ('show_pronunciation_hints', 'enable_audio_playback', 'audio_playback_speed', 'show_progress_animations', 'font_size'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
