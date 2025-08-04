from django.contrib import admin
from .models import Organization, OrganizationUser, OrganizationMembership


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'plan', 'is_active', 'created_at']
    list_filter = ['plan', 'is_active', 'is_verified']
    search_fields = ['name', 'slug', 'email']
    readonly_fields = ['id', 'database_name', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'slug', 'domain', 'email', 'phone']
        }),
        ('Database', {
            'fields': ['database_name'],
            'classes': ['collapse']
        }),
        ('Plan & Limits', {
            'fields': ['plan', 'max_students', 'max_instructors']
        }),
        ('Status', {
            'fields': ['is_active', 'is_verified']
        }),
        ('Metadata', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(OrganizationUser)
class OrganizationUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('organizations')


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__username', 'user__email', 'organization__name']
    raw_id_fields = ['user', 'organization']