from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Avg
from .models import User, CoachProfile, Review, UserFeedback, CookieConsent, CookieConsentLog

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
    list_display = ('email', 'username', 'full_name', 'language_info', 'terms_status', 'is_active', 'is_staff', 'is_coach')
    list_filter = ('terms_accepted', 'is_active', 'is_staff', 'is_coach', 'native_language', 'target_language')
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
        ('Terms & Conditions', {
            'fields': ('terms_accepted', 'terms_accepted_at', 'terms_version'),
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

    def terms_status(self, obj):
        if obj.terms_accepted:
            accepted_date = obj.terms_accepted_at.strftime('%Y-%m-%d') if obj.terms_accepted_at else 'Unknown date'
            return format_html('<span style="color: green;">✓</span> Accepted ({}, v{})',
                              accepted_date, obj.terms_version or 'n/a')
        return format_html('<span style="color: red;">✗</span> Not accepted')
    terms_status.short_description = "Terms & Conditions"
    
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


# ============================================================================
# Cookie Consent Admin Views
# ============================================================================

from django.contrib import admin
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

class CookieConsentLogInline(admin.TabularInline):
    """Inline for displaying consent logs"""
    model = CookieConsentLog
    extra = 0
    readonly_fields = ('action', 'old_values_formatted', 'new_values_formatted', 'ip_address', 'user_agent_short', 'created_at')
    can_delete = False
    fields = ('action', 'old_values_formatted', 'new_values_formatted', 'ip_address', 'user_agent_short', 'created_at')
    
    def old_values_formatted(self, obj):
        """Format old values JSON"""
        if obj.old_values:
            try:
                data = json.loads(obj.old_values) if isinstance(obj.old_values, str) else obj.old_values
                return format_html('<pre style="font-size: 11px;">{}</pre>', json.dumps(data, indent=2))
            except (json.JSONDecodeError, TypeError):
                return obj.old_values
        return '-'
    old_values_formatted.short_description = "Previous Values"
    
    def new_values_formatted(self, obj):
        """Format new values JSON"""
        if obj.new_values:
            try:
                data = json.loads(obj.new_values) if isinstance(obj.new_values, str) else obj.new_values
                return format_html('<pre style="font-size: 11px;">{}</pre>', json.dumps(data, indent=2))
            except (json.JSONDecodeError, TypeError):
                return obj.new_values
        return '-'
    new_values_formatted.short_description = "New Values"
    
    def user_agent_short(self, obj):
        """Display shortened user agent"""
        if obj.user_agent:
            return obj.user_agent[:80] + '...' if len(obj.user_agent) > 80 else obj.user_agent
        return '-'
    user_agent_short.short_description = "User Agent"
    
    def has_add_permission(self, request, obj=None):
        return False


class ConsentLevelFilter(admin.SimpleListFilter):
    """Custom filter for consent level"""
    title = 'Consent Level'
    parameter_name = 'consent_level'
    
    def lookups(self, request, model_admin):
        return (
            ('full', 'Full Consent (All categories)'),
            ('partial', 'Partial Consent (Some categories)'),
            ('minimal', 'Essential Only'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'full':
            return queryset.filter(
                essential=True, analytics=True, 
                functionality=True, performance=True
            )
        elif self.value() == 'partial':
            return queryset.filter(
                Q(analytics=True) | Q(functionality=True) | Q(performance=True)
            ).exclude(
                essential=True, analytics=True, 
                functionality=True, performance=True
            )
        elif self.value() == 'minimal':
            return queryset.filter(
                essential=True, analytics=False, 
                functionality=False, performance=False
            )


class ExpirationFilter(admin.SimpleListFilter):
    """Custom filter for consent expiration"""
    title = 'Expiration Status'
    parameter_name = 'expiration'
    
    def lookups(self, request, model_admin):
        return (
            ('expired', 'Expired'),
            ('expiring_soon', 'Expiring in 30 days'),
            ('valid', 'Valid'),
        )
    
    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'expired':
            return queryset.filter(expires_at__lt=now)
        elif self.value() == 'expiring_soon':
            future = now + timedelta(days=30)
            return queryset.filter(expires_at__range=(now, future))
        elif self.value() == 'valid':
            return queryset.filter(Q(expires_at__gt=now) | Q(expires_at__isnull=True))


@admin.register(CookieConsent)
class CookieConsentAdmin(admin.ModelAdmin):
    """Enhanced admin interface for cookie consents"""
    
    list_display = (
        'identifier', 'consent_summary_display', 'language', 'consent_method', 
        'version', 'expiration_status', 'created_at', 'revocation_status'
    )
    list_filter = (
        ConsentLevelFilter, ExpirationFilter, 'is_revoked', 'version', 
        'language', 'consent_method', 'created_at', 'revocation_reason'
    )
    search_fields = ('user__email', 'user__username', 'user__first_name', 'user__last_name', 'session_id', 'ip_address')
    readonly_fields = (
        'id', 'user', 'session_id', 'ip_address', 'user_agent_formatted', 
        'created_at', 'updated_at', 'is_revoked', 'revoked_at', 'consent_age',
        'expiration_info', 'consent_analytics'
    )
    
    fieldsets = (
        ('Identity', {
            'fields': ('id', 'user', 'session_id', 'ip_address')
        }),
        ('Consent Details', {
            'fields': (
                'version', 'language', 'consent_method',
                'essential', 'analytics', 'functionality', 'performance'
            )
        }),
        ('Analytics & Info', {
            'fields': ('consent_analytics', 'consent_age', 'expiration_info'),
            'classes': ('collapse',)
        }),
        ('Technical Details', {
            'fields': ('user_agent_formatted', 'created_at', 'updated_at', 'expires_at'),
            'classes': ('collapse',)
        }),
        ('Revocation', {
            'fields': ('is_revoked', 'revoked_at', 'revocation_reason'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [CookieConsentLogInline]
    
    actions = ['revoke_consents', 'export_consents', 'extend_expiration', 'send_renewal_notification']
    
    def identifier(self, obj):
        """Enhanced user identifier with better formatting"""
        if obj.user:
            name = f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
            return format_html(
                '<a href="{}" title="View user details">'
                '<strong>{}</strong><br>'
                '<small style="color: #666;">{}</small>'
                '</a>',
                reverse("admin:authentication_user_change", args=[obj.user.id]),
                name,
                obj.user.email
            )
        elif obj.session_id:
            return format_html(
                '<span title="Anonymous session">📱 Session<br>'
                '<small style="color: #666;">{}</small></span>',
                obj.session_id[:12] + '...'
            )
        else:
            return format_html(
                '<span title="IP only">🌐 Anonymous<br>'
                '<small style="color: #666;">{}</small></span>',
                obj.ip_address
            )
    identifier.short_description = "User/Session"
    identifier.admin_order_field = 'user__email'
    
    def consent_summary_display(self, obj):
        """Enhanced consent summary with better visuals"""
        summary = obj.get_consent_summary()
        level = summary['consent_level']
        categories = summary['categories']
        total = summary['total_accepted']
        
        # Visual indicators
        icons = {
            'Essential': '🔒',
            'Analytics': '📊', 
            'Functionality': '⚙️',
            'Performance': '⚡'
        }
        
        category_display = []
        for cat in categories:
            icon = icons.get(cat, '•')
            category_display.append(f"{icon} {cat}")
        
        color_map = {
            'full': '#28a745',
            'partial': '#ffc107', 
            'minimal': '#dc3545'
        }
        
        level_labels = {
            'full': '✅ Full Consent',
            'partial': '⚠️ Partial Consent', 
            'minimal': '🔒 Essential Only'
        }
        
        color = color_map.get(level, '#6c757d')
        label = level_labels.get(level, '❓ Unknown')
        
        return format_html(
            '<div style="line-height: 1.4;">'
            '<span style="color: {}; font-weight: bold; font-size: 13px;">{}</span><br>'
            '<small style="color: #666;">({}/4 categories)<br>{}</small>'
            '</div>',
            color, label, total, '<br>'.join(category_display)
        )
    consent_summary_display.short_description = "Consent Summary"
    
    def expiration_status(self, obj):
        """Display expiration status with visual indicators"""
        if not obj.expires_at:
            return format_html('<span style="color: #28a745;">♾️ No expiration</span>')
        
        now = timezone.now()
        if obj.expires_at < now:
            return format_html('<span style="color: #dc3545;">💀 Expired</span>')
        
        days_left = (obj.expires_at - now).days
        if days_left <= 7:
            return format_html('<span style="color: #fd7e14;">⚠️ {} days left</span>', days_left)
        elif days_left <= 30:
            return format_html('<span style="color: #ffc107;">⏰ {} days left</span>', days_left)
        else:
            return format_html('<span style="color: #28a745;">✅ {} days left</span>', days_left)
    expiration_status.short_description = "Expiration"
    expiration_status.admin_order_field = 'expires_at'
    
    def revocation_status(self, obj):
        """Enhanced revocation status display"""
        if obj.is_revoked:
            reason = obj.revocation_reason or 'Unknown'
            revoked_date = obj.revoked_at.strftime('%Y-%m-%d %H:%M') if obj.revoked_at else 'Unknown'
            return format_html(
                '<span style="color: #dc3545;" title="Revoked: {}">❌ Revoked<br>'
                '<small>{}</small></span>',
                revoked_date, reason
            )
        else:
            return format_html('<span style="color: #28a745;">✅ Active</span>')
    revocation_status.short_description = "Status"
    revocation_status.admin_order_field = 'is_revoked'
    
    def user_agent_formatted(self, obj):
        """Format user agent for better readability"""
        if not obj.user_agent:
            return '-'
        
        # Simple parsing for common patterns
        ua = obj.user_agent
        browser = "Unknown"
        os = "Unknown"
        
        if "Chrome/" in ua:
            browser = "Chrome"
        elif "Firefox/" in ua:
            browser = "Firefox"
        elif "Safari/" in ua and "Chrome/" not in ua:
            browser = "Safari"
        elif "Edge/" in ua:
            browser = "Edge"
        
        if "Windows" in ua:
            os = "Windows"
        elif "Macintosh" in ua:
            os = "macOS"
        elif "Linux" in ua:
            os = "Linux"
        elif "Android" in ua:
            os = "Android"
        elif "iPhone" in ua or "iPad" in ua:
            os = "iOS"
        
        return format_html(
            '<div>'
            '<strong>{} on {}</strong><br>'
            '<details style="margin-top: 5px;">'
            '<summary style="cursor: pointer; color: #666;">View full user agent</summary>'
            '<pre style="font-size: 11px; margin: 5px 0; white-space: pre-wrap;">{}</pre>'
            '</details>'
            '</div>',
            browser, os, ua
        )
    user_agent_formatted.short_description = "User Agent"
    
    def consent_age(self, obj):
        """Display age of consent"""
        if obj.created_at:
            delta = timezone.now() - obj.created_at
            days = delta.days
            hours = delta.seconds // 3600
            
            if days > 0:
                return f"{days} days ago"
            elif hours > 0:
                return f"{hours} hours ago"
            else:
                return "Less than 1 hour ago"
        return "-"
    consent_age.short_description = "Age"
    
    def expiration_info(self, obj):
        """Detailed expiration information"""
        if not obj.expires_at:
            return "No expiration set"
        
        now = timezone.now()
        delta = obj.expires_at - now
        
        if delta.total_seconds() < 0:
            return format_html('<span style="color: red;">Expired {} days ago</span>', abs(delta.days))
        else:
            return f"Expires in {delta.days} days ({obj.expires_at.strftime('%Y-%m-%d %H:%M')})"
    expiration_info.short_description = "Expiration Details"
    
    def consent_analytics(self, obj):
        """Display consent analytics"""
        summary = obj.get_consent_summary()
        return format_html(
            '<ul style="margin: 0; padding-left: 15px;">'
            '<li>Level: <strong>{}</strong></li>'
            '<li>Categories: <strong>{}</strong></li>'
            '<li>Method: <strong>{}</strong></li>'
            '<li>Version: <strong>{}</strong></li>'
            '</ul>',
            summary['consent_level'].title(),
            ', '.join(summary['categories']) or 'None',
            obj.consent_method.replace('_', ' ').title(),
            obj.version
        )
    consent_analytics.short_description = "Analytics"
    
    def revoke_consents(self, request, queryset):
        """Enhanced admin action to revoke selected consents"""
        count = 0
        for consent in queryset.filter(is_revoked=False):
            consent.revoke(reason='admin_bulk_action')
            count += 1
        
        self.message_user(
            request,
            f"Successfully revoked {count} consent(s). Audit logs have been created.",
            level='SUCCESS' if count > 0 else 'WARNING'
        )
    revoke_consents.short_description = "🚫 Revoke selected consents"
    
    def extend_expiration(self, request, queryset):
        """Admin action to extend expiration by 1 year"""
        from datetime import timedelta
        count = 0
        new_expiration = timezone.now() + timedelta(days=365)
        
        for consent in queryset.filter(is_revoked=False):
            consent.expires_at = new_expiration
            consent.save()
            count += 1
        
        self.message_user(
            request,
            f"Extended expiration for {count} consent(s) to {new_expiration.strftime('%Y-%m-%d')}.",
            level='SUCCESS'
        )
    extend_expiration.short_description = "⏰ Extend expiration by 1 year"
    
    def export_consents(self, request, queryset):
        """Enhanced CSV export with more data"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="cookie_consents_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'User Email', 'User Name', 'Session ID', 'IP Address', 'Version',
            'Essential', 'Analytics', 'Functionality', 'Performance',
            'Language', 'Method', 'Created At', 'Expires At', 'Is Revoked', 'Revoked At',
            'Revocation Reason', 'Consent Level', 'Browser', 'OS'
        ])
        
        for consent in queryset.select_related('user'):
            # Parse user agent for browser/OS
            ua = consent.user_agent or ''
            browser = 'Unknown'
            os = 'Unknown'
            
            if "Chrome/" in ua:
                browser = "Chrome"
            elif "Firefox/" in ua:
                browser = "Firefox"
            elif "Safari/" in ua and "Chrome/" not in ua:
                browser = "Safari"
                
            if "Windows" in ua:
                os = "Windows"
            elif "Macintosh" in ua:
                os = "macOS"
            elif "Android" in ua:
                os = "Android"
            elif "iPhone" in ua or "iPad" in ua:
                os = "iOS"
            
            summary = consent.get_consent_summary()
            user_name = ''
            if consent.user:
                user_name = f"{consent.user.first_name} {consent.user.last_name}".strip() or consent.user.username
            
            writer.writerow([
                str(consent.id),
                consent.user.email if consent.user else '',
                user_name,
                consent.session_id or '',
                consent.ip_address or '',
                consent.version,
                consent.essential,
                consent.analytics,
                consent.functionality,
                consent.performance,
                consent.language,
                consent.consent_method,
                consent.created_at.isoformat(),
                consent.expires_at.isoformat() if consent.expires_at else '',
                consent.is_revoked,
                consent.revoked_at.isoformat() if consent.revoked_at else '',
                consent.revocation_reason or '',
                summary['consent_level'],
                browser,
                os
            ])
        
        return response
    export_consents.short_description = "📊 Export selected consents as CSV"
    
    def send_renewal_notification(self, request, queryset):
        """Admin action to send renewal notifications"""
        # This would integrate with your notification system
        count = queryset.filter(
            expires_at__lte=timezone.now() + timedelta(days=30),
            is_revoked=False,
            user__isnull=False
        ).count()
        
        self.message_user(
            request,
            f"Would send renewal notifications to {count} users (feature not implemented yet).",
            level='INFO'
        )
    send_renewal_notification.short_description = "📧 Send renewal notifications"
    
    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user').prefetch_related('logs')
    
    def changelist_view(self, request, extra_context=None):
        """Add custom context to changelist"""
        extra_context = extra_context or {}
        
        # Add summary statistics
        qs = self.get_queryset(request)
        extra_context['consent_stats'] = {
            'total': qs.count(),
            'active': qs.filter(is_revoked=False).count(),
            'revoked': qs.filter(is_revoked=True).count(),
            'expiring_soon': qs.filter(
                expires_at__lte=timezone.now() + timedelta(days=30),
                is_revoked=False
            ).count(),
            'full_consent': qs.filter(
                essential=True, analytics=True,
                functionality=True, performance=True,
                is_revoked=False
            ).count(),
        }
        
        return super().changelist_view(request, extra_context)


@admin.register(CookieConsentLog)
class CookieConsentLogAdmin(admin.ModelAdmin):
    """Admin interface for cookie consent logs"""
    
    list_display = (
        'consent_identifier', 'action', 'created_at', 'ip_address'
    )
    list_filter = ('action', 'created_at')
    search_fields = ('consent__user__email', 'consent__session_id', 'ip_address')
    readonly_fields = (
        'consent', 'action', 'old_values', 'new_values', 
        'ip_address', 'user_agent', 'created_at'
    )
    
    fieldsets = (
        ('Log Entry', {
            'fields': ('consent', 'action', 'created_at')
        }),
        ('Changes', {
            'fields': ('old_values', 'new_values')
        }),
        ('Request Info', {
            'fields': ('ip_address', 'user_agent')
        })
    )
    
    def consent_identifier(self, obj):
        """Display consent identifier"""
        consent = obj.consent
        if consent.user:
            return f"User: {consent.user.email}"
        elif consent.session_id:
            return f"Session: {consent.session_id[:8]}..."
        else:
            return f"IP: {consent.ip_address}"
    consent_identifier.short_description = "Consent"
    
    def has_add_permission(self, request):
        """Prevent manual creation of logs"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing of logs"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of logs"""
        return False
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('consent__user')