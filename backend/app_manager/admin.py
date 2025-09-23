# app_manager/admin.py
import json
from datetime import datetime, timedelta
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponse
from django.utils.html import format_html
from django.contrib import messages
from django.db.models import Count, Q, Avg, Max, Min
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.template.response import TemplateResponse
from .models import App, UserAppSettings, AppDataRetention

User = get_user_model()

@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = [
        'display_name_with_icon', 'code', 'enabled_status', 'category_badge',
        'version', 'total_users', 'active_users_7d', 'order',
        'usage_percentage', 'health_status', 'created_at'
    ]
    list_filter = [
        'is_enabled', 'category', 'version', 'installable',
        'created_at', 'updated_at'
    ]
    search_fields = ['display_name', 'code', 'description', 'category']
    ordering = ['order', 'display_name']
    readonly_fields = [
        'total_users', 'active_users_7d', 'created_at', 'updated_at',
        'manifest_preview', 'usage_analytics'
    ]
    list_per_page = 25
    actions = [
        'enable_selected_apps', 'disable_selected_apps', 'sync_manifest_data',
        'clear_app_cache', 'export_app_analytics'
    ]

    fieldsets = (
        ('📋 Basic Information', {
            'fields': ('code', 'display_name', 'description', 'category', 'version'),
            'classes': ('wide',),
        }),
        ('🎨 Appearance & Navigation', {
            'fields': ('icon_name', 'color', 'route_path'),
            'classes': ('wide',),
        }),
        ('⚙️ Configuration', {
            'fields': ('is_enabled', 'installable', 'order'),
            'classes': ('wide',),
        }),
        ('📊 Usage Analytics', {
            'fields': ('total_users', 'active_users_7d', 'usage_analytics'),
            'classes': ('wide', 'collapse'),
        }),
        ('🔧 Technical Details', {
            'fields': ('manifest_data', 'manifest_preview', 'created_at', 'updated_at'),
            'classes': ('wide', 'collapse'),
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_site.admin_view(self.analytics_view), name='app_manager_app_analytics'),
            path('health-check/', self.admin_site.admin_view(self.health_check_view), name='app_manager_app_health'),
            path('sync-manifests/', self.admin_site.admin_view(self.sync_manifests_view), name='app_manager_sync_manifests'),
            path('export-analytics/', self.admin_site.admin_view(self.export_analytics_view), name='app_manager_export_analytics'),
            path('fix-apps/', self.admin_site.admin_view(self.fix_apps_view), name='app_manager_app_fix_apps'),
            path('fix-apps-action/', self.admin_site.admin_view(self.fix_apps_action), name='app_manager_app_fix_apps_action'),
        ]
        return custom_urls + urls

    # ===== CUSTOM DISPLAY METHODS =====

    def display_name_with_icon(self, obj):
        """Display app name with icon and color indicator"""
        icon_html = f'<span style="color: {obj.color}; margin-right: 8px;">🔗</span>'
        return format_html(
            '{}{}',
            icon_html,
            obj.display_name
        )
    display_name_with_icon.short_description = '📱 Application'
    display_name_with_icon.admin_order_field = 'display_name'

    def enabled_status(self, obj):
        """Enhanced status display with visual indicators"""
        if obj.is_enabled:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✅ Enabled</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">❌ Disabled</span>'
            )
    enabled_status.short_description = '🔋 Status'
    enabled_status.admin_order_field = 'is_enabled'

    def category_badge(self, obj):
        """Display category with colored badge"""
        color_map = {
            'Intelligence IA': '#6c5ce7',
            'Apprentissage': '#fd79a8',
            'Productivité': '#00b894',
            'Communication': '#0984e3',
            'Uncategorized': '#636e72'
        }
        color = color_map.get(obj.category, '#636e72')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            color,
            obj.category
        )
    category_badge.short_description = '🏷️ Category'
    category_badge.admin_order_field = 'category'

    def total_users(self, obj):
        """Get total number of users who have enabled this app"""
        count = obj.enabled_users.count()
        return format_html(
            '<strong style="color: #0984e3;">{}</strong> users',
            count
        )
    total_users.short_description = '👥 Total Users'

    def active_users_7d(self, obj):
        """Get users who were active in the last 7 days"""
        seven_days_ago = timezone.now() - timedelta(days=7)
        count = obj.enabled_users.filter(
            last_login__gte=seven_days_ago
        ).count()
        return format_html(
            '<span style="color: #00b894;">{}</span> active',
            count
        )
    active_users_7d.short_description = '📈 7d Active'

    def usage_percentage(self, obj):
        """Calculate usage percentage among all users"""
        total_users = User.objects.count()
        app_users = obj.enabled_users.count()
        if total_users == 0:
            percentage = 0
        else:
            percentage = (app_users / total_users) * 100

        color = '#28a745' if percentage > 50 else '#ffc107' if percentage > 25 else '#dc3545'
        return format_html(
            '<div style="background: linear-gradient(90deg, {} {}%, #e9ecef {}%); padding: 4px; border-radius: 4px; text-align: center; color: white; font-weight: bold;">{:.1f}%</div>',
            color, percentage, percentage, percentage
        )
    usage_percentage.short_description = '📊 Usage %'

    def health_status(self, obj):
        """App health status based on various metrics"""
        issues = []

        if not obj.is_enabled:
            issues.append('Disabled')
        if not obj.description.strip():
            issues.append('No description')
        if obj.enabled_users.count() == 0:
            issues.append('No users')
        if not obj.route_path:
            issues.append('No route')

        if not issues:
            return format_html('<span style="color: #28a745;">✅ Healthy</span>')
        elif len(issues) == 1:
            return format_html('<span style="color: #ffc107;">⚠️ Warning</span>')
        else:
            return format_html('<span style="color: #dc3545;">❌ Critical</span>')
    health_status.short_description = '🏥 Health'

    def manifest_preview(self, obj):
        """Preview of manifest data"""
        if not obj.manifest_data:
            return format_html('<em>No manifest data</em>')

        preview = json.dumps(obj.manifest_data, indent=2)[:500]
        if len(json.dumps(obj.manifest_data)) > 500:
            preview += "..."

        return format_html('<pre style="font-size: 11px; max-height: 200px; overflow-y: auto;">{}</pre>', preview)
    manifest_preview.short_description = '📄 Manifest Preview'

    def usage_analytics(self, obj):
        """Detailed usage analytics"""
        total_users = User.objects.count()
        app_users = obj.enabled_users.count()
        retention_records = obj.data_retentions.filter(data_deleted=False).count()

        analytics_html = f"""
        <div style="font-size: 12px; line-height: 1.4;">
            <strong>📊 Analytics Summary:</strong><br>
            • Total users who enabled: {app_users}<br>
            • Platform penetration: {(app_users/total_users*100) if total_users > 0 else 0:.1f}%<br>
            • Data retention records: {retention_records}<br>
            • Created: {obj.created_at.strftime('%Y-%m-%d')}<br>
            • Last updated: {obj.updated_at.strftime('%Y-%m-%d %H:%M')}
        </div>
        """
        return format_html(analytics_html)
    usage_analytics.short_description = '📈 Analytics'

    # ===== CUSTOM VIEWS =====

    def analytics_view(self, request):
        """Comprehensive analytics dashboard"""
        apps = App.objects.prefetch_related('enabled_users', 'data_retentions')

        # Calculate overall statistics
        total_apps = apps.count()
        enabled_apps = apps.filter(is_enabled=True).count()
        total_users = User.objects.count()

        # App usage statistics
        app_stats = []
        for app in apps:
            users_count = app.enabled_users.count()
            retention_count = app.data_retentions.filter(data_deleted=False).count()
            app_stats.append({
                'app': app,
                'users_count': users_count,
                'usage_percentage': (users_count / total_users * 100) if total_users > 0 else 0,
                'retention_count': retention_count
            })

        app_stats.sort(key=lambda x: x['users_count'], reverse=True)

        # Category distribution
        category_stats = {}
        for app in apps:
            if app.category not in category_stats:
                category_stats[app.category] = {'count': 0, 'enabled': 0, 'users': 0}
            category_stats[app.category]['count'] += 1
            if app.is_enabled:
                category_stats[app.category]['enabled'] += 1
            category_stats[app.category]['users'] += app.enabled_users.count()

        context = {
            'title': 'App Manager Analytics Dashboard',
            'total_apps': total_apps,
            'enabled_apps': enabled_apps,
            'total_users': total_users,
            'app_stats': app_stats,
            'category_stats': category_stats,
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/app_manager/analytics.html', context)

    def health_check_view(self, request):
        """System health check view"""
        apps = App.objects.all()
        health_issues = []

        for app in apps:
            issues = []
            if not app.is_enabled:
                issues.append('Application disabled')
            if not app.description.strip():
                issues.append('Missing description')
            if app.enabled_users.count() == 0:
                issues.append('No users')
            if not app.route_path:
                issues.append('Missing route path')
            if not app.manifest_data:
                issues.append('No manifest data')

            if issues:
                health_issues.append({
                    'app': app,
                    'issues': issues,
                    'severity': 'critical' if len(issues) > 2 else 'warning'
                })

        context = {
            'title': 'App Manager Health Check',
            'health_issues': health_issues,
            'total_apps': apps.count(),
            'healthy_apps': apps.count() - len(health_issues),
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/app_manager/health_check.html', context)

    def sync_manifests_view(self, request):
        """Sync all app manifests"""
        if request.method == 'POST':
            try:
                summary = App.sync_apps()
                messages.success(
                    request,
                    f"Manifest sync completed: {summary['total_discovered']} apps discovered, "
                    f"{summary['newly_created']} created, {summary['updated']} updated"
                )
            except Exception as e:
                messages.error(request, f"Error syncing manifests: {str(e)}")

            return redirect('admin:app_manager_app_changelist')

        context = {
            'title': 'Sync App Manifests',
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/app_manager/sync_manifests.html', context)

    def export_analytics_view(self, request):
        """Export analytics to CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="app_analytics_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'App Code', 'App Name', 'Category', 'Version', 'Enabled',
            'Total Users', 'Active Users (7d)', 'Usage %', 'Data Retentions',
            'Created', 'Updated'
        ])

        total_users = User.objects.count()
        for app in App.objects.all():
            users_count = app.enabled_users.count()
            active_users = app.enabled_users.filter(
                last_login__gte=timezone.now() - timedelta(days=7)
            ).count()
            retention_count = app.data_retentions.filter(data_deleted=False).count()

            writer.writerow([
                app.code,
                app.display_name,
                app.category,
                app.version,
                'Yes' if app.is_enabled else 'No',
                users_count,
                active_users,
                f"{(users_count/total_users*100) if total_users > 0 else 0:.1f}%",
                retention_count,
                app.created_at.strftime('%Y-%m-%d'),
                app.updated_at.strftime('%Y-%m-%d %H:%M')
            ])

        return response

    # ===== BULK ACTIONS =====

    def enable_selected_apps(self, request, queryset):
        """Enable selected applications"""
        count = queryset.update(is_enabled=True)
        self.message_user(
            request,
            f"✅ Successfully enabled {count} application(s)",
            messages.SUCCESS
        )
    enable_selected_apps.short_description = "🔓 Enable selected applications"

    def disable_selected_apps(self, request, queryset):
        """Disable selected applications"""
        count = queryset.update(is_enabled=False)
        self.message_user(
            request,
            f"🔒 Successfully disabled {count} application(s)",
            messages.SUCCESS
        )
    disable_selected_apps.short_description = "🔒 Disable selected applications"

    def sync_manifest_data(self, request, queryset):
        """Sync manifest data for selected apps"""
        count = 0
        for app in queryset:
            try:
                # Re-discover and update manifest data
                App.discover_apps_from_manifests()
                count += 1
            except Exception as e:
                messages.error(request, f"Error syncing {app.display_name}: {str(e)}")

        if count > 0:
            self.message_user(
                request,
                f"🔄 Successfully synced manifest data for {count} application(s)",
                messages.SUCCESS
            )
    sync_manifest_data.short_description = "🔄 Sync manifest data"

    def clear_app_cache(self, request, queryset):
        """Clear cache for selected apps"""
        count = 0
        for app in queryset:
            cache_keys = [
                f"user_installed_apps_*",
                f"app_data_{app.code}",
                f"app_icons_{app.code}"
            ]
            for pattern in cache_keys:
                cache.delete_many(cache.keys(pattern))
            count += 1

        self.message_user(
            request,
            f"🧹 Successfully cleared cache for {count} application(s)",
            messages.SUCCESS
        )
    clear_app_cache.short_description = "🧹 Clear app cache"

    def export_app_analytics(self, request, queryset):
        """Export analytics for selected apps"""
        # Redirect to the export view with app filter
        app_codes = ','.join(queryset.values_list('code', flat=True))
        return redirect(f'{reverse("admin:app_manager_export_analytics")}?apps={app_codes}')
    export_app_analytics.short_description = "📊 Export analytics"

    # ===== OVERRIDES =====

    def changelist_view(self, request, extra_context=None):
        """Enhanced changelist with additional context"""
        extra_context = extra_context or {}

        # Add dashboard links
        extra_context.update({
            'analytics_url': reverse('admin:app_manager_app_analytics'),
            'health_check_url': reverse('admin:app_manager_app_health'),
            'sync_manifests_url': reverse('admin:app_manager_sync_manifests'),
            'export_url': reverse('admin:app_manager_export_analytics'),
            'fix_apps_url': reverse('admin:app_manager_app_fix_apps'),
        })

        # Add quick stats
        total_apps = App.objects.count()
        enabled_apps = App.objects.filter(is_enabled=True).count()
        total_users = User.objects.count()

        extra_context.update({
            'quick_stats': {
                'total_apps': total_apps,
                'enabled_apps': enabled_apps,
                'disabled_apps': total_apps - enabled_apps,
                'total_users': total_users,
            }
        })

        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        """Optimize queryset with prefetch_related"""
        return super().get_queryset(request).prefetch_related(
            'enabled_users', 'data_retentions'
        )

    # ===== LEGACY METHODS (KEPT FOR COMPATIBILITY) =====

    def fix_apps_view(self, request):
        """Vue pour afficher la page de correction des apps"""
        context = {
            'title': 'Correction des Applications',
            'apps': App.objects.all().order_by('order', 'display_name'),
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request),
        }
        return render(request, 'admin/app_manager/fix_apps.html', context)
    
    def fix_apps_action(self, request):
        """Action pour corriger les apps via AJAX"""
        if not self.has_change_permission(request):
            return JsonResponse({'success': False, 'message': 'Permission refusée'})
        
        try:
            # Logique de correction directe
            app_fixes = {
                'conversation ai': {
                    'display_name': 'Assistant IA',
                    'category': 'Intelligence IA',
                    'description': 'Conversez avec notre IA pour pratiquer la langue et recevoir des corrections personnalisées.',
                    'order': 4,
                },
                'notes': {
                    'display_name': 'Notebook',
                    'category': 'Productivité',
                    'description': 'Prenez des notes intelligentes et organisez votre vocabulaire avec des fonctionnalités avancées.',
                    'order': 1,
                },
                'quiz interactif': {
                    'display_name': 'Quiz',
                    'category': 'Apprentissage',
                    'description': 'Créez et participez à des quiz personnalisés pour tester vos connaissances.',
                    'order': 5,
                },
                'révision': {
                    'display_name': 'Révisions',
                    'category': 'Apprentissage',
                    'description': 'Système de révision avec répétition espacée (Flashcards).',
                    'order': 3,
                }
            }
            
            updated_count = 0
            existing_apps = App.objects.filter(is_enabled=True)
            
            for app in existing_apps:
                app_name_lower = app.display_name.lower()
                if app_name_lower in app_fixes:
                    fixes = app_fixes[app_name_lower]
                    updated = False
                    
                    for key, value in fixes.items():
                        if hasattr(app, key):
                            current_value = getattr(app, key)
                            if current_value != value:
                                setattr(app, key, value)
                                updated = True
                    
                    if updated:
                        app.save()
                        updated_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'{updated_count} applications mises à jour avec succès',
                'updated_count': updated_count
            })
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'})
    
    def changelist_view(self, request, extra_context=None):
        """Ajouter le bouton de correction dans la liste"""
        extra_context = extra_context or {}
        extra_context['fix_apps_url'] = reverse('admin:app_manager_app_fix_apps')
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_object_actions(self, obj):
        """Ajouter des actions personnalisées"""
        return []
    
    def get_list_display_links(self, request, list_display):
        """Personnaliser les liens d'affichage"""
        return super().get_list_display_links(request, list_display)
    
    def response_add(self, request, obj, post_url_continue=None):
        """Personnaliser la réponse après ajout"""
        return super().response_add(request, obj, post_url_continue)
    
    def get_actions(self, request):
        """Ajouter des actions personnalisées"""
        actions = super().get_actions(request)
        if request.user.is_staff:
            actions['fix_apps_action'] = (self.fix_apps_bulk_action, 'fix_apps_action', 'Corriger les applications sélectionnées')
        return actions
    
    def fix_apps_bulk_action(self, request, queryset):
        """Action bulk pour corriger les apps"""
        try:
            from .views import debug_apps
            from django.http import HttpRequest
            
            fake_request = HttpRequest()
            fake_request.method = 'PUT'
            fake_request.user = request.user
            
            response = debug_apps(fake_request)
            
            self.message_user(request, "Applications corrigées avec succès!", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Erreur lors de la correction: {str(e)}", messages.ERROR)
    
    fix_apps_bulk_action.short_description = "🔧 Corriger les applications"

@admin.register(UserAppSettings)
class UserAppSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'user_info', 'enabled_apps_badges', 'apps_count_chart',
        'last_activity', 'user_status', 'engagement_score',
        'custom_order_status', 'created_at'
    ]
    list_filter = [
        'created_at', 'updated_at', 'enabled_apps__category',
        'user__is_active'
    ]
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 'user__last_name',
        'enabled_apps__display_name', 'enabled_apps__code'
    ]
    filter_horizontal = ['enabled_apps']
    readonly_fields = [
        'apps_count_chart', 'user_engagement_analytics', 'app_usage_timeline',
        'created_at', 'updated_at'
    ]
    list_per_page = 30
    actions = [
        'reset_app_order', 'enable_popular_apps', 'sync_default_apps',
        'export_user_settings', 'bulk_app_assignment'
    ]

    fieldsets = (
        ('👤 User Information', {
            'fields': ('user',),
            'classes': ('wide',),
        }),
        ('📱 Enabled Applications', {
            'fields': ('enabled_apps',),
            'classes': ('wide',),
        }),
        ('⚙️ Custom Configuration', {
            'fields': ('app_order',),
            'classes': ('wide',),
        }),
        ('📊 Usage Analytics', {
            'fields': ('apps_count_chart', 'user_engagement_analytics', 'app_usage_timeline'),
            'classes': ('wide', 'collapse'),
        }),
        ('🕒 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('wide', 'collapse'),
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('user-analytics/', self.admin_site.admin_view(self.user_analytics_view), name='app_manager_user_analytics'),
            path('engagement-report/', self.admin_site.admin_view(self.engagement_report_view), name='app_manager_engagement_report'),
            path('bulk-operations/', self.admin_site.admin_view(self.bulk_operations_view), name='app_manager_bulk_operations'),
        ]
        return custom_urls + urls

    # ===== CUSTOM DISPLAY METHODS =====

    def user_info(self, obj):
        """Enhanced user information display"""
        user = obj.user
        status_color = '#28a745' if user.is_active else '#dc3545'
        last_login_info = user.last_login.strftime('%Y-%m-%d') if user.last_login else 'Never'

        return format_html(
            '<div style="line-height: 1.4;">'
            '<strong>{}</strong> ({})<br>'
            '<span style="color: {}; font-size: 11px;">● {}</span><br>'
            '<span style="color: #6c757d; font-size: 11px;">Last login: {}</span>'
            '</div>',
            user.get_full_name() or user.username,
            user.email,
            status_color,
            'Active' if user.is_active else 'Inactive',
            last_login_info
        )
    user_info.short_description = '👤 User Details'
    user_info.admin_order_field = 'user__username'

    def enabled_apps_badges(self, obj):
        """Display enabled apps as colored badges"""
        apps = obj.enabled_apps.all()[:6]  # Show first 6 apps
        badges_html = []

        color_map = {
            'Intelligence IA': '#6c5ce7',
            'Apprentissage': '#fd79a8',
            'Productivité': '#00b894',
            'Communication': '#0984e3',
            'Uncategorized': '#636e72'
        }

        for app in apps:
            color = color_map.get(app.category, '#636e72')
            badges_html.append(
                f'<span style="background-color: {color}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-right: 3px; display: inline-block; margin-bottom: 2px;">{app.display_name[:10]}</span>'
            )

        total_count = obj.enabled_apps.count()
        if total_count > 6:
            badges_html.append(f'<span style="color: #6c757d; font-size: 11px;">+{total_count - 6} more</span>')

        return format_html(''.join(badges_html))
    enabled_apps_badges.short_description = '📱 Enabled Apps'

    def apps_count_chart(self, obj):
        """Visual representation of app count"""
        total_apps = App.objects.filter(is_enabled=True).count()
        user_apps = obj.enabled_apps.count()
        percentage = (user_apps / total_apps * 100) if total_apps > 0 else 0

        color = '#28a745' if percentage > 75 else '#ffc107' if percentage > 50 else '#fd79a8' if percentage > 25 else '#dc3545'

        chart_html = f"""
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 60px; height: 12px; background-color: #e9ecef; border-radius: 6px; overflow: hidden;">
                <div style="width: {percentage}%; height: 100%; background-color: {color}; border-radius: 6px;"></div>
            </div>
            <span style="font-weight: bold; color: {color};">{user_apps}/{total_apps}</span>
            <span style="font-size: 11px; color: #6c757d;">({percentage:.0f}%)</span>
        </div>
        """
        return format_html(chart_html)
    apps_count_chart.short_description = 'Apps Usage'

    def last_activity(self, obj):
        """Show user's last activity"""
        if obj.user.last_login:
            days_ago = (timezone.now() - obj.user.last_login).days
            if days_ago == 0:
                return format_html('<span style="color: #28a745;">🟢 Today</span>')
            elif days_ago <= 7:
                return format_html('<span style="color: #ffc107;">🟡 {} days ago</span>', days_ago)
            elif days_ago <= 30:
                return format_html('<span style="color: #fd79a8;">🟠 {} days ago</span>', days_ago)
            else:
                return format_html('<span style="color: #dc3545;">🔴 {} days ago</span>', days_ago)
        return format_html('<span style="color: #6c757d;">❌ Never</span>')
    last_activity.short_description = '🕒 Last Active'

    def user_status(self, obj):
        """Comprehensive user status"""
        user = obj.user
        apps_count = obj.enabled_apps.count()

        if not user.is_active:
            return format_html('<span style="color: #dc3545;">🔴 Inactive</span>')
        elif apps_count == 0:
            return format_html('<span style="color: #ffc107;">⚠️ No Apps</span>')
        elif user.last_login and (timezone.now() - user.last_login).days <= 7:
            return format_html('<span style="color: #28a745;">✅ Active</span>')
        else:
            return format_html('<span style="color: #fd79a8;">💤 Dormant</span>')
    user_status.short_description = '📊 Status'

    def engagement_score(self, obj):
        """Calculate and display user engagement score"""
        score = 0
        max_score = 100

        # App adoption (40 points max)
        total_apps = App.objects.filter(is_enabled=True).count()
        if total_apps > 0:
            score += (obj.enabled_apps.count() / total_apps) * 40

        # Recent activity (30 points max)
        if obj.user.last_login:
            days_since_login = (timezone.now() - obj.user.last_login).days
            if days_since_login <= 1:
                score += 30
            elif days_since_login <= 7:
                score += 20
            elif days_since_login <= 30:
                score += 10

        # Custom configuration (15 points max)
        if obj.app_order:
            score += 15

        # Profile completeness (15 points max)
        if obj.user.first_name and obj.user.last_name:
            score += 10
        if obj.user.email:
            score += 5

        score = min(score, max_score)
        color = '#28a745' if score > 70 else '#ffc107' if score > 40 else '#dc3545'

        return format_html(
            '<div style="text-align: center;">'
            '<div style="font-weight: bold; color: {};">{:.0f}/100</div>'
            '<div style="font-size: 10px; color: #6c757d;">Engagement</div>'
            '</div>',
            color, score
        )
    engagement_score.short_description = '🎯 Score'

    def custom_order_status(self, obj):
        """Show if user has custom app order"""
        if obj.app_order:
            return format_html(
                '<span style="color: #0984e3;">✅ Custom ({} apps)</span>',
                len(obj.app_order)
            )
        return format_html('<span style="color: #6c757d;">📋 Default</span>')
    custom_order_status.short_description = '🔄 Order'

    def user_engagement_analytics(self, obj):
        """Detailed engagement analytics"""
        user = obj.user
        apps_count = obj.enabled_apps.count()
        total_apps = App.objects.filter(is_enabled=True).count()

        # Calculate metrics
        adoption_rate = (apps_count / total_apps * 100) if total_apps > 0 else 0
        days_since_join = (timezone.now() - user.date_joined).days
        days_since_login = (timezone.now() - user.last_login).days if user.last_login else 'N/A'

        analytics_html = f"""
        <div style="font-size: 12px; line-height: 1.6;">
            <h4 style="margin: 0 0 10px 0; color: #495057;">📊 User Engagement Analytics</h4>
            <table style="width: 100%; font-size: 11px;">
                <tr><td><strong>App Adoption Rate:</strong></td><td>{adoption_rate:.1f}% ({apps_count}/{total_apps})</td></tr>
                <tr><td><strong>Account Age:</strong></td><td>{days_since_join} days</td></tr>
                <tr><td><strong>Last Login:</strong></td><td>{days_since_login} days ago</td></tr>
                <tr><td><strong>Custom Order:</strong></td><td>{'Yes' if obj.app_order else 'No'}</td></tr>
                <tr><td><strong>Settings Updated:</strong></td><td>{obj.updated_at.strftime('%Y-%m-%d %H:%M')}</td></tr>
            </table>
        </div>
        """
        return format_html(analytics_html)
    user_engagement_analytics.short_description = '📈 Engagement Analytics'

    def app_usage_timeline(self, obj):
        """Timeline of app usage"""
        enabled_apps = obj.enabled_apps.all()

        timeline_html = '<div style="font-size: 12px;"><h4 style="margin: 0 0 10px 0;">📅 App Usage Timeline</h4>'

        if enabled_apps:
            for app in enabled_apps[:5]:  # Show first 5 apps
                timeline_html += f'''
                <div style="margin-bottom: 8px; padding: 6px; background-color: #f8f9fa; border-left: 3px solid {app.color};">
                    <strong>{app.display_name}</strong> ({app.category})<br>
                    <small style="color: #6c757d;">Route: {app.route_path}</small>
                </div>
                '''

            if enabled_apps.count() > 5:
                timeline_html += f'<p style="color: #6c757d; font-style: italic;">... and {enabled_apps.count() - 5} more apps</p>'
        else:
            timeline_html += '<p style="color: #6c757d; font-style: italic;">No apps enabled</p>'

        timeline_html += '</div>'
        return format_html(timeline_html)
    app_usage_timeline.short_description = '⏱️ Usage Timeline'

    # ===== CUSTOM VIEWS =====

    def user_analytics_view(self, request):
        """User analytics dashboard"""
        users_with_settings = UserAppSettings.objects.select_related('user').prefetch_related('enabled_apps')

        # Calculate overall metrics
        total_users = User.objects.count()
        users_with_apps = users_with_settings.filter(enabled_apps__isnull=False).distinct().count()
        avg_apps_per_user = users_with_settings.aggregate(
            avg=Avg('enabled_apps')
        )['avg'] or 0

        # User engagement distribution
        engagement_distribution = {'high': 0, 'medium': 0, 'low': 0, 'none': 0}
        for settings in users_with_settings:
            apps_count = settings.enabled_apps.count()
            total_apps = App.objects.filter(is_enabled=True).count()
            percentage = (apps_count / total_apps * 100) if total_apps > 0 else 0

            if percentage > 75:
                engagement_distribution['high'] += 1
            elif percentage > 50:
                engagement_distribution['medium'] += 1
            elif percentage > 0:
                engagement_distribution['low'] += 1
            else:
                engagement_distribution['none'] += 1

        context = {
            'title': 'User App Settings Analytics',
            'total_users': total_users,
            'users_with_apps': users_with_apps,
            'avg_apps_per_user': avg_apps_per_user,
            'engagement_distribution': engagement_distribution,
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/app_manager/user_analytics.html', context)

    def engagement_report_view(self, request):
        """Detailed engagement report"""
        # Implementation for engagement report
        pass

    def bulk_operations_view(self, request):
        """Bulk operations interface"""
        # Implementation for bulk operations
        pass

    # ===== BULK ACTIONS =====

    def reset_app_order(self, request, queryset):
        """Reset custom app order to default"""
        count = queryset.update(app_order=[])
        self.message_user(
            request,
            f"🔄 Reset app order for {count} user(s)",
            messages.SUCCESS
        )
    reset_app_order.short_description = "🔄 Reset app order to default"

    def enable_popular_apps(self, request, queryset):
        """Enable the most popular apps for selected users"""
        popular_apps = App.objects.filter(is_enabled=True).annotate(
            user_count=Count('enabled_users')
        ).order_by('-user_count')[:3]

        count = 0
        for settings in queryset:
            for app in popular_apps:
                settings.enabled_apps.add(app)
            count += 1

        self.message_user(
            request,
            f"📈 Enabled popular apps for {count} user(s)",
            messages.SUCCESS
        )
    enable_popular_apps.short_description = "📈 Enable popular apps"

    def sync_default_apps(self, request, queryset):
        """Sync with default app configuration"""
        # Implementation for syncing default apps
        pass

    def export_user_settings(self, request, queryset):
        """Export user settings to CSV"""
        # Implementation for CSV export
        pass

    def bulk_app_assignment(self, request, queryset):
        """Bulk assign apps to users"""
        # Implementation for bulk assignment
        pass

    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related(
            'user'
        ).prefetch_related(
            'enabled_apps'
        )


@admin.register(AppDataRetention)
class AppDataRetentionAdmin(admin.ModelAdmin):
    list_display = [
        'user_app_info', 'retention_status', 'days_remaining_chart',
        'data_size_estimate', 'disabled_date', 'expiry_alert',
        'retention_actions', 'created_at'
    ]
    list_filter = [
        'data_deleted', 'disabled_at', 'data_expires_at',
        'app__category', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'app__display_name',
        'app__code'
    ]
    readonly_fields = [
        'days_remaining_chart', 'retention_analytics', 'data_cleanup_log',
        'created_at', 'updated_at'
    ]
    list_per_page = 25
    actions = [
        'mark_data_deleted', 'extend_retention_period', 'restore_apps',
        'export_retention_report', 'cleanup_expired_data'
    ]
    date_hierarchy = 'disabled_at'

    fieldsets = (
        ('👤 User & App Information', {
            'fields': ('user', 'app'),
            'classes': ('wide',),
        }),
        ('📅 Retention Timeline', {
            'fields': ('disabled_at', 'data_expires_at', 'data_deleted', 'data_deleted_at'),
            'classes': ('wide',),
        }),
        ('📊 Analytics & Monitoring', {
            'fields': ('days_remaining_chart', 'retention_analytics', 'data_cleanup_log'),
            'classes': ('wide', 'collapse'),
        }),
        ('🕒 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('wide', 'collapse'),
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('retention-dashboard/', self.admin_site.admin_view(self.retention_dashboard_view), name='app_manager_retention_dashboard'),
            path('cleanup-wizard/', self.admin_site.admin_view(self.cleanup_wizard_view), name='app_manager_cleanup_wizard'),
            path('retention-alerts/', self.admin_site.admin_view(self.retention_alerts_view), name='app_manager_retention_alerts'),
        ]
        return custom_urls + urls

    # ===== CUSTOM DISPLAY METHODS =====

    def user_app_info(self, obj):
        """Display user and app information"""
        return format_html(
            '<div style="line-height: 1.4;">'
            '<strong>👤 {}</strong><br>'
            '<span style="color: {}; font-size: 12px;">📱 {}</span><br>'
            '<span style="color: #6c757d; font-size: 11px;">💼 {}</span>'
            '</div>',
            obj.user.get_full_name() or obj.user.username,
            obj.app.color,
            obj.app.display_name,
            obj.app.category
        )
    user_app_info.short_description = '👤 User & App'
    user_app_info.admin_order_field = 'user__username'

    def retention_status(self, obj):
        """Visual retention status"""
        if obj.data_deleted:
            return format_html('<span style="color: #dc3545; font-weight: bold;">🗑️ Deleted</span>')
        elif obj.is_expired:
            return format_html('<span style="color: #fd79a8; font-weight: bold;">⏰ Expired</span>')
        elif obj.days_until_deletion <= 7:
            return format_html('<span style="color: #ffc107; font-weight: bold;">⚠️ Critical</span>')
        elif obj.days_until_deletion <= 14:
            return format_html('<span style="color: #17a2b8; font-weight: bold;">🔔 Warning</span>')
        else:
            return format_html('<span style="color: #28a745; font-weight: bold;">✅ Active</span>')
    retention_status.short_description = '🔋 Status'

    def days_remaining_chart(self, obj):
        """Visual representation of days remaining"""
        if obj.data_deleted:
            return format_html('<span style="color: #dc3545;">🗑️ Data Deleted</span>')

        days_remaining = obj.days_until_deletion
        total_days = 30  # Default retention period

        if days_remaining <= 0:
            percentage = 0
            color = '#dc3545'
            status = 'EXPIRED'
        else:
            percentage = (days_remaining / total_days) * 100
            if percentage > 70:
                color = '#28a745'
            elif percentage > 40:
                color = '#ffc107'
            else:
                color = '#dc3545'
            status = f'{days_remaining}d left'

        chart_html = f"""
        <div style="display: flex; align-items: center; gap: 8px; width: 120px;">
            <div style="width: 60px; height: 8px; background-color: #e9ecef; border-radius: 4px; overflow: hidden;">
                <div style="width: {percentage}%; height: 100%; background-color: {color}; border-radius: 4px;"></div>
            </div>
            <span style="font-size: 11px; font-weight: bold; color: {color};">{status}</span>
        </div>
        """
        return format_html(chart_html)
    days_remaining_chart.short_description = '⏰ Time Left'

    def data_size_estimate(self, obj):
        """Estimate data size for this retention record"""
        # This would need to be implemented based on actual data models
        # For now, we'll show a placeholder
        return format_html(
            '<span style="color: #6c757d; font-size: 11px;">📊 ~{} MB</span>',
            'N/A'  # Placeholder
        )
    data_size_estimate.short_description = '💾 Data Size'

    def disabled_date(self, obj):
        """Formatted disabled date"""
        return format_html(
            '<div style="font-size: 11px;">'
            '<strong>{}</strong><br>'
            '<span style="color: #6c757d;">{}</span>'
            '</div>',
            obj.disabled_at.strftime('%Y-%m-%d'),
            obj.disabled_at.strftime('%H:%M')
        )
    disabled_date.short_description = '📅 Disabled'
    disabled_date.admin_order_field = 'disabled_at'

    def expiry_alert(self, obj):
        """Alert level based on expiry"""
        if obj.data_deleted:
            return format_html('✅')
        elif obj.is_expired:
            return format_html('<span style="color: #dc3545; font-size: 18px;" title="Data has expired!">🚨</span>')
        elif obj.days_until_deletion <= 3:
            return format_html('<span style="color: #fd79a8; font-size: 16px;" title="Expires very soon!">⚡</span>')
        elif obj.days_until_deletion <= 7:
            return format_html('<span style="color: #ffc107; font-size: 14px;" title="Expires soon">⚠️</span>')
        else:
            return format_html('<span style="color: #28a745;" title="Safe">✅</span>')
    expiry_alert.short_description = '🚨'

    def retention_actions(self, obj):
        """Quick action buttons"""
        if obj.data_deleted:
            return format_html('<em style="color: #6c757d;">No actions</em>')

        actions_html = []

        if obj.is_expired:
            actions_html.append(
                '<a href="#" onclick="return false;" style="color: #dc3545; text-decoration: none; margin-right: 8px;" title="Delete Now">🗑️</a>'
            )
        else:
            actions_html.append(
                '<a href="#" onclick="return false;" style="color: #0984e3; text-decoration: none; margin-right: 8px;" title="Extend Retention">⏰</a>'
            )
            actions_html.append(
                '<a href="#" onclick="return false;" style="color: #28a745; text-decoration: none; margin-right: 8px;" title="Restore App">↩️</a>'
            )

        return format_html(''.join(actions_html))
    retention_actions.short_description = '⚡ Actions'

    def retention_analytics(self, obj):
        """Detailed retention analytics"""
        days_since_disabled = (timezone.now() - obj.disabled_at).days
        days_remaining = obj.days_until_deletion

        analytics_html = f"""
        <div style="font-size: 12px; line-height: 1.6;">
            <h4 style="margin: 0 0 10px 0; color: #495057;">📊 Retention Analytics</h4>
            <table style="width: 100%; font-size: 11px;">
                <tr><td><strong>Days since disabled:</strong></td><td>{days_since_disabled}</td></tr>
                <tr><td><strong>Days remaining:</strong></td><td>{days_remaining}</td></tr>
                <tr><td><strong>Expiry date:</strong></td><td>{obj.data_expires_at.strftime('%Y-%m-%d %H:%M')}</td></tr>
                <tr><td><strong>Data deleted:</strong></td><td>{'Yes' if obj.data_deleted else 'No'}</td></tr>
                <tr><td><strong>App category:</strong></td><td>{obj.app.category}</td></tr>
            </table>
        </div>
        """
        return format_html(analytics_html)
    retention_analytics.short_description = '📈 Analytics'

    def data_cleanup_log(self, obj):
        """Log of data cleanup activities"""
        log_html = f"""
        <div style="font-size: 12px;">
            <h4 style="margin: 0 0 10px 0;">📋 Cleanup Log</h4>
            <div style="background-color: #f8f9fa; padding: 8px; border-radius: 4px;">
                <p style="margin: 0;"><strong>Status:</strong> {'Deleted' if obj.data_deleted else 'Pending'}</p>
                {f'<p style="margin: 0;"><strong>Deleted at:</strong> {obj.data_deleted_at.strftime("%Y-%m-%d %H:%M")}</p>' if obj.data_deleted_at else '<p style="margin: 0; color: #6c757d;"><em>No deletion date</em></p>'}
                <p style="margin: 0;"><strong>Created:</strong> {obj.created_at.strftime('%Y-%m-%d %H:%M')}</p>
            </div>
        </div>
        """
        return format_html(log_html)
    data_cleanup_log.short_description = '📋 Cleanup Log'

    # ===== CUSTOM VIEWS =====

    def retention_dashboard_view(self, request):
        """Retention management dashboard"""
        # Calculate statistics
        total_retentions = AppDataRetention.objects.count()
        expired_retentions = AppDataRetention.objects.filter(
            data_expires_at__lte=timezone.now(),
            data_deleted=False
        ).count()

        critical_retentions = AppDataRetention.objects.filter(
            data_expires_at__lte=timezone.now() + timedelta(days=7),
            data_deleted=False
        ).count()

        context = {
            'title': 'Data Retention Dashboard',
            'total_retentions': total_retentions,
            'expired_retentions': expired_retentions,
            'critical_retentions': critical_retentions,
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/app_manager/retention_dashboard.html', context)

    def cleanup_wizard_view(self, request):
        """Data cleanup wizard"""
        # Implementation for cleanup wizard
        pass

    def retention_alerts_view(self, request):
        """Retention alerts and notifications"""
        # Implementation for alerts
        pass

    # ===== BULK ACTIONS =====

    def mark_data_deleted(self, request, queryset):
        """Mark selected records as data deleted"""
        count = 0
        for retention in queryset.filter(data_deleted=False):
            retention.mark_data_deleted()
            count += 1

        self.message_user(
            request,
            f"🗑️ Marked {count} retention record(s) as deleted",
            messages.SUCCESS
        )
    mark_data_deleted.short_description = "🗑️ Mark data as deleted"

    def extend_retention_period(self, request, queryset):
        """Extend retention period by 30 days"""
        count = queryset.filter(data_deleted=False).update(
            data_expires_at=timezone.now() + timedelta(days=30)
        )

        self.message_user(
            request,
            f"⏰ Extended retention for {count} record(s)",
            messages.SUCCESS
        )
    extend_retention_period.short_description = "⏰ Extend retention period"

    def restore_apps(self, request, queryset):
        """Restore apps for users (remove retention records)"""
        count = 0
        for retention in queryset.filter(data_deleted=False):
            # Re-enable the app for the user
            settings, created = UserAppSettings.objects.get_or_create(user=retention.user)
            settings.enabled_apps.add(retention.app)
            retention.delete()
            count += 1

        self.message_user(
            request,
            f"↩️ Restored {count} app(s) for users",
            messages.SUCCESS
        )
    restore_apps.short_description = "↩️ Restore apps to users"

    def export_retention_report(self, request, queryset):
        """Export retention report"""
        # Implementation for export
        pass

    def cleanup_expired_data(self, request, queryset):
        """Cleanup expired data"""
        expired_records = queryset.filter(
            data_expires_at__lte=timezone.now(),
            data_deleted=False
        )
        count = expired_records.count()

        for record in expired_records:
            record.mark_data_deleted()

        self.message_user(
            request,
            f"🧹 Cleaned up {count} expired retention record(s)",
            messages.SUCCESS
        )
    cleanup_expired_data.short_description = "🧹 Cleanup expired data"

    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related(
            'user', 'app'
        )


# ===== GLOBAL APP MANAGER MONITORING =====

class AppManagerMonitoringAdmin:
    """
    Global monitoring class for App Manager system.
    Provides centralized monitoring, alerts, and system health checks.
    """

    @staticmethod
    def get_system_health():
        """Get overall system health metrics"""
        return {
            'apps': {
                'total': App.objects.count(),
                'enabled': App.objects.filter(is_enabled=True).count(),
                'with_users': App.objects.filter(enabled_users__isnull=False).distinct().count(),
                'critical_issues': App.objects.filter(
                    Q(description='') | Q(route_path='') | Q(icon_name='')
                ).count()
            },
            'users': {
                'total': User.objects.count(),
                'with_apps': UserAppSettings.objects.filter(enabled_apps__isnull=False).distinct().count(),
                'active_7d': User.objects.filter(
                    last_login__gte=timezone.now() - timedelta(days=7)
                ).count(),
                'never_logged': User.objects.filter(last_login__isnull=True).count()
            },
            'retention': {
                'total_records': AppDataRetention.objects.count(),
                'expired': AppDataRetention.objects.filter(
                    data_expires_at__lte=timezone.now(),
                    data_deleted=False
                ).count(),
                'critical': AppDataRetention.objects.filter(
                    data_expires_at__lte=timezone.now() + timedelta(days=3),
                    data_deleted=False
                ).count(),
                'deleted': AppDataRetention.objects.filter(data_deleted=True).count()
            }
        }

    @staticmethod
    def get_usage_analytics():
        """Get detailed usage analytics"""
        total_users = User.objects.count()

        # App popularity
        app_popularity = App.objects.annotate(
            user_count=Count('enabled_users')
        ).order_by('-user_count')[:10]

        # User engagement levels
        engagement_levels = {
            'high': 0,      # 75%+ apps enabled
            'medium': 0,    # 50-75% apps enabled
            'low': 0,       # 25-50% apps enabled
            'minimal': 0,   # 1-25% apps enabled
            'none': 0       # 0% apps enabled
        }

        total_apps = App.objects.filter(is_enabled=True).count()
        for settings in UserAppSettings.objects.prefetch_related('enabled_apps'):
            user_apps = settings.enabled_apps.count()
            if total_apps > 0:
                percentage = (user_apps / total_apps) * 100
                if percentage >= 75:
                    engagement_levels['high'] += 1
                elif percentage >= 50:
                    engagement_levels['medium'] += 1
                elif percentage >= 25:
                    engagement_levels['low'] += 1
                elif percentage > 0:
                    engagement_levels['minimal'] += 1
                else:
                    engagement_levels['none'] += 1

        return {
            'app_popularity': app_popularity,
            'engagement_levels': engagement_levels,
            'total_users': total_users,
            'total_apps': total_apps
        }

    @staticmethod
    def get_critical_alerts():
        """Get critical system alerts"""
        alerts = []

        # Check for apps without users
        orphaned_apps = App.objects.filter(
            is_enabled=True,
            enabled_users__isnull=True
        ).distinct()
        if orphaned_apps.exists():
            alerts.append({
                'level': 'warning',
                'type': 'orphaned_apps',
                'message': f'{orphaned_apps.count()} enabled apps have no users',
                'count': orphaned_apps.count()
            })

        # Check for expired data retentions
        expired_retentions = AppDataRetention.objects.filter(
            data_expires_at__lte=timezone.now(),
            data_deleted=False
        )
        if expired_retentions.exists():
            alerts.append({
                'level': 'critical',
                'type': 'expired_data',
                'message': f'{expired_retentions.count()} data retention records have expired',
                'count': expired_retentions.count()
            })

        # Check for critical retention periods
        critical_retentions = AppDataRetention.objects.filter(
            data_expires_at__lte=timezone.now() + timedelta(days=3),
            data_deleted=False
        )
        if critical_retentions.exists():
            alerts.append({
                'level': 'warning',
                'type': 'critical_retention',
                'message': f'{critical_retentions.count()} data retention records expire within 3 days',
                'count': critical_retentions.count()
            })

        # Check for users without apps
        users_no_apps = User.objects.filter(
            is_active=True,
            app_settings__enabled_apps__isnull=True
        ).distinct()
        if users_no_apps.exists():
            alerts.append({
                'level': 'info',
                'type': 'users_no_apps',
                'message': f'{users_no_apps.count()} active users have no apps enabled',
                'count': users_no_apps.count()
            })

        # Check for apps with configuration issues
        problematic_apps = App.objects.filter(
            Q(description='') | Q(route_path='') | Q(icon_name='')
        )
        if problematic_apps.exists():
            alerts.append({
                'level': 'warning',
                'type': 'app_config_issues',
                'message': f'{problematic_apps.count()} apps have configuration issues',
                'count': problematic_apps.count()
            })

        return alerts

    @staticmethod
    def generate_health_report():
        """Generate comprehensive health report"""
        health = AppManagerMonitoringAdmin.get_system_health()
        analytics = AppManagerMonitoringAdmin.get_usage_analytics()
        alerts = AppManagerMonitoringAdmin.get_critical_alerts()

        # Calculate health score
        health_score = 100

        # Deduct points for issues
        if health['apps']['critical_issues'] > 0:
            health_score -= min(20, health['apps']['critical_issues'] * 5)

        if health['retention']['expired'] > 0:
            health_score -= min(30, health['retention']['expired'] * 2)

        if health['users']['never_logged'] > health['users']['total'] * 0.3:
            health_score -= 15

        # Engagement penalty
        total_settings = UserAppSettings.objects.count()
        if total_settings > 0:
            no_apps_ratio = analytics['engagement_levels']['none'] / total_settings
            if no_apps_ratio > 0.5:
                health_score -= 20

        health_score = max(0, health_score)

        return {
            'health_score': health_score,
            'health_status': 'excellent' if health_score >= 90 else 'good' if health_score >= 70 else 'fair' if health_score >= 50 else 'poor',
            'metrics': health,
            'analytics': analytics,
            'alerts': alerts,
            'recommendations': AppManagerMonitoringAdmin._generate_recommendations(health, analytics, alerts)
        }

    @staticmethod
    def _generate_recommendations(health, analytics, alerts):
        """Generate actionable recommendations"""
        recommendations = []

        # App-related recommendations
        if health['apps']['critical_issues'] > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'configuration',
                'title': 'Fix App Configuration Issues',
                'description': f'{health["apps"]["critical_issues"]} apps need configuration fixes (description, routes, icons)',
                'action': 'Review and update app configurations'
            })

        # User engagement recommendations
        if analytics['engagement_levels']['none'] > analytics['total_users'] * 0.3:
            recommendations.append({
                'priority': 'medium',
                'category': 'engagement',
                'title': 'Improve User Engagement',
                'description': f'{analytics["engagement_levels"]["none"]} users have no apps enabled',
                'action': 'Implement onboarding flow or default app assignment'
            })

        # Data retention recommendations
        if health['retention']['expired'] > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'data_management',
                'title': 'Clean Up Expired Data',
                'description': f'{health["retention"]["expired"]} expired data retention records need cleanup',
                'action': 'Run data cleanup process immediately'
            })

        # Performance recommendations
        if health['users']['total'] > 1000 and analytics['total_apps'] > 20:
            recommendations.append({
                'priority': 'low',
                'category': 'performance',
                'title': 'Consider Performance Optimization',
                'description': 'Large user and app base may benefit from caching improvements',
                'action': 'Review and optimize database queries and caching strategies'
            })

        return recommendations


# Register a custom admin site change for better organization
admin.site.site_header = "Linguify App Manager Administration"
admin.site.site_title = "App Manager Admin"
admin.site.index_title = "App Manager Dashboard"

# Add monitoring utilities to admin site
def admin_monitoring_context(request):
    """Add monitoring data to admin context"""
    if request.user.is_staff:
        return {
            'app_manager_health': AppManagerMonitoringAdmin.get_system_health(),
            'app_manager_alerts': AppManagerMonitoringAdmin.get_critical_alerts()[:5],  # Top 5 alerts
        }
    return {}

# You can use this context processor in your admin templates