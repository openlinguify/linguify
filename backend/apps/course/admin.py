from django.contrib import admin
from .models.core import Unit, Chapter, Lesson, ContentLesson
from .models.progress import UserProgress, ChapterProgress, LessonProgress


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'teacher_cms_id', 'is_published', 'created_at')
    list_filter = ('level', 'is_published', 'created_at')
    search_fields = ('title_fr', 'title_en', 'title_es', 'title_nl')
    ordering = ('level', 'order')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('teacher_cms_id', 'level', 'order', 'is_published')
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
    list_display = ('title', 'unit', 'chapter', 'lesson_type', 'estimated_duration', 'is_published')
    list_filter = ('unit__level', 'lesson_type', 'is_published', 'created_at')
    search_fields = ('title_fr', 'title_en', 'unit__title_fr', 'chapter__title_fr')
    ordering = ('unit', 'chapter', 'order')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('unit', 'chapter', 'lesson_type', 'estimated_duration', 'order', 'is_published')
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
    list_display = ('user', 'unit', 'progress_percentage', 'is_completed', 'last_activity')
    list_filter = ('is_completed', 'unit__level', 'last_activity')
    search_fields = ('user__username', 'user__email', 'unit__title_fr')
    ordering = ('-last_activity',)
    readonly_fields = ('enrollment_date', 'completion_date', 'lessons_completed')


@admin.register(ChapterProgress)
class ChapterProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'chapter', 'progress_percentage', 'is_completed')
    list_filter = ('is_completed', 'chapter__unit__level')
    search_fields = ('user__username', 'chapter__title_fr')
    ordering = ('-started_at',)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'is_completed', 'time_spent', 'last_accessed')
    list_filter = ('completed_at', 'lesson__lesson_type', 'lesson__unit__level')
    search_fields = ('user__username', 'lesson__title_fr')
    ordering = ('-last_accessed',)
    readonly_fields = ('started_at', 'completed_at')