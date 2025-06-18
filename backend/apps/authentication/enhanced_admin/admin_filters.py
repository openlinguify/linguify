"""
Custom admin filters for the Linguify project.
"""
from django.contrib import admin
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

class RegistrationDateFilter(admin.SimpleListFilter):
    title = 'Registration Date'
    parameter_name = 'created_at'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_week', 'This week'),
            ('last_week', 'Last week'),
            ('this_month', 'This month'),
            ('last_month', 'Last month'),
            ('this_year', 'This year'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'today':
            return queryset.filter(created_at__date=now.date())
        if self.value() == 'yesterday':
            yesterday = now - timedelta(days=1)
            return queryset.filter(created_at__date=yesterday.date())
        if self.value() == 'this_week':
            start_of_week = now - timedelta(days=now.weekday())
            return queryset.filter(created_at__date__gte=start_of_week.date())
        if self.value() == 'last_week':
            start_of_last_week = now - timedelta(days=now.weekday() + 7)
            end_of_last_week = start_of_last_week + timedelta(days=6)
            return queryset.filter(created_at__date__gte=start_of_last_week.date(),
                                 created_at__date__lte=end_of_last_week.date())
        if self.value() == 'this_month':
            return queryset.filter(created_at__month=now.month, created_at__year=now.year)
        if self.value() == 'last_month':
            last_month = now.month - 1 if now.month > 1 else 12
            last_month_year = now.year if now.month > 1 else now.year - 1
            return queryset.filter(created_at__month=last_month, created_at__year=last_month_year)
        if self.value() == 'this_year':
            return queryset.filter(created_at__year=now.year)
        return queryset

class AccountStatusFilter(admin.SimpleListFilter):
    title = 'Account Status'
    parameter_name = 'account_status'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('pending_deletion', 'Pending Deletion'),
            ('deletion_soon', 'Deletion within 7 days'),
            ('new_users', 'New Users (last 30 days)'),
            ('inactive_long', 'Inactive > 90 days'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'active':
            return queryset.filter(is_active=True, is_pending_deletion=False)
        if self.value() == 'inactive':
            return queryset.filter(is_active=False)
        if self.value() == 'pending_deletion':
            return queryset.filter(is_pending_deletion=True)
        if self.value() == 'deletion_soon':
            deletion_cutoff = now + timedelta(days=7)
            return queryset.filter(is_pending_deletion=True, 
                                 deletion_date__lte=deletion_cutoff)
        if self.value() == 'new_users':
            thirty_days_ago = now - timedelta(days=30)
            return queryset.filter(created_at__gte=thirty_days_ago)
        if self.value() == 'inactive_long':
            ninety_days_ago = now - timedelta(days=90)
            return queryset.filter(is_active=True, last_login__lt=ninety_days_ago)
        return queryset

class ProfileCompletionFilter(admin.SimpleListFilter):
    title = 'Profile Completion'
    parameter_name = 'profile_completion'

    def lookups(self, request, model_admin):
        return (
            ('complete', 'Complete Profile'),
            ('incomplete', 'Incomplete Profile'),
            ('no_profile_pic', 'No Profile Picture'),
            ('no_bio', 'No Bio'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'complete':
            return queryset.exclude(
                Q(profile_picture='') | Q(profile_picture__isnull=True) |
                Q(bio='') | Q(bio__isnull=True) |
                Q(first_name='') | Q(last_name='')
            )
        if self.value() == 'incomplete':
            return queryset.filter(
                Q(profile_picture='') | Q(profile_picture__isnull=True) |
                Q(bio='') | Q(bio__isnull=True) |
                Q(first_name='') | Q(last_name='')
            )
        if self.value() == 'no_profile_pic':
            return queryset.filter(Q(profile_picture='') | Q(profile_picture__isnull=True))
        if self.value() == 'no_bio':
            return queryset.filter(Q(bio='') | Q(bio__isnull=True))
        return queryset