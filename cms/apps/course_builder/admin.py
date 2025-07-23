from django.contrib import admin
from .models import (CMSUnit, CMSChapter, CMSLesson, CMSContentLesson, 
                     CMSVocabularyList, CMSVocabularyWord, CMSTheoryContent)

@admin.register(CMSUnit)
class CMSUnitAdmin(admin.ModelAdmin):
    list_display = ['title_fr', 'teacher', 'level', 'order', 'is_published', 'sync_status', 'price']
    list_filter = ['level', 'is_published', 'sync_status', 'teacher']
    search_fields = ['title_en', 'title_fr', 'teacher__user__username']
    readonly_fields = ['backend_id', 'last_sync']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('teacher', 'level', 'order', 'is_published', 'price')
        }),
        ('Titles', {
            'fields': ('title_en', 'title_fr', 'title_es', 'title_nl')
        }),
        ('Descriptions', {
            'fields': ('description_en', 'description_fr', 'description_es', 'description_nl'),
            'classes': ('collapse',)
        }),
        ('Sync', {
            'fields': ('sync_status', 'backend_id', 'last_sync', 'sync_error'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CMSChapter)
class CMSChapterAdmin(admin.ModelAdmin):
    list_display = ['title_fr', 'unit', 'order', 'style', 'sync_status']
    list_filter = ['style', 'sync_status']
    search_fields = ['title_en', 'title_fr', 'unit__title_en']

@admin.register(CMSLesson)
class CMSLessonAdmin(admin.ModelAdmin):
    list_display = ['title_fr', 'unit', 'chapter', 'lesson_type', 'order', 'sync_status']
    list_filter = ['lesson_type', 'sync_status']
    search_fields = ['title_en', 'title_fr', 'unit__title_en']

@admin.register(CMSContentLesson)
class CMSContentLessonAdmin(admin.ModelAdmin):
    list_display = ['title_fr', 'lesson', 'content_type', 'order', 'sync_status']
    list_filter = ['content_type', 'sync_status']
    search_fields = ['title_en', 'title_fr', 'lesson__title_en']

@admin.register(CMSVocabularyList)
class CMSVocabularyListAdmin(admin.ModelAdmin):
    list_display = ['title_fr', 'content_lesson', 'sync_status']
    search_fields = ['title_en', 'title_fr']

@admin.register(CMSVocabularyWord)
class CMSVocabularyWordAdmin(admin.ModelAdmin):
    list_display = ['word_fr', 'word_en', 'vocabulary_list', 'order']
    search_fields = ['word_en', 'word_fr', 'word_es', 'word_nl']

@admin.register(CMSTheoryContent)
class CMSTheoryContentAdmin(admin.ModelAdmin):
    list_display = ['content_lesson', 'sync_status']
    search_fields = ['content_en', 'content_fr']