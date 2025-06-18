"""
Admin interface for SEO monitoring and management
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import path, reverse
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib import messages
from django.core.management import call_command
import subprocess
import io
import sys
from .models import SitemapLog, SitemapGenerationReport, SEOPageMetrics, SearchEngineStatus, SystemManagement
from .jobs.admin import *  # Import jobs admin configurations


@admin.register(SitemapLog)
class SitemapLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'sitemaps_generated', 'timestamp', 'success', 'colored_status']
    list_filter = ['action', 'success', 'timestamp']
    search_fields = ['action', 'error_message']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def colored_status(self, obj):
        color = 'green' if obj.success else 'red'
        status = '✓ Success' if obj.success else '✗ Failed'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, status
        )
    colored_status.short_description = 'Status'


@admin.register(SitemapGenerationReport)
class SitemapGenerationReportAdmin(admin.ModelAdmin):
    list_display = [
        'generation_date', 'total_sitemaps', 'total_urls', 
        'total_images', 'total_videos', 'total_size_display', 
        'validation_rate_display'
    ]
    list_filter = ['generation_date']
    readonly_fields = [
        'generation_date', 'total_sitemaps', 'total_urls',
        'total_images', 'total_videos', 'file_sizes',
        'validation_results', 'performance_metrics'
    ]
    ordering = ['-generation_date']
    
    def total_size_display(self, obj):
        return f"{obj.total_size_mb} MB"
    total_size_display.short_description = 'Total Size'
    
    def validation_rate_display(self, obj):
        rate = obj.validation_success_rate
        color = 'green' if rate >= 90 else 'orange' if rate >= 70 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    validation_rate_display.short_description = 'Validation Rate'


@admin.register(SEOPageMetrics)
class SEOPageMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'url', 'page_title', 'score', 'crawl_date',
        'title_status_display', 'description_status_display',
        'issues_count', 'mobile_friendly'
    ]
    list_filter = [
        'mobile_friendly', 'has_structured_data', 
        'has_sitemap_entry', 'crawl_date'
    ]
    search_fields = ['url', 'page_title', 'meta_description']
    readonly_fields = ['crawl_date']
    ordering = ['-score', '-crawl_date']
    
    fieldsets = (
        ('Page Information', {
            'fields': ('url', 'page_title', 'meta_description', 'canonical_url')
        }),
        ('Content Analysis', {
            'fields': (
                'h1_count', 'h2_count', 'word_count',
                'internal_links', 'external_links', 'images_without_alt'
            )
        }),
        ('Technical SEO', {
            'fields': (
                'page_load_time', 'mobile_friendly', 'has_structured_data',
                'has_sitemap_entry', 'robots_directive'
            )
        }),
        ('Performance', {
            'fields': ('score', 'issues', 'crawl_date')
        })
    )
    
    def title_status_display(self, obj):
        status = obj.title_length_status
        colors = {
            'optimal': 'green',
            'too_short': 'orange',
            'too_long': 'red',
            'missing': 'red'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(status, 'black'), status.replace('_', ' ').title()
        )
    title_status_display.short_description = 'Title Status'
    
    def description_status_display(self, obj):
        status = obj.description_length_status
        colors = {
            'optimal': 'green',
            'too_short': 'orange',
            'too_long': 'red',
            'missing': 'red'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(status, 'black'), status.replace('_', ' ').title()
        )
    description_status_display.short_description = 'Description Status'
    
    def issues_count(self, obj):
        count = len(obj.issues)
        color = 'green' if count == 0 else 'orange' if count <= 3 else 'red'
        return format_html(
            '<span style="color: {};">{} issues</span>',
            color, count
        )
    issues_count.short_description = 'Issues'


@admin.register(SearchEngineStatus)
class SearchEngineStatusAdmin(admin.ModelAdmin):
    list_display = [
        'engine', 'last_ping_success_display', 'last_ping_date',
        'response_time_display', 'indexed_pages', 'crawl_errors'
    ]
    list_filter = ['engine', 'last_ping_success']
    readonly_fields = ['last_ping_date', 'last_crawl_date']
    ordering = ['engine']
    
    def last_ping_success_display(self, obj):
        if obj.last_ping_success:
            return format_html('<span style="color: green;">✓ Success</span>')
        else:
            return format_html('<span style="color: red;">✗ Failed</span>')
    last_ping_success_display.short_description = 'Last Ping'
    
    def response_time_display(self, obj):
        if obj.response_time > 0:
            color = 'green' if obj.response_time < 1 else 'orange' if obj.response_time < 3 else 'red'
            return format_html(
                '<span style="color: {};">{:.2f}s</span>',
                color, obj.response_time
            )
        return '-'
    response_time_display.short_description = 'Response Time'


# Custom admin actions
@admin.action(description='Generate fresh sitemaps')
def generate_sitemaps_action(modeladmin, request, queryset):
    """Admin action to generate sitemaps"""
    from django.core.management import call_command
    try:
        call_command('generate_sitemaps', '--ping', '--compress')
        modeladmin.message_user(request, "Sitemaps generated successfully!")
    except Exception as e:
        modeladmin.message_user(request, f"Error generating sitemaps: {str(e)}", level='ERROR')


@admin.action(description='Run SEO analysis')
def run_seo_analysis_action(modeladmin, request, queryset):
    """Admin action to run SEO analysis"""
    from django.core.management import call_command
    try:
        call_command('seo_monitor')
        modeladmin.message_user(request, "SEO analysis completed!")
    except Exception as e:
        modeladmin.message_user(request, f"Error running SEO analysis: {str(e)}", level='ERROR')


# Add actions to relevant admin classes
SitemapLogAdmin.actions = [generate_sitemaps_action]
SEOPageMetricsAdmin.actions = [run_seo_analysis_action]


@admin.register(SystemManagement)
class SystemManagementAdmin(admin.ModelAdmin):
    """
    Admin interface for system management tasks
    """
    list_display = ['name', 'description', 'last_updated']
    readonly_fields = ['last_updated']
    
    # Remove add/delete permissions since this is a virtual model for actions
    def has_add_permission(self, request):
        # Only allow one instance
        return not SystemManagement.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('system-dashboard/', self.admin_site.admin_view(self.system_dashboard_view), name='core_systemmanagement_dashboard'),
            path('fix-translations/', self.admin_site.admin_view(self.fix_translations_view), name='core_systemmanagement_fix_translations'),
            path('run-tests/', self.admin_site.admin_view(self.run_tests_view), name='core_systemmanagement_run_tests'),
            path('check-auth/', self.admin_site.admin_view(self.check_auth_view), name='core_systemmanagement_check_auth'),
            path('system-info/', self.admin_site.admin_view(self.system_info_view), name='core_systemmanagement_system_info'),
            path('execute-command/', self.admin_site.admin_view(self.execute_command_view), name='core_systemmanagement_execute_command'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        """Show system dashboard instead of standard changelist"""
        return self.system_dashboard_view(request)
    
    def system_dashboard_view(self, request):
        """Main system management dashboard"""
        context = {
            'title': 'Gestion Système - Tableau de Bord',
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request),
        }
        return render(request, 'admin/core/system_dashboard.html', context)
    
    def fix_translations_view(self, request):
        """Fix translations interface"""
        if request.method == 'POST':
            return self.execute_command_view(request, 'fix_translations', 
                                          'Correction des traductions', 
                                          ['--fix-encoding-only'])
        
        context = {
            'title': 'Corriger les Traductions',
            'opts': self.model._meta,
            'command_name': 'fix_translations',
            'description': 'Corrige les problèmes d\'encodage et compile les traductions',
        }
        return render(request, 'admin/core/command_interface.html', context)
    
    def run_tests_view(self, request):
        """Run tests interface"""
        if request.method == 'POST':
            app_name = request.POST.get('app_name', '')
            args = []
            if app_name:
                args = [app_name]
            return self.execute_command_view(request, 'test', 'Tests unitaires', args)
        
        # Get list of available apps for testing
        from django.apps import apps
        available_apps = []
        for app_config in apps.get_app_configs():
            if app_config.name.startswith('apps.') or app_config.name in ['core']:
                available_apps.append({
                    'name': app_config.name,
                    'label': app_config.verbose_name or app_config.label
                })
        
        context = {
            'title': 'Lancer les Tests',
            'opts': self.model._meta,
            'command_name': 'test',
            'description': 'Lance les tests unitaires pour une app ou toutes les apps',
            'available_apps': available_apps,
        }
        return render(request, 'admin/core/test_interface.html', context)
    
    def check_auth_view(self, request):
        """Check authentication system"""
        if request.method == 'POST':
            return self.execute_command_view(request, 'check', 
                                          'Vérification du système', 
                                          ['--deploy'])
        
        context = {
            'title': 'Vérifier l\'Authentification',
            'opts': self.model._meta,
            'command_name': 'check',
            'description': 'Vérifie l\'intégrité du système d\'authentification et de la configuration',
        }
        return render(request, 'admin/core/command_interface.html', context)
    
    def system_info_view(self, request):
        """Display system information"""
        try:
            # Get Django version
            import django
            django_version = django.get_version()
            
            # Get Python version
            python_version = sys.version
            
            # Get installed apps count
            from django.apps import apps
            installed_apps = len(apps.get_app_configs())
            
            # Get database info
            from django.db import connection
            db_vendor = connection.vendor
            
            # Get recent logs
            recent_logs = SitemapLog.objects.all()[:5]
            
            context = {
                'title': 'Informations Système',
                'opts': self.model._meta,
                'django_version': django_version,
                'python_version': python_version,
                'installed_apps': installed_apps,
                'db_vendor': db_vendor,
                'recent_logs': recent_logs,
            }
            return render(request, 'admin/core/system_info.html', context)
        except Exception as e:
            messages.error(request, f'Erreur lors de la récupération des informations: {str(e)}')
            return redirect('admin:core_systemmanagement_dashboard')
    
    def execute_command_view(self, request, command_name, command_description, args=None):
        """Execute a Django management command"""
        if not self.has_change_permission(request):
            return JsonResponse({'success': False, 'message': 'Permission refusée'})
        
        try:
            # For test command, use subprocess to avoid threading issues
            if command_name == 'test':
                import subprocess
                from django.conf import settings
                
                # Build command
                cmd = [sys.executable, 'manage.py', 'test']
                if args:
                    cmd.extend(args)
                
                # Execute with subprocess
                result = subprocess.run(
                    cmd,
                    cwd=settings.BASE_DIR,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                output_content = result.stdout
                error_content = result.stderr
                success = result.returncode == 0
                
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({
                        'success': success,
                        'message': f'{command_description} exécuté' + (' avec succès' if success else ' avec des erreurs'),
                        'output': output_content,
                        'errors': error_content
                    })
                else:
                    if not success:
                        messages.error(request, f'Erreurs dans les tests: {error_content}')
                    else:
                        messages.success(request, f'{command_description} exécuté avec succès!')
                    if output_content:
                        messages.info(request, f'Sortie: {output_content[:500]}...' if len(output_content) > 500 else output_content)
                    return redirect('admin:core_systemmanagement_dashboard')
            
            else:
                # For other commands, use call_command
                output = io.StringIO()
                error_output = io.StringIO()
                
                # Execute command
                if args:
                    call_command(command_name, *args, stdout=output, stderr=error_output)
                else:
                    call_command(command_name, stdout=output, stderr=error_output)
                
                output_content = output.getvalue()
                error_content = error_output.getvalue()
                
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({
                        'success': True,
                        'message': f'{command_description} exécuté avec succès',
                        'output': output_content,
                        'errors': error_content
                    })
                else:
                    if error_content:
                        messages.warning(request, f'Avertissements: {error_content}')
                    messages.success(request, f'{command_description} exécuté avec succès!')
                    messages.info(request, f'Sortie: {output_content}')
                    return redirect('admin:core_systemmanagement_dashboard')
                
        except subprocess.TimeoutExpired:
            error_msg = f'Timeout: {command_description} a pris trop de temps (>5min)'
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'success': False, 'message': error_msg})
            else:
                messages.error(request, error_msg)
                return redirect('admin:core_systemmanagement_dashboard')
                
        except Exception as e:
            error_msg = f'Erreur lors de l\'exécution de {command_name}: {str(e)}'
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'success': False, 'message': error_msg})
            else:
                messages.error(request, error_msg)
                return redirect('admin:core_systemmanagement_dashboard')