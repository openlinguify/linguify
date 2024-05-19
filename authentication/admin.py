from django.contrib import admin
from .models import User, UserSetting, UserFeedback

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'profile_picture', 'mother_language', 'learning_language', 'language_level', 'objectives')
    search_fields = ('username', 'email', 'profile_picture', 'mother_language', 'learning_language', 'language_level', 'objectives')
    list_filter = ('username', 'email', 'profile_picture', 'mother_language', 'learning_language', 'language_level', 'objectives')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'profile_picture', 'mother_language', 'learning_language', 'language_level', 'objectives')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'profile_picture', 'mother_language', 'learning_language', 'language_level', 'objectives', 'password1', 'password2'),
        }),
    )
    ordering = ('username',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
