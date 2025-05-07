from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Avg
from .models import User, CoachProfile, Review, UserFeedback

class CoachProfileInline(admin.StackedInline):
    model = CoachProfile
    can_delete = False
    verbose_name_plural = "Coach Profile"
    fk_name = "user"
    fieldsets = (
        (None, {
            'fields': ('coaching_languages', 'price_per_hour', 'availability')
        }),
        ('Commission Settings', {
            'fields': ('commission_rate', 'commission_override'),
            'classes': ('collapse',),
        }),
        ('Description', {
            'fields': ('description', 'bio'),
            'classes': ('wide',),
        }),
    )
    extra = 0

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'full_name', 'language_info', 'is_active', 'is_staff', 'is_coach')
    list_filter = ('is_active', 'is_staff', 'is_coach', 'native_language', 'target_language')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'public_id')
    readonly_fields = ('public_id', 'created_at', 'updated_at', 'last_login')
    exclude = ('password',)  # Do not expose password hash in admin forms
    inlines = [CoachProfileInline]
    ordering = ('email',)
    actions = ['activate_users', 'deactivate_users', 'make_coaches', 'remove_coach_status']
    
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'first_name', 'last_name')
        }),
        ('Profile', {
            'fields': ('profile_picture', 'bio', 'birthday', 'gender'),
        }),
        ('Language Settings', {
            'fields': ('native_language', 'target_language', 'language_level', 'objectives'),
        }),
        ('Status', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_coach'),
        }),
        ('Learning Preferences', {
            'fields': (
                'speaking_exercises', 'listening_exercises', 
                'reading_exercises', 'writing_exercises',
                'daily_goal'
            ),
            'classes': ('collapse',),
        }),
        ('System Information', {
            'fields': ('public_id', 'created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',),
        }),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Name"
    
    def language_info(self, obj):
        return f"{obj.native_language} → {obj.target_language} ({obj.language_level})"
    language_info.short_description = "Languages"
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} users successfully activated.")
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} users successfully deactivated.")
    deactivate_users.short_description = "Deactivate selected users"
    
    def make_coaches(self, request, queryset):
        updated = queryset.update(is_coach=True)
        self.message_user(request, f"{updated} users successfully marked as coaches.")
    make_coaches.short_description = "Mark selected users as coaches"
    
    def remove_coach_status(self, request, queryset):
        updated = queryset.update(is_coach=False)
        self.message_user(request, f"{updated} users successfully removed from coach status.")
    remove_coach_status.short_description = "Remove coach status from selected users"

@admin.register(CoachProfile)
class CoachProfileAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'coaching_languages', 'price_per_hour', 'availability_preview', 'commission_rate')
    list_filter = ('coaching_languages', 'user__is_active')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    
    def user_link(self, obj):
        url = reverse("admin:authentication_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"
    
    def availability_preview(self, obj):
        if obj.availability and len(obj.availability) > 30:
            return f"{obj.availability[:30]}..."
        return obj.availability
    availability_preview.short_description = "Availability"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('coach_link', 'reviewer_link', 'rating_display', 'comment_preview', 'review_date')
    list_filter = ('rating', 'review_date')
    search_fields = ('coach__user__username', 'reviewer__username', 'comment')
    
    def coach_link(self, obj):
        url = reverse("admin:authentication_coachprofile_change", args=[obj.coach.id])
        return format_html('<a href="{}">{}</a>', url, obj.coach.user.username)
    coach_link.short_description = "Coach"
    
    def reviewer_link(self, obj):
        url = reverse("admin:authentication_user_change", args=[obj.reviewer.id])
        return format_html('<a href="{}">{}</a>', url, obj.reviewer.username)
    reviewer_link.short_description = "Reviewer"
    
    def rating_display(self, obj):
        stars = '★' * int(obj.rating)
        empty_stars = '☆' * (5 - int(obj.rating))
        return format_html('<span style="color: #f1c40f;">{}</span>{} ({:.1f})', 
                          stars, empty_stars, obj.rating)
    rating_display.short_description = "Rating"
    
    def comment_preview(self, obj):
        if obj.comment and len(obj.comment) > 50:
            return f"{obj.comment[:50]}..."
        return obj.comment or "No comment"
    comment_preview.short_description = "Comment"

@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'feedback_type', 'feedback_preview', 'feedback_date')
    list_filter = ('feedback_type', 'feedback_date')
    search_fields = ('user__username', 'user__email', 'feedback_content')
    
    def user_link(self, obj):
        url = reverse("admin:authentication_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"
    
    def feedback_preview(self, obj):
        if hasattr(obj, 'feedback_content') and obj.feedback_content and len(obj.feedback_content) > 50:
            return f"{obj.feedback_content[:50]}..."
        return getattr(obj, 'feedback_content', '') or "No content"
    feedback_preview.short_description = "Feedback"

# Enhance the admin interface with additional features
try:
    from apps.authentication.enhanced_admin.admin_enhancements import enhance_user_admin, enhance_coach_admin
    enhance_user_admin(UserAdmin)
    enhance_coach_admin(CoachProfileAdmin)
except ImportError:
    pass