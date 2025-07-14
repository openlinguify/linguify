# backend/chat/admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import Conversation, ConversationMessage, Call, CallParticipant

class ConversationMessageInline(admin.TabularInline):
    model = ConversationMessage
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at', 'get_users')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('users__username', 'users__email')
    inlines = [ConversationMessageInline]
    
    def get_users(self, obj):
        return ", ".join([user.username for user in obj.users.all()])
    get_users.short_description = 'Users'

@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'created_by', 'sent_to', 'created_at', 'body_preview')
    list_filter = ('created_at',)
    search_fields = ('body', 'created_by__username', 'sent_to__username')
    readonly_fields = ('created_at',)
    
    def body_preview(self, obj):
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
    body_preview.short_description = 'Message Preview'

class CallParticipantInline(admin.TabularInline):
    model = CallParticipant
    extra = 0
    readonly_fields = ('joined_at', 'left_at')

@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('id', 'caller', 'receiver', 'call_type', 'status', 'started_at', 'duration_display', 'room_id')
    list_filter = ('call_type', 'status', 'started_at')
    search_fields = ('caller__username', 'receiver__username', 'room_id')
    readonly_fields = ('room_id', 'started_at', 'ended_at', 'duration')
    inlines = [CallParticipantInline]
    
    def duration_display(self, obj):
        if obj.duration:
            minutes = obj.duration // 60
            seconds = obj.duration % 60
            return f"{minutes}m {seconds}s"
        return "N/A"
    duration_display.short_description = 'Duration'

@admin.register(CallParticipant)
class CallParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'call', 'user', 'joined_at', 'left_at', 'is_muted_audio', 'is_muted_video', 'duration_in_call')
    list_filter = ('joined_at', 'left_at', 'is_muted_audio', 'is_muted_video')
    search_fields = ('user__username', 'call__room_id')
    readonly_fields = ('joined_at', 'left_at')
    
    def duration_in_call(self, obj):
        if obj.joined_at and obj.left_at:
            duration = (obj.left_at - obj.joined_at).total_seconds()
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            return f"{minutes}m {seconds}s"
        elif obj.joined_at:
            return "Still in call"
        return "N/A"
    duration_in_call.short_description = 'Time in Call'