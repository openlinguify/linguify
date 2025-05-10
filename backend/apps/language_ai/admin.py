from django.contrib import admin
from .models import AIConversation, ConversationMessage, ConversationFeedback, ConversationTopic

@admin.register(ConversationTopic)
class ConversationTopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'language', 'difficulty', 'is_active')
    list_filter = ('language', 'difficulty', 'is_active')
    search_fields = ('name', 'description')

class ConversationMessageInline(admin.TabularInline):
    model = ConversationMessage
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'language', 'created_at', 'last_activity', 'status')
    list_filter = ('language', 'status', 'created_at')
    search_fields = ('user__username', 'user__email', 'topic__name')
    inlines = [ConversationMessageInline]
    readonly_fields = ('created_at', 'last_activity')

@admin.register(ConversationFeedback)
class ConversationFeedbackAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'correction_type', 'created_at')
    list_filter = ('correction_type', 'created_at')
    search_fields = ('message__content', 'user__username', 'corrected_content')