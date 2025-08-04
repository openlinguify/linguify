from django.contrib import admin
from .models.core import Unit, Chapter, Lesson, ContentLesson
from .models.progress import UserProgress, UnitProgress, ChapterProgress, LessonProgress


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'teacher_id', 'is_published', 'created_at')
    list_filter = ('level', 'is_published', 'created_at')
    search_fields = ('title_fr', 'title_en', 'title_es', 'title_nl')
    ordering = ('level', 'order')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('teacher_id', 'teacher_name', 'level', 'order', 'is_published', 'is_free', 'price')
        }),
        ('Titres', {
            'fields': ('title_fr', 'title_en', 'title_es', 'title_nl')
        }),
        ('Descriptions', {
            'fields': ('description_fr', 'description_en', 'description_es', 'description_nl'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit', 'theme', 'order', 'points_reward')
    list_filter = ('unit__level', 'theme', 'style')
    search_fields = ('title_fr', 'title_en', 'unit__title_fr', 'unit__title_en')
    ordering = ('unit', 'order')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('unit', 'theme', 'order', 'style', 'points_reward')
        }),
        ('Titres', {
            'fields': ('title_fr', 'title_en', 'title_es', 'title_nl')
        }),
        ('Descriptions', {
            'fields': ('description_fr', 'description_en', 'description_es', 'description_nl'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit', 'chapter', 'lesson_type', 'estimated_duration', 'created_at')
    list_filter = ('unit__level', 'lesson_type', 'created_at')
    search_fields = ('title_fr', 'title_en', 'unit__title_fr', 'chapter__title_fr')
    ordering = ('unit', 'chapter', 'order')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('unit', 'chapter', 'lesson_type', 'estimated_duration', 'order')
        }),
        ('Titres', {
            'fields': ('title_fr', 'title_en', 'title_es', 'title_nl')
        }),
        ('Descriptions', {
            'fields': ('description_fr', 'description_en', 'description_es', 'description_nl'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContentLesson)
class ContentLessonAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'content_type', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('lesson__title_fr', 'lesson__title_en')


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_level', 'total_xp', 'streak_days', 'last_activity_date')
    list_filter = ('current_level', 'last_activity_date')
    search_fields = ('user__username', 'user__email')
    ordering = ('-last_activity_date',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UnitProgress)
class UnitProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'unit', 'progress_percentage', 'status', 'started_at')
    list_filter = ('status', 'unit__level', 'started_at')
    search_fields = ('user__username', 'user__email', 'unit__title_fr')
    ordering = ('-started_at',)
    readonly_fields = ('started_at', 'completed_at', 'lessons_completed')


@admin.register(ChapterProgress)
class ChapterProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'chapter', 'progress_percentage', 'is_completed')
    list_filter = ('is_completed', 'chapter__unit__level')
    search_fields = ('user__username', 'chapter__title_fr')
    ordering = ('-started_at',)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'status', 'progress_percentage', 'last_accessed')
    list_filter = ('status', 'lesson__lesson_type', 'lesson__unit__level')
    search_fields = ('user__username', 'lesson__title_fr')
    ordering = ('-last_accessed',)
    readonly_fields = ('started_at', 'completed_at')