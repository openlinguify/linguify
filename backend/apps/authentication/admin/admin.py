from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from ..models import User, CoachProfile, Review, UserFeedback, FeedbackAttachment, FeedbackResponse, CookieConsent, CookieConsentLog

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


class NewUsersFilter(admin.SimpleListFilter):
    """Filtre pour voir les nouveaux utilisateurs"""
    title = 'Nouveaux utilisateurs'
    parameter_name = 'new_users'
    
    def lookups(self, request, model_admin):
        return (
            ('today', 'Aujourd\'hui'),
            ('yesterday', 'Hier'),
            ('week', 'Cette semaine'),
            ('month', 'Ce mois'),
            ('online', 'En ligne maintenant'),
        )
    
    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'today':
            return queryset.filter(created_at__date=now.date())
        elif self.value() == 'yesterday':
            yesterday = now.date() - timedelta(days=1)
            return queryset.filter(created_at__date=yesterday)
        elif self.value() == 'week':
            week_ago = now - timedelta(days=7)
            return queryset.filter(created_at__gte=week_ago)
        elif self.value() == 'month':
            month_ago = now - timedelta(days=30)
            return queryset.filter(created_at__gte=month_ago)
        elif self.value() == 'online':
            # Considéré en ligne si dernière activité < 15 minutes
            online_threshold = now - timedelta(minutes=15)
            return queryset.filter(last_login__gte=online_threshold)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'full_name', 'phone_number', 'interface_language', 'acquisition_source', 'online_status', 'new_user_badge', 'terms_accepted', 'is_active', 'is_staff', 'is_superuser', 'is_coach', 'last_login', 'created_at')
    list_filter = (NewUsersFilter, 'how_did_you_hear', 'terms_accepted', 'is_active', 'is_staff', 'is_superuser', 'is_coach', 'created_at')
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
        ('Contact & Profile', {
            'fields': ('phone_number', 'profile_picture', 'bio', 'birthday', 'gender', 'how_did_you_hear'),
        }),
        ('Language Settings', {
            'fields': ('interface_language',),
            'description': 'Language settings for the application interface. Learning language preferences are managed in the Language Learning Profile.'
        }),
        ('Account Deletion', {
            'fields': ('is_pending_deletion', 'deletion_scheduled_at', 'deletion_date'),
            'classes': ('collapse',),
        }),
        ('Terms & Conditions', {
            'fields': ('terms_accepted', 'terms_accepted_at', 'terms_version'),
        }),
        ('Status', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_coach'),
        }),
        ('Learning Preferences', {
            'description': 'Learning preferences are managed via the Language Learning Profile (see related objects below).',
            'fields': (),  # Empty fieldset with description only
        }),
        ('System Information', {
            'fields': ('public_id', 'created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',),
        }),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Name"

    def acquisition_source(self, obj):
        """Display how the user heard about us"""
        if obj.how_did_you_hear:
            # Map values to user-friendly labels
            source_labels = {
                'search_engine': '🔍 Search',
                'social_media': '📱 Social',
                'friend_referral': '👥 Friend',
                'online_ad': '📢 Ad',
                'blog_article': '📝 Blog',
                'app_store': '📲 App Store',
                'school_university': '🎓 School',
                'work_colleague': '💼 Work',
                'other': '❓ Other',
            }
            label = source_labels.get(obj.how_did_you_hear, obj.how_did_you_hear)

            # Add color coding
            color_map = {
                'search_engine': '#4285f4',
                'social_media': '#1877f2',
                'friend_referral': '#28a745',
                'online_ad': '#ff6b6b',
                'blog_article': '#6f42c1',
                'app_store': '#007aff',
                'school_university': '#17a2b8',
                'work_colleague': '#ffc107',
                'other': '#6c757d',
            }
            color = color_map.get(obj.how_did_you_hear, '#6c757d')

            return format_html(
                '<span style="color: {}; font-weight: 500;">{}</span>',
                color, label
            )
        return format_html('<span style="color: #999;">-</span>')
    acquisition_source.short_description = "Source"
    acquisition_source.admin_order_field = 'how_did_you_hear'
    
    # Note: language_info supprimée car les champs ont été déplacés vers UserLearningProfile

    def terms_status(self, obj):
        if obj.terms_accepted:
            accepted_date = obj.terms_accepted_at.strftime('%Y-%m-%d') if obj.terms_accepted_at else 'Unknown date'
            return format_html('<span style="color: green;">✓</span> Accepted ({}, v{})',
                              accepted_date, obj.terms_version or 'n/a')
        return format_html('<span style="color: red;">✗</span> Not accepted')
    terms_status.short_description = "Terms & Conditions"
    
    def online_status(self, obj):
        """Affiche si l'utilisateur est en ligne"""
        if not obj.last_login:
            return format_html('<span style="color: #666;">❌ Jamais connecté</span>')
        
        now = timezone.now()
        online_threshold = now - timedelta(minutes=15)
        
        if obj.last_login >= online_threshold:
            return format_html('<span style="color: #28a745;">🟢 En ligne</span>')
        
        # Calcul du temps depuis dernière connexion
        time_diff = now - obj.last_login
        if time_diff.days > 0:
            return format_html('<span style="color: #dc3545;">🔴 Il y a {} jours</span>', time_diff.days)
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            return format_html('<span style="color: #ffc107;">🟡 Il y a {} heures</span>', hours)
        else:
            minutes = time_diff.seconds // 60
            return format_html('<span style="color: #17a2b8;">🔵 Il y a {} minutes</span>', minutes)
    online_status.short_description = "Statut"
    online_status.admin_order_field = 'last_login'
    
    def new_user_badge(self, obj):
        """Badge pour les nouveaux utilisateurs"""
        if not obj.created_at:
            return '-'
        
        now = timezone.now()
        time_diff = now - obj.created_at
        
        if time_diff.days == 0:
            return format_html('<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">🆕 AUJOURD\'HUI</span>')
        elif time_diff.days == 1:
            return format_html('<span style="background: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">📅 HIER</span>')
        elif time_diff.days <= 7:
            return format_html('<span style="background: #ffc107; color: black; padding: 2px 6px; border-radius: 3px; font-size: 11px;">📆 {} jours</span>', time_diff.days)
        else:
            return '-'
    new_user_badge.short_description = "Nouveau"
    new_user_badge.admin_order_field = 'created_at'
    
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
    
    def changelist_view(self, request, extra_context=None):
        """Ajoute des statistiques au tableau de bord"""
        extra_context = extra_context or {}
        
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        online_threshold = now - timedelta(minutes=15)
        
        # Statistiques des utilisateurs
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        # Nouveaux utilisateurs
        new_today = User.objects.filter(created_at__gte=today_start).count()
        new_yesterday = User.objects.filter(created_at__range=(yesterday_start, today_start)).count()
        new_week = User.objects.filter(created_at__gte=week_start).count()
        new_month = User.objects.filter(created_at__gte=month_start).count()
        
        # Utilisateurs en ligne
        online_now = User.objects.filter(last_login__gte=online_threshold).count()
        
        # Statistiques d'activité
        logged_in_today = User.objects.filter(last_login__gte=today_start).count()
        logged_in_week = User.objects.filter(last_login__gte=week_start).count()
        
        extra_context['user_stats'] = {
            'total_users': total_users,
            'active_users': active_users,
            'new_today': new_today,
            'new_yesterday': new_yesterday,
            'new_week': new_week,
            'new_month': new_month,
            'online_now': online_now,
            'logged_in_today': logged_in_today,
            'logged_in_week': logged_in_week,
        }
        
        return super().changelist_view(request, extra_context)

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

# ============================================================================
# Enhanced Feedback Management System
# ============================================================================

class FeedbackAttachmentInline(admin.TabularInline):
    """Inline for managing feedback attachments"""
    model = FeedbackAttachment
    extra = 0
    fields = ('file', 'filename', 'file_size_display', 'content_type', 'uploaded_at')
    readonly_fields = ('filename', 'file_size_display', 'content_type', 'uploaded_at')

    def file_size_display(self, obj):
        """Display file size in human-readable format"""
        if obj and obj.file_size:
            return obj.get_file_size_display()
        return '-'
    file_size_display.short_description = 'Size'


class FeedbackResponseInline(admin.StackedInline):
    """Inline for managing feedback responses"""
    model = FeedbackResponse
    extra = 0
    fields = ('author', 'message', 'is_internal', 'created_at')
    readonly_fields = ('created_at',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class FeedbackTypeFilter(admin.SimpleListFilter):
    """Custom filter for feedback types"""
    title = 'Feedback Type'
    parameter_name = 'type_filter'

    def lookups(self, request, model_admin):
        return [
            ('bug_report', '🐛 Bug Reports'),
            ('feature_request', '💡 Feature Requests'),
            ('improvement', '⭐ Improvements'),
            ('compliment', '👍 Compliments'),
            ('complaint', '👎 Complaints'),
            ('question', '❓ Questions'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(feedback_type=self.value())
        return queryset


class FeedbackStatusFilter(admin.SimpleListFilter):
    """Custom filter for feedback status"""
    title = 'Status'
    parameter_name = 'status_filter'

    def lookups(self, request, model_admin):
        return [
            ('new', '🆕 New'),
            ('in_progress', '🔄 In Progress'),
            ('resolved', '✅ Resolved'),
            ('closed', '🔒 Closed'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class FeedbackPriorityFilter(admin.SimpleListFilter):
    """Custom filter for feedback priority"""
    title = 'Priority'
    parameter_name = 'priority_filter'

    def lookups(self, request, model_admin):
        return [
            ('critical', '🚨 Critical'),
            ('high', '🔴 High'),
            ('medium', '🟡 Medium'),
            ('low', '🟢 Low'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(priority=self.value())
        return queryset


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    """Comprehensive admin interface for user feedback and bug tracking"""

    list_display = (
        'title_display', 'user_link', 'feedback_type_display', 'category_display',
        'priority_display', 'status_display', 'days_since_created', 'assigned_to_display',
        'responses_count', 'attachments_count'
    )
    list_filter = (
        FeedbackTypeFilter, FeedbackStatusFilter, FeedbackPriorityFilter,
        'category', 'assigned_to', 'created_at', 'resolved_at'
    )
    search_fields = (
        'title', 'user__username', 'user__email', 'user__first_name', 'user__last_name',
        'description', 'admin_notes', 'page_url'
    )
    readonly_fields = (
        'created_at', 'updated_at', 'resolved_at', 'days_since_created',
        'days_since_updated', 'user_info_display', 'technical_info_display',
        'legacy_data_display'
    )

    fieldsets = (
        ('📋 Basic Information', {
            'fields': ('title', 'user_info_display', 'feedback_type', 'category')
        }),
        ('🎯 Priority & Assignment', {
            'fields': ('priority', 'status', 'assigned_to')
        }),
        ('📝 Description & Details', {
            'fields': ('description', 'steps_to_reproduce', 'expected_behavior', 'actual_behavior'),
            'classes': ('wide',)
        }),
        ('💻 Technical Information', {
            'fields': ('technical_info_display', 'page_url', 'screenshot'),
            'classes': ('collapse',)
        }),
        ('👨‍💼 Admin Section', {
            'fields': ('admin_notes',),
            'classes': ('collapse',)
        }),
        ('⏱️ Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at', 'days_since_created', 'days_since_updated'),
            'classes': ('collapse',)
        }),
        ('📁 Legacy Data', {
            'fields': ('legacy_data_display',),
            'classes': ('collapse',),
            'description': 'Legacy fields for backward compatibility - data automatically migrated to new fields.'
        })
    )

    inlines = [FeedbackAttachmentInline, FeedbackResponseInline]

    actions = [
        'mark_as_new', 'mark_as_in_progress', 'mark_as_resolved', 'mark_as_closed',
        'set_priority_high', 'set_priority_critical', 'assign_to_me',
        'export_feedback_report', 'send_user_update'
    ]

    list_per_page = 25
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related"""
        return super().get_queryset(request).select_related(
            'user', 'assigned_to'
        ).prefetch_related(
            'attachments', 'responses'
        )

    # ===== CUSTOM DISPLAY METHODS =====

    def title_display(self, obj):
        """Enhanced title display with type icon"""
        type_icons = {
            'bug_report': '🐛',
            'feature_request': '💡',
            'improvement': '⭐',
            'compliment': '👍',
            'complaint': '👎',
            'question': '❓',
            'other': '📝'
        }
        icon = type_icons.get(obj.feedback_type, '📝')

        # Truncate long titles
        title = obj.title[:60] + '...' if len(obj.title) > 60 else obj.title

        return format_html(
            '{} <strong>{}</strong>',
            icon, title
        )
    title_display.short_description = '📋 Title'
    title_display.admin_order_field = 'title'

    def user_link(self, obj):
        """Enhanced user display with avatar placeholder"""
        url = reverse("admin:authentication_user_change", args=[obj.user.id])
        user_name = obj.user.get_full_name() or obj.user.username

        return format_html(
            '<a href="{}" title="View user details">'
            '👤 <strong>{}</strong><br>'
            '<small style="color: #666;">{}</small>'
            '</a>',
            url, user_name, obj.user.email
        )
    user_link.short_description = '👤 User'
    user_link.admin_order_field = 'user__username'

    def feedback_type_display(self, obj):
        """Display feedback type with color coding"""
        type_colors = {
            'bug_report': '#dc3545',
            'feature_request': '#007bff',
            'improvement': '#28a745',
            'compliment': '#17a2b8',
            'complaint': '#fd7e14',
            'question': '#6f42c1',
            'other': '#6c757d'
        }

        color = type_colors.get(obj.feedback_type, '#6c757d')
        display_name = obj.get_feedback_type_display()

        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, display_name
        )
    feedback_type_display.short_description = '🏷️ Type'
    feedback_type_display.admin_order_field = 'feedback_type'

    def category_display(self, obj):
        """Display category with icon"""
        category_icons = {
            'ui_ux': '🎨',
            'performance': '⚡',
            'functionality': '⚙️',
            'content': '📝',
            'mobile': '📱',
            'desktop': '🖥️',
            'account': '👤',
            'payment': '💳',
            'language_learning': '🎓',
            'other': '📂'
        }

        icon = category_icons.get(obj.category, '📂')
        display_name = obj.get_category_display()

        return format_html(
            '{} {}',
            icon, display_name
        )
    category_display.short_description = '📂 Category'
    category_display.admin_order_field = 'category'

    def priority_display(self, obj):
        """Display priority with color and visual indicator"""
        priority_info = obj.get_priority_display_with_color()
        priority_text = priority_info['priority']
        color = priority_info['color']

        priority_icons = {
            'critical': '🚨',
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }

        icon = priority_icons.get(obj.priority, '⚪')

        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, priority_text
        )
    priority_display.short_description = '🎯 Priority'
    priority_display.admin_order_field = 'priority'

    def status_display(self, obj):
        """Display status with color and progress indicator"""
        status_info = obj.get_status_display_with_color()
        status_text = status_info['status']
        color = status_info['color']

        status_icons = {
            'new': '🆕',
            'in_progress': '🔄',
            'resolved': '✅',
            'closed': '🔒',
            'duplicate': '👯',
            'wont_fix': '❌'
        }

        icon = status_icons.get(obj.status, '❓')

        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, status_text
        )
    status_display.short_description = '📊 Status'
    status_display.admin_order_field = 'status'

    def assigned_to_display(self, obj):
        """Display assigned staff member"""
        if obj.assigned_to:
            url = reverse("admin:authentication_user_change", args=[obj.assigned_to.id])
            name = obj.assigned_to.get_full_name() or obj.assigned_to.username
            return format_html(
                '<a href="{}" title="View staff member">👨‍💼 {}</a>',
                url, name
            )
        return format_html('<span style="color: #6c757d;">⚪ Unassigned</span>')
    assigned_to_display.short_description = '👨‍💼 Assigned To'
    assigned_to_display.admin_order_field = 'assigned_to__username'

    def responses_count(self, obj):
        """Display number of responses"""
        count = obj.responses.count()
        if count > 0:
            public_count = obj.responses.filter(is_internal=False).count()
            internal_count = obj.responses.filter(is_internal=True).count()
            return format_html(
                '<span title="{} public, {} internal responses">💬 {}</span>',
                public_count, internal_count, count
            )
        return format_html('<span style="color: #6c757d;">💬 0</span>')
    responses_count.short_description = '💬 Responses'

    def attachments_count(self, obj):
        """Display number of attachments"""
        count = obj.attachments.count()
        if count > 0:
            return format_html('<span style="color: #007bff;">📎 {}</span>', count)
        return format_html('<span style="color: #6c757d;">📎 0</span>')
    attachments_count.short_description = '📎 Files'

    def user_info_display(self, obj):
        """Display detailed user information"""
        user = obj.user
        return format_html(
            '<div style="line-height: 1.6;">'
            '<h4 style="margin: 0 0 10px 0; color: #495057;">👤 User Information</h4>'
            '<table style="width: 100%; font-size: 12px;">'
            '<tr><td><strong>Name:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Email:</strong></td><td><a href="mailto:{}">{}</a></td></tr>'
            '<tr><td><strong>Username:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Joined:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Last Login:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Active:</strong></td><td>{}</td></tr>'
            '</table>'
            '</div>',
            user.get_full_name() or 'N/A',
            user.email, user.email,
            user.username,
            user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'N/A',
            user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never',
            '✅ Yes' if user.is_active else '❌ No'
        )
    user_info_display.short_description = '👤 User Details'

    def technical_info_display(self, obj):
        """Display technical information"""
        return format_html(
            '<div style="font-size: 12px; line-height: 1.6;">'
            '<h4 style="margin: 0 0 10px 0; color: #495057;">💻 Technical Information</h4>'
            '<table style="width: 100%; font-size: 11px;">'
            '<tr><td><strong>Browser/System:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Page URL:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Has Screenshot:</strong></td><td>{}</td></tr>'
            '</table>'
            '</div>',
            obj.browser_info[:100] + '...' if obj.browser_info and len(obj.browser_info) > 100 else obj.browser_info or 'Not provided',
            f'<a href="{obj.page_url}" target="_blank">{obj.page_url}</a>' if obj.page_url else 'Not provided',
            '✅ Yes' if obj.screenshot else '❌ No'
        )
    technical_info_display.short_description = '💻 Technical Info'

    def legacy_data_display(self, obj):
        """Display legacy data for migration reference"""
        return format_html(
            '<div style="font-size: 12px; line-height: 1.6;">'
            '<h4 style="margin: 0 0 10px 0; color: #495057;">📁 Legacy Data</h4>'
            '<table style="width: 100%; font-size: 11px;">'
            '<tr><td><strong>Legacy Content:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Legacy Date:</strong></td><td>{}</td></tr>'
            '<tr><td><strong>Migration Status:</strong></td><td>✅ Migrated to new fields</td></tr>'
            '</table>'
            '</div>',
            obj.feedback_content[:100] + '...' if obj.feedback_content and len(obj.feedback_content) > 100 else obj.feedback_content or 'None',
            obj.feedback_date.strftime('%Y-%m-%d %H:%M') if obj.feedback_date else 'None'
        )
    legacy_data_display.short_description = '📁 Legacy Data'

    # ===== ADMIN ACTIONS =====

    def mark_as_new(self, request, queryset):
        """Mark selected feedback as new"""
        count = queryset.update(status='new', resolved_at=None)
        self.message_user(request, f'Marked {count} feedback(s) as new.')
    mark_as_new.short_description = '🆕 Mark as new'

    def mark_as_in_progress(self, request, queryset):
        """Mark selected feedback as in progress"""
        count = queryset.update(status='in_progress', resolved_at=None)
        self.message_user(request, f'Marked {count} feedback(s) as in progress.')
    mark_as_in_progress.short_description = '🔄 Mark as in progress'

    def mark_as_resolved(self, request, queryset):
        """Mark selected feedback as resolved"""
        from django.utils import timezone
        count = queryset.filter(status__in=['new', 'in_progress']).update(
            status='resolved', resolved_at=timezone.now()
        )
        self.message_user(request, f'Marked {count} feedback(s) as resolved.')
    mark_as_resolved.short_description = '✅ Mark as resolved'

    def mark_as_closed(self, request, queryset):
        """Mark selected feedback as closed"""
        count = queryset.update(status='closed')
        self.message_user(request, f'Closed {count} feedback(s).')
    mark_as_closed.short_description = '🔒 Mark as closed'

    def set_priority_high(self, request, queryset):
        """Set priority to high"""
        count = queryset.update(priority='high')
        self.message_user(request, f'Set {count} feedback(s) to high priority.')
    set_priority_high.short_description = '🔴 Set priority: High'

    def set_priority_critical(self, request, queryset):
        """Set priority to critical"""
        count = queryset.update(priority='critical')
        self.message_user(request, f'Set {count} feedback(s) to critical priority.')
    set_priority_critical.short_description = '🚨 Set priority: Critical'

    def assign_to_me(self, request, queryset):
        """Assign selected feedback to current user"""
        if request.user.is_staff:
            count = queryset.update(assigned_to=request.user)
            self.message_user(request, f'Assigned {count} feedback(s) to you.')
        else:
            self.message_user(request, 'Only staff members can be assigned feedback.', level='ERROR')
    assign_to_me.short_description = '👨‍💼 Assign to me'

    def export_feedback_report(self, request, queryset):
        """Export detailed feedback report as CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="feedback_report_{timestamp}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Title', 'User Email', 'User Name', 'Type', 'Category', 'Priority', 'Status',
            'Description', 'Page URL', 'Browser Info', 'Assigned To', 'Created At', 'Updated At',
            'Resolved At', 'Days Open', 'Responses Count', 'Attachments Count'
        ])

        for feedback in queryset.select_related('user', 'assigned_to').prefetch_related('responses', 'attachments'):
            days_open = (timezone.now() - feedback.created_at).days if not feedback.resolved_at else (feedback.resolved_at - feedback.created_at).days

            writer.writerow([
                feedback.id,
                feedback.title,
                feedback.user.email,
                feedback.user.get_full_name() or feedback.user.username,
                feedback.get_feedback_type_display(),
                feedback.get_category_display(),
                feedback.get_priority_display(),
                feedback.get_status_display(),
                feedback.description[:500] + '...' if len(feedback.description) > 500 else feedback.description,
                feedback.page_url or '',
                feedback.browser_info[:200] + '...' if feedback.browser_info and len(feedback.browser_info) > 200 else feedback.browser_info or '',
                feedback.assigned_to.get_full_name() if feedback.assigned_to else '',
                feedback.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                feedback.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                feedback.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if feedback.resolved_at else '',
                days_open,
                feedback.responses.count(),
                feedback.attachments.count()
            ])

        return response
    export_feedback_report.short_description = '📊 Export detailed report'

    def send_user_update(self, request, queryset):
        """Send update notification to users (placeholder)"""
        # This would integrate with your notification system
        count = queryset.count()
        self.message_user(
            request,
            f'Would send update notifications for {count} feedback(s) (feature not implemented yet).',
            level='INFO'
        )
    send_user_update.short_description = '📧 Send user updates'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Customize foreign key fields"""
        if db_field.name == "assigned_to":
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to changelist"""
        extra_context = extra_context or {}

        # Get queryset for statistics
        qs = self.get_queryset(request)

        # Calculate statistics
        stats = {
            'total': qs.count(),
            'new': qs.filter(status='new').count(),
            'in_progress': qs.filter(status='in_progress').count(),
            'resolved': qs.filter(status='resolved').count(),
            'closed': qs.filter(status='closed').count(),
            'critical': qs.filter(priority='critical').count(),
            'high': qs.filter(priority='high').count(),
            'bugs': qs.filter(feedback_type='bug_report').count(),
            'features': qs.filter(feedback_type='feature_request').count(),
            'unassigned': qs.filter(assigned_to__isnull=True).count(),
            'with_attachments': qs.filter(attachments__isnull=False).distinct().count(),
        }

        extra_context['feedback_stats'] = stats

        return super().changelist_view(request, extra_context)


@admin.register(FeedbackAttachment)
class FeedbackAttachmentAdmin(admin.ModelAdmin):
    """Admin interface for feedback attachments"""

    list_display = ('feedback_title', 'filename', 'file_size_display', 'content_type', 'uploaded_at')
    list_filter = ('content_type', 'uploaded_at')
    search_fields = ('feedback__title', 'filename', 'feedback__user__email')
    readonly_fields = ('filename', 'file_size', 'content_type', 'uploaded_at')

    def feedback_title(self, obj):
        """Display related feedback title with link"""
        url = reverse("admin:authentication_userfeedback_change", args=[obj.feedback.id])
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.feedback.title[:50] + '...' if len(obj.feedback.title) > 50 else obj.feedback.title
        )
    feedback_title.short_description = 'Feedback'
    feedback_title.admin_order_field = 'feedback__title'

    def file_size_display(self, obj):
        """Display file size in human-readable format"""
        return obj.get_file_size_display()
    file_size_display.short_description = 'Size'
    file_size_display.admin_order_field = 'file_size'


@admin.register(FeedbackResponse)
class FeedbackResponseAdmin(admin.ModelAdmin):
    """Admin interface for feedback responses"""

    list_display = ('feedback_title', 'author', 'message_preview', 'visibility', 'created_at')
    list_filter = ('is_internal', 'author', 'created_at')
    search_fields = ('feedback__title', 'message', 'author__username', 'feedback__user__email')
    readonly_fields = ('created_at',)

    def feedback_title(self, obj):
        """Display related feedback title with link"""
        url = reverse("admin:authentication_userfeedback_change", args=[obj.feedback.id])
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.feedback.title[:50] + '...' if len(obj.feedback.title) > 50 else obj.feedback.title
        )
    feedback_title.short_description = 'Feedback'
    feedback_title.admin_order_field = 'feedback__title'

    def message_preview(self, obj):
        """Display message preview"""
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message'

    def visibility(self, obj):
        """Display visibility status"""
        if obj.is_internal:
            return format_html('<span style="color: #fd7e14;">🔒 Internal</span>')
        else:
            return format_html('<span style="color: #28a745;">👁️ Public</span>')
    visibility.short_description = 'Visibility'
    visibility.admin_order_field = 'is_internal'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Customize foreign key fields"""
        if db_field.name == "author":
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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