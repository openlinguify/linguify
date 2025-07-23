from django.contrib import admin
from .models import Teacher, TeacherLanguage, TeacherQualification, TeacherAvailability

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'hourly_rate', 'years_experience', 'sync_status', 'created_at']
    list_filter = ['status', 'sync_status', 'years_experience']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['backend_id', 'last_sync', 'total_earnings']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'status', 'profile_picture')
        }),
        ('Biography', {
            'fields': ('bio_en', 'bio_fr', 'bio_es', 'bio_nl')
        }),
        ('Contact', {
            'fields': ('phone_number', 'country', 'city', 'timezone')
        }),
        ('Teaching', {
            'fields': ('years_experience', 'hourly_rate', 'max_students_per_class', 
                      'available_for_individual', 'available_for_group')
        }),
        ('Payment', {
            'fields': ('bank_account', 'tax_id')
        }),
        ('Statistics', {
            'fields': ('total_earnings', 'total_courses_sold', 'total_hours_taught', 'average_rating'),
            'classes': ('collapse',)
        }),
        ('Sync', {
            'fields': ('sync_status', 'backend_id', 'last_sync', 'sync_error'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TeacherLanguage)
class TeacherLanguageAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'language_name', 'proficiency', 'can_teach']
    list_filter = ['proficiency', 'can_teach']

@admin.register(TeacherQualification)
class TeacherQualificationAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'type', 'title', 'institution', 'year_obtained', 'verified']
    list_filter = ['type', 'verified', 'year_obtained']

@admin.register(TeacherAvailability)
class TeacherAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active']