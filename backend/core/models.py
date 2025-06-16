"""
SEO monitoring models for Django
"""

from django.db import models
from django.utils import timezone
import json


class SitemapLog(models.Model):
    """Log sitemap generation and ping activities"""
    
    ACTION_CHOICES = [
        ('generate', 'Generate'),
        ('ping', 'Ping Search Engines'),
        ('validate', 'Validate'),
        ('compress', 'Compress'),
    ]
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    sitemaps_generated = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'core_sitemap_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['success', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class SitemapGenerationReport(models.Model):
    """Detailed sitemap generation reports"""
    
    generation_date = models.DateTimeField(default=timezone.now)
    total_sitemaps = models.IntegerField(default=0)
    total_urls = models.IntegerField(default=0)
    total_images = models.IntegerField(default=0)
    total_videos = models.IntegerField(default=0)
    file_sizes = models.JSONField(default=dict)  # {sitemap: size_bytes}
    validation_results = models.JSONField(default=dict)  # {sitemap: valid}
    performance_metrics = models.JSONField(default=dict)
    compression_ratios = models.JSONField(default=dict)
    search_engine_pings = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'core_sitemap_generation_report'
        ordering = ['-generation_date']
    
    def __str__(self):
        return f"Report {self.generation_date.strftime('%Y-%m-%d %H:%M')} - {self.total_urls} URLs"
    
    @property
    def total_size_mb(self):
        """Calculate total size in MB"""
        total_bytes = sum(self.file_sizes.values())
        return round(total_bytes / 1024 / 1024, 2)
    
    @property
    def validation_success_rate(self):
        """Calculate validation success rate"""
        if not self.validation_results:
            return 0
        valid_count = sum(1 for v in self.validation_results.values() if v)
        return round(valid_count / len(self.validation_results) * 100, 1)


class SEOPageMetrics(models.Model):
    """Store SEO metrics for individual pages"""
    
    url = models.URLField(max_length=500)
    page_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    h1_count = models.IntegerField(default=0)
    h2_count = models.IntegerField(default=0)
    word_count = models.IntegerField(default=0)
    internal_links = models.IntegerField(default=0)
    external_links = models.IntegerField(default=0)
    images_without_alt = models.IntegerField(default=0)
    page_load_time = models.FloatField(default=0)
    mobile_friendly = models.BooleanField(default=True)
    has_structured_data = models.BooleanField(default=False)
    has_sitemap_entry = models.BooleanField(default=False)
    canonical_url = models.URLField(null=True, blank=True)
    robots_directive = models.CharField(max_length=100, default='index,follow')
    crawl_date = models.DateTimeField(auto_now_add=True)
    issues = models.JSONField(default=list)
    score = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'core_seo_page_metrics'
        indexes = [
            models.Index(fields=['url', '-crawl_date']),
            models.Index(fields=['score']),
            models.Index(fields=['-crawl_date']),
        ]
        unique_together = ['url', 'crawl_date']
    
    def __str__(self):
        return f"{self.url} - Score: {self.score}/100"
    
    @property
    def title_length_status(self):
        """Check title length status"""
        if not self.page_title:
            return 'missing'
        length = len(self.page_title)
        if length < 30:
            return 'too_short'
        elif length > 60:
            return 'too_long'
        return 'optimal'
    
    @property
    def description_length_status(self):
        """Check description length status"""
        if not self.meta_description:
            return 'missing'
        length = len(self.meta_description)
        if length < 120:
            return 'too_short'
        elif length > 155:
            return 'too_long'
        return 'optimal'


class SearchEngineStatus(models.Model):
    """Track search engine crawler status"""
    
    SEARCH_ENGINES = [
        ('google', 'Google'),
        ('bing', 'Bing'),
        ('yandex', 'Yandex'),
        ('duckduckgo', 'DuckDuckGo'),
    ]
    
    engine = models.CharField(max_length=20, choices=SEARCH_ENGINES)
    last_ping_date = models.DateTimeField(null=True, blank=True)
    last_ping_success = models.BooleanField(default=False)
    response_time = models.FloatField(default=0)
    indexed_pages = models.IntegerField(default=0)
    crawl_errors = models.IntegerField(default=0)
    last_crawl_date = models.DateTimeField(null=True, blank=True)
    status_details = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'core_search_engine_status'
        unique_together = ['engine']
    
    def __str__(self):
        return f"{self.get_engine_display()} - {'✓' if self.last_ping_success else '✗'}"


class SystemManagement(models.Model):
    """
    Virtual model for system management interface in Django admin.
    This model doesn't actually store data, it's just used to provide
    an admin interface for system management tasks.
    """
    
    name = models.CharField(max_length=100, default="Gestion Système")
    description = models.TextField(default="Interface de gestion générale du système")
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_system_management'
        verbose_name = 'Gestion Système'
        verbose_name_plural = 'Gestion Système'
        # Ensure only one instance exists
        permissions = [
            ('can_manage_system', 'Can manage system'),
            ('can_run_tests', 'Can run tests'),
            ('can_fix_translations', 'Can fix translations'),
            ('can_check_auth', 'Can check authentication'),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SystemManagement.objects.exists():
            # If trying to create a new instance when one already exists
            return
        super().save(*args, **kwargs)