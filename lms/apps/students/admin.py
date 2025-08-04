# Admin disabled for multi-tenant architecture
# Student data is managed per organization in tenant databases
# Access student data through organization-specific dashboards

from django.contrib import admin
from .models import StudentProfile, CourseEnrollment

# NOTE: Admin registration is commented out because in our multi-tenant LMS:
# - Student data resides in organization-specific databases
# - The main admin accesses the default database which doesn't contain student data
# - Student administration should be done through organization-specific interfaces

# Uncomment the following lines only if you want to enable admin for a specific tenant database
# or if you modify the architecture to include student data in the main database

# @admin.register(StudentProfile)
# class StudentProfileAdmin(admin.ModelAdmin):
#     list_display = [
#         'student_id', 'user', 'organization_id', 'program', 
#         'academic_year', 'status', 'gpa', 'progress_percentage'
#     ]
#     list_filter = [
#         'organization_id', 'academic_year', 'status', 'study_mode', 'program'
#     ]
#     search_fields = [
#         'student_id', 'user__username', 'user__email', 
#         'user__first_name', 'user__last_name', 'program'
#     ]
#     readonly_fields = ['created_at', 'updated_at', 'progress_percentage']
#     
#     fieldsets = (
#         ('Informations de base', {
#             'fields': ('user', 'student_id', 'organization_id')
#         }),
#         ('Informations académiques', {
#             'fields': (
#                 'program', 'specialization', 'academic_year', 
#                 'study_mode', 'status'
#             )
#         }),
#         ('Dates importantes', {
#             'fields': ('enrollment_date', 'expected_graduation')
#         }),
#         ('Progression', {
#             'fields': ('gpa', 'credits_earned', 'credits_required', 'progress_percentage')
#         }),
#         ('Contact d\'urgence', {
#             'fields': (
#                 'emergency_contact_name', 'emergency_contact_phone', 
#                 'emergency_contact_relation'
#             ),
#             'classes': ('collapse',)
#         }),
#         ('Métadonnées', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )


# @admin.register(CourseEnrollment)
# class CourseEnrollmentAdmin(admin.ModelAdmin):
#     list_display = [
#         'student', 'course_name', 'status', 'final_grade', 
#         'credits', 'enrolled_at'
#     ]
#     list_filter = ['status', 'credits', 'enrolled_at']
#     search_fields = [
#         'student__user__username', 'student__student_id', 
#         'course_id', 'course_name'
#     ]
#     readonly_fields = ['enrolled_at']