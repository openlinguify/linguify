# authentication admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LevelTarget, Language, UserSetting, UserFeedback

class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'mother_language', 'learning_language', 'is_staff', 'is_active', 'date_joined', 'role', 'objectives', 'level')
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('language_id', 'language_name', 'language_code')
class UsersettingAdmin(admin.ModelAdmin):
    list_display = ('user_setting_id', 'user_id', 'settings_language', 'settings_theme', 'settings_notifications', 'settings_email_notifications', 'settings_push_notifications', 'settings_sound_notifications', 'settings_language_notifications', 'settings_flashcards_notifications', 'settings_exercises_notifications', 'settings_lessons_notifications', 'settings_courses_notifications', 'settings_groups_notifications', 'settings_friends_notifications', 'settings_messages_notifications', 'settings_calls_notifications', 'settings_video_notifications', 'settings_audio_notifications', 'settings_text_notifications', 'settings_images_notifications', 'settings_videos_notifications', 'settings_audios_notifications', 'settings_files_notifications', 'settings_links_notifications')
class LevelTargetAdmin(admin.ModelAdmin):
    list_display = ['level']
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user_feedback_id', 'user_id', 'feedback_type', 'feedback_content', 'feedback_date')



admin.site.register(User, UserAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(UserSetting, UsersettingAdmin)
admin.site.register(LevelTarget, LevelTargetAdmin)
admin.site.register(UserFeedback, UserFeedbackAdmin)