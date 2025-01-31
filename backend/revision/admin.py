from django.contrib import admin
from .models import (
    Flashcard,
    FlashcardDeck,
    RevisionSession,
    VocabularyWord,
    CreateRevisionList,
    AddField
)

@admin.register(FlashcardDeck)
class FlashcardDeckAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'user__username')
    date_hierarchy = 'created_at'

@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('front_text', 'back_text', 'deck', 'learned', 'review_count', 'last_reviewed')
    list_filter = ('learned', 'deck', 'created_at')
    search_fields = ('front_text', 'back_text')
    date_hierarchy = 'created_at'

@admin.register(RevisionSession)
class RevisionSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'scheduled_date', 'status', 'success_rate')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('user__username',)
    date_hierarchy = 'scheduled_date'

@admin.register(VocabularyWord)
class VocabularyWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'translation', 'source_language', 'target_language', 'mastery_level', 'review_count')
    list_filter = ('source_language', 'target_language', 'mastery_level')
    search_fields = ('word', 'translation', 'context')
    date_hierarchy = 'created_at'

@admin.register(CreateRevisionList)
class CreateRevisionListAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'created_at'

@admin.register(AddField)
class AddFieldAdmin(admin.ModelAdmin):
    list_display = ('field_1', 'field_2', 'user', 'revision_list', 'last_reviewed')
    list_filter = ('created_at', 'last_reviewed')
    search_fields = ('field_1', 'field_2', 'user__username')
    date_hierarchy = 'created_at'