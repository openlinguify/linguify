"""
Admin interface for SEO monitoring and management
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import SitemapLog, SitemapGenerationReport, SEOPageMetrics, SearchEngineStatus


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