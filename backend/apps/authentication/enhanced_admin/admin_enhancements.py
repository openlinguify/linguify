"""
Enhancements for the Django admin interface.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django import forms
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.db.models import Avg
from datetime import timedelta
import csv

from .admin_filters import RegistrationDateFilter, AccountStatusFilter, ProfileCompletionFilter

def enhance_user_admin(UserAdmin):
    """
    Enhances the UserAdmin class with additional functionality.

    This function adds:
    - Additional list display fields
    - Custom filters
    - Account deletion section
    - Export functionality
    - Notification sending
    - Language learning profile inline

    Args:
        UserAdmin: The existing UserAdmin class to enhance
    """

    # Add to list_display
    if 'deletion_status' not in UserAdmin.list_display:
        UserAdmin.list_display = list(UserAdmin.list_display) + ['deletion_status']

    # Add custom filters
    UserAdmin.list_filter = list(UserAdmin.list_filter) + [
        AccountStatusFilter,
        ProfileCompletionFilter,
        RegistrationDateFilter
    ]

    # Add UserLearningProfileInline from language_learning app
    try:
        from apps.language_learning.admin import UserLearningProfileInline
        if UserLearningProfileInline not in UserAdmin.inlines:
            UserAdmin.inlines = list(UserAdmin.inlines) + [UserLearningProfileInline]
    except (ImportError, RuntimeError):
        # Language learning app not available or not in INSTALLED_APPS, skip adding the inline
        pass
    
    # Add readonly fields
    UserAdmin.readonly_fields = list(UserAdmin.readonly_fields) + [
        'days_until_deletion_display', 
        'account_age'
    ]
    
    # Add custom actions
    UserAdmin.actions = list(UserAdmin.actions) + [
        'cancel_scheduled_deletions', 
        'schedule_account_deletions', 
        'export_user_data', 
        'send_notification_to_users'
    ]
    
    # Add Account Deletion fieldset if it doesn't exist
    has_deletion_fieldset = False
    for name, options in UserAdmin.fieldsets:
        if name == 'Account Deletion':
            has_deletion_fieldset = True
            break
    
    if not has_deletion_fieldset:
        fieldsets = list(UserAdmin.fieldsets)
        fieldsets.insert(4, ('Account Deletion', {
            'fields': ('is_pending_deletion', 'deletion_scheduled_at', 'deletion_date', 'days_until_deletion_display'),
            'classes': ('wide',),
        }))
        UserAdmin.fieldsets = fieldsets
    
    # Add methods to the UserAdmin class
    UserAdmin.deletion_status = deletion_status
    UserAdmin.days_until_deletion_display = days_until_deletion_display
    UserAdmin.account_age = account_age
    UserAdmin.cancel_scheduled_deletions = cancel_scheduled_deletions
    UserAdmin.schedule_account_deletions = schedule_account_deletions
    UserAdmin.export_user_data = export_user_data
    UserAdmin.send_notification_to_users = send_notification_to_users
    
    return UserAdmin

def enhance_coach_admin(CoachProfileAdmin):
    """
    Enhances the CoachProfileAdmin class with additional functionality.
    
    Args:
        CoachProfileAdmin: The existing CoachProfileAdmin class to enhance
    """
    
    # Update list_display
    CoachProfileAdmin.list_display = (
        'user_link', 'coach_name', 'coaching_languages', 'price_per_hour', 
        'commission_amount', 'revenue_after_commission', 'availability_preview', 
        'rating_summary'
    )
    
    # Update list_filter
    CoachProfileAdmin.list_filter = (
        'coaching_languages', 'user__is_active', 'price_per_hour'
    )
    
    # Set ordering
    CoachProfileAdmin.ordering = ('-price_per_hour',)
    
    # Add methods to the CoachProfileAdmin class
    CoachProfileAdmin.coach_name = coach_name
    CoachProfileAdmin.commission_amount = commission_amount
    CoachProfileAdmin.revenue_after_commission = revenue_after_commission
    CoachProfileAdmin.rating_summary = rating_summary
    CoachProfileAdmin.get_queryset = get_coach_queryset
    
    return CoachProfileAdmin


# Methods for UserAdmin

def deletion_status(self, obj):
    """Display account deletion status in list view"""
    if obj.is_pending_deletion:
        days = obj.days_until_deletion()
        return format_html(
            '<span style="color: #e74c3c;">Deletion in {} days</span>',
            days if days is not None else '?'
        )
    return format_html('<span style="color: #2ecc71;">Active</span>' if obj.is_active else 
                      '<span style="color: #f39c12;">Inactive</span>')
deletion_status.short_description = "Deletion Status"

def days_until_deletion_display(self, obj):
    """Read-only field showing days remaining until deletion"""
    if not obj.is_pending_deletion:
        return "N/A"
    days = obj.days_until_deletion()
    if days is None:
        return "Unknown"
    elif days <= 0:
        return "Deletion imminent"
    elif days == 1:
        return "1 day remaining"
    else:
        return f"{days} days remaining"
days_until_deletion_display.short_description = "Time Until Deletion"

def account_age(self, obj):
    """Calculate account age"""
    if not obj.created_at:
        return "Unknown"
        
    now = timezone.now()
    days = (now - obj.created_at).days
    
    if days < 1:
        hours = (now - obj.created_at).seconds // 3600
        return f"{hours} hours"
    elif days < 30:
        return f"{days} days"
    elif days < 365:
        months = days // 30
        return f"{months} months"
    else:
        years = days // 365
        remaining_days = days % 365
        remaining_months = remaining_days // 30
        if remaining_months > 0:
            return f"{years} years, {remaining_months} months"
        return f"{years} years"
account_age.short_description = "Account Age"

def cancel_scheduled_deletions(self, request, queryset):
    """Admin action to cancel scheduled deletions for selected users"""
    canceled_count = 0
    for user in queryset:
        if user.is_pending_deletion:
            user.cancel_account_deletion()
            canceled_count += 1
    
    if canceled_count > 0:
        self.message_user(request, f"Canceled scheduled deletion for {canceled_count} users.")
    else:
        self.message_user(request, "No users with scheduled deletions were selected.")
cancel_scheduled_deletions.short_description = "Cancel scheduled account deletions"

def schedule_account_deletions(self, request, queryset):
    """Admin action to schedule deletions for selected users"""
    scheduled_count = 0
    for user in queryset:
        if not user.is_pending_deletion:
            user.schedule_account_deletion()
            scheduled_count += 1
    
    if scheduled_count > 0:
        self.message_user(request, f"Scheduled deletion for {scheduled_count} users (30-day grace period).")
    else:
        self.message_user(request, "No active users were selected or all selected users already have scheduled deletions.")
schedule_account_deletions.short_description = "Schedule deletion (30-day grace period)"

def export_user_data(self, request, queryset):
    """Export user data as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write header row
    writer.writerow([
        'Email', 'Username', 'First Name', 'Last Name', 'Native Language',
        'Target Language', 'Level', 'Is Active', 'Is Coach', 'Joined',
        'Last Login', 'Profile Completion'
    ])
    
    # Write data rows
    for user in queryset:
        # Calculate profile completion
        fields = [
            bool(user.profile_picture),
            bool(user.first_name),
            bool(user.last_name),
            bool(user.bio),
            bool(user.birthday),
            bool(user.gender)
        ]
        completion = int((sum(fields) / len(fields)) * 100)
        
        writer.writerow([
            user.email,
            user.username,
            user.first_name,
            user.last_name,
            # Note: Champs de langue supprimés - voir UserLearningProfile
            'Yes' if user.is_active else 'No',
            'Yes' if user.is_coach else 'No',
            user.created_at.strftime('%Y-%m-%d'),
            user.last_login.strftime('%Y-%m-%d') if user.last_login else 'Never',
            f"{completion}%"
        ])
    
    self.message_user(request, f"Exported {queryset.count()} users to CSV.")
    return response
export_user_data.short_description = "Export selected users to CSV"

def send_notification_to_users(self, request, queryset):
    """Send a custom notification to selected users"""
    class NotificationForm(forms.Form):
        subject = forms.CharField(max_length=100, required=True, 
                                 widget=forms.TextInput(attrs={'size': '40'}))
        message = forms.CharField(required=True, 
                                widget=forms.Textarea(attrs={'rows': 4, 'cols': 60}))
        send_email = forms.BooleanField(required=False, initial=True,
                                      help_text="Send as email (if unchecked, only in-app notification will be sent)")
        
    # Check if the form was submitted
    if 'apply' in request.POST:
        form = NotificationForm(request.POST)
        
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            send_email = form.cleaned_data['send_email']
            
            # Process each user
            sent_count = 0
            for user in queryset:
                if user.is_active:  # Only send to active users
                    # Here we would integrate with your notification system
                    # This is a placeholder - replace with actual notification logic
                    if send_email and user.email_notifications:
                        try:
                            from django.core.mail import send_mail
                            from django.conf import settings
                            
                            send_mail(
                                subject=subject,
                                message=message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[user.email],
                                fail_silently=False,
                            )
                            sent_count += 1
                        except Exception as e:
                            self.message_user(request, f"Error sending to {user.email}: {str(e)}", level='ERROR')
                    
                    # In-app notification logic would go here
                    
            self.message_user(request, f"Notification sent to {sent_count} users")
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = NotificationForm()
        
    # Render form template
    return TemplateResponse(request, 'admin/send_notification.html', {
        'title': 'Send Notification to Users',
        'queryset': queryset,
        'opts': self.model._meta,
        'form': form,
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        'media': self.media,
    })
send_notification_to_users.short_description = "Send notification to selected users"


# Methods for CoachProfileAdmin

def coach_name(self, obj):
    """Display coach's full name"""
    return f"{obj.user.first_name} {obj.user.last_name}"
coach_name.short_description = "Name"

def commission_amount(self, obj):
    """Calculate commission amount"""
    return f"${obj.calculate_commission():.2f}"
commission_amount.short_description = "Commission ($)"

def revenue_after_commission(self, obj):
    """Calculate net revenue after commission"""
    net = obj.price_per_hour - obj.calculate_commission()
    return f"${net:.2f}"
revenue_after_commission.short_description = "Net Revenue ($)"

def rating_summary(self, obj):
    """Display average rating with stars"""
    avg_rating = obj.reviews.aggregate(Avg('rating'))['rating__avg']
    
    if avg_rating is None:
        return "No ratings"
        
    # Round to nearest half star
    stars = round(avg_rating * 2) / 2
    full_stars = int(stars)
    half_star = (stars - full_stars) >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    
    star_html = '<span style="color: #f1c40f;">★</span>' * full_stars
    if half_star:
        star_html += '<span style="color: #f1c40f;">½</span>'
    star_html += '<span style="color: #bdc3c7;">☆</span>' * empty_stars
    
    return format_html('{} ({:.1f})', star_html, avg_rating or 0)
rating_summary.short_description = "Rating"

def get_coach_queryset(self, request):
    """Optimize queryset with select_related and prefetch_related"""
    return super(self.__class__, self).get_queryset(request).select_related('user').prefetch_related('reviews')