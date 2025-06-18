from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from core.jobs.models import Department, JobPosition, JobApplication


class ApplicationTypeFilter(admin.SimpleListFilter):
    title = 'Type de candidature'
    parameter_name = 'application_type'

    def lookups(self, request, model_admin):
        return (
            ('spontaneous', 'Candidatures spontanées'),
            ('position', 'Candidatures pour un poste'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'spontaneous':
            return queryset.filter(position__isnull=True)
        if self.value() == 'position':
            return queryset.filter(position__isnull=False)
        return queryset


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'position_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    def position_count(self, obj):
        count = obj.positions.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:jobs_jobposition_changelist') + f'?department__id__exact={obj.id}'
            return format_html('<a href="{}">{} active positions</a>', url, count)
        return '0 positions'
    position_count.short_description = 'Active Positions'


class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    readonly_fields = ['applied_at', 'full_name_display', 'email', 'status']
    fields = ['full_name_display', 'email', 'status', 'applied_at']
    can_delete = False
    
    def full_name_display(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name_display.short_description = 'Full Name'
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'department', 
        'location', 
        'employment_type', 
        'status_badge', 
        'application_count',
        'posted_date'
    ]
    list_filter = [
        'is_active', 
        'is_featured', 
        'department', 
        'employment_type', 
        'experience_level',
        'posted_date'
    ]
    search_fields = ['title', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at', 'application_count_detail']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'department', 'location', 'employment_type', 'experience_level')
        }),
        ('Job Details', {
            'fields': ('description', 'requirements', 'responsibilities', 'benefits'),
            'classes': ('wide',)
        }),
        ('Salary Information', {
            'fields': ('salary_min', 'salary_max', 'salary_currency'),
            'classes': ('collapse',)
        }),
        ('Application Settings', {
            'fields': ('application_email', 'application_url')
        }),
        ('Status & Dates', {
            'fields': ('is_active', 'is_featured', 'posted_date', 'closing_date'),
            'description': 'Set closing_date to prevent new applications. Leave empty for indefinite applications.'
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'application_count_detail'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [JobApplicationInline]
    
    def status_badge(self, obj):
        if obj.is_open:
            color = 'green' if obj.is_featured else 'blue'
            text = 'Featured & Open' if obj.is_featured else 'Open'
        else:
            color = 'red'
            if obj.closing_date:
                from django.utils import timezone
                if obj.closing_date < timezone.now():
                    text = f'Closed (deadline passed: {obj.closing_date.strftime("%Y-%m-%d %H:%M")})'
                else:
                    text = 'Inactive'
            else:
                text = 'Inactive'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    status_badge.short_description = 'Status'
    
    def application_count(self, obj):
        count = obj.applications.count()
        if count > 0:
            url = reverse('admin:jobs_jobapplication_changelist') + f'?position__id__exact={obj.id}'
            return format_html('<a href="{}">{} applications</a>', url, count)
        return '0 applications'
    application_count.short_description = 'Applications'
    
    def application_count_detail(self, obj):
        total = obj.applications.count()
        if total == 0:
            return 'No applications yet'
        
        statuses = obj.applications.values('status').distinct()
        status_counts = []
        for status_dict in statuses:
            status = status_dict['status']
            count = obj.applications.filter(status=status).count()
            status_counts.append(f"{status.title()}: {count}")
        
        return f"Total: {total} ({', '.join(status_counts)})"
    application_count_detail.short_description = 'Application Breakdown'
    
    actions = ['make_active', 'make_inactive', 'make_featured']
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} job(s) marked as active.')
    make_active.short_description = 'Mark selected jobs as active'
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} job(s) marked as inactive.')
    make_inactive.short_description = 'Mark selected jobs as inactive'
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} job(s) marked as featured.')
    make_featured.short_description = 'Mark selected jobs as featured'


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 
        'position_display', 
        'email', 
        'status_badge', 
        'resume_status',
        'email_status',
        'applied_at'
    ]
    list_filter = ['status', ApplicationTypeFilter, 'position__department', 'applied_at']
    search_fields = ['first_name', 'last_name', 'email', 'position__title']
    readonly_fields = ['applied_at', 'updated_at', 'resume_download_link']
    
    fieldsets = (
        ('Application Details', {
            'fields': ('position', 'status')
        }),
        ('Applicant Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Application Materials', {
            'fields': ('cover_letter', 'resume_download_link', 'resume_url', 'portfolio_url', 'linkedin_url')
        }),
        ('Internal Notes', {
            'fields': ('notes',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        status_colors = {
            'submitted': 'blue',
            'reviewed': 'orange',
            'interview': 'purple',
            'offer': 'green',
            'hired': 'darkgreen',
            'rejected': 'red',
            'withdrawn': 'gray',
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def email_status(self, obj):
        """Show email notification status based on application status"""
        email_statuses = {
            'submitted': '📧 Confirmation sent',
            'reviewed': '👀 Review notification sent', 
            'interview': '🎯 Interview invite sent',
            'offer': '🎉 Offer email sent',
            'hired': '✅ Welcome email sent',
            'rejected': '📨 Rejection email sent',
            'withdrawn': '📤 Withdrawal confirmed',
        }
        
        if obj.status in email_statuses:
            return format_html(
                '<span style="color: #059669; font-size: 12px;">{}</span>',
                email_statuses[obj.status]
            )
        return '-'
    email_status.short_description = 'Email Status'
    
    actions = ['mark_reviewed', 'mark_interview', 'mark_offer', 'mark_hired', 'mark_rejected', 'mark_withdrawn']
    
    def mark_reviewed(self, request, queryset):
        # Update each instance individually to trigger signals
        count = 0
        for application in queryset:
            if application.status != 'reviewed':
                application.status = 'reviewed'
                application.save()
                count += 1
        self.message_user(request, f'{count} application(s) marked as under review. Email notifications sent.')
    mark_reviewed.short_description = 'Mark as under review'
    
    def mark_interview(self, request, queryset):
        count = 0
        for application in queryset:
            if application.status != 'interview':
                application.status = 'interview'
                application.save()
                count += 1
        self.message_user(request, f'{count} application(s) moved to interview stage. Email notifications sent.')
    mark_interview.short_description = 'Move to interview stage'
    
    def mark_offer(self, request, queryset):
        count = 0
        for application in queryset:
            if application.status != 'offer':
                application.status = 'offer'
                application.save()
                count += 1
        self.message_user(request, f'{count} application(s) marked with job offer. Email notifications sent.')
    mark_offer.short_description = 'Extend job offer'
    
    def mark_hired(self, request, queryset):
        count = 0
        for application in queryset:
            if application.status != 'hired':
                application.status = 'hired'
                application.save()
                count += 1
        self.message_user(request, f'{count} application(s) marked as hired. Email notifications sent.')
    mark_hired.short_description = 'Mark as hired'
    
    def mark_rejected(self, request, queryset):
        count = 0
        for application in queryset:
            if application.status != 'rejected':
                application.status = 'rejected'
                application.save()
                count += 1
        self.message_user(request, f'{count} application(s) marked as rejected. Email notifications sent.')
    mark_rejected.short_description = 'Mark as rejected'
    
    def mark_withdrawn(self, request, queryset):
        count = 0
        for application in queryset:
            if application.status != 'withdrawn':
                application.status = 'withdrawn'
                application.save()
                count += 1
        self.message_user(request, f'{count} application(s) marked as withdrawn.')
    mark_withdrawn.short_description = 'Mark as withdrawn'
    
    def resume_download_link(self, obj):
        """Display secure download link for resume"""
        if not obj.has_resume():
            return format_html('<span style="color: #666;">No resume uploaded</span>')
        
        download_url = reverse('jobs:download-resume', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank" style="color: #0066cc; text-decoration: none; padding: 5px 10px; border: 1px solid #0066cc; border-radius: 3px; font-size: 12px;">'
            '📄 Download Resume ({})</a><br/>'
            '<small style="color: #666;">Original filename: {}</small>',
            download_url,
            obj.resume_content_type or 'Unknown type',
            obj.resume_original_filename or 'Unknown'
        )
    resume_download_link.short_description = 'Resume File'
    
    def resume_status(self, obj):
        """Display resume status in list view"""
        if obj.has_resume():
            return format_html('<span style="color: green;">✅ CV</span>')
        else:
            return format_html('<span style="color: #ccc;">❌ No CV</span>')
    resume_status.short_description = 'CV'
    
    def position_display(self, obj):
        """Display position or 'Spontaneous' if no position"""
        if obj.position:
            return obj.position.title
        else:
            return format_html('<span style="color: #e67e22; font-weight: bold;">🎯 Candidature spontanée</span>')
    position_display.short_description = 'Poste'
    
    def get_queryset(self, request):
        """Override to show spontaneous applications prominently"""
        qs = super().get_queryset(request)
        return qs.select_related('position', 'position__department')