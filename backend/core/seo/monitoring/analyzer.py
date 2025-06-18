"""
SEO Monitoring and Analytics System
Tracks performance, identifies issues, and provides optimization recommendations
"""

import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.cache import cache
from django.db import models
from datetime import datetime, timedelta
import json
import re
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class SEOMetrics(models.Model):
    """Store SEO metrics for monitoring"""
    url = models.URLField()
    page_title = models.CharField(max_length=200)
    meta_description = models.TextField()
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
        db_table = 'seo_metrics'
        indexes = [
            models.Index(fields=['url', '-crawl_date']),
            models.Index(fields=['score']),
        ]


class SEOMonitor:
    """Monitor and analyze SEO performance"""
    
    IDEAL_TITLE_LENGTH = (30, 60)
    IDEAL_DESCRIPTION_LENGTH = (120, 155)
    MIN_WORD_COUNT = 300
    MAX_LOAD_TIME = 3.0  # seconds
    
    @classmethod
    def analyze_page(cls, url):
        """Analyze a single page for SEO issues"""
        try:
            # Fetch page content
            start_time = timezone.now()
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'OpenLinguify SEO Bot/1.0'
            })
            load_time = (timezone.now() - start_time).total_seconds()
            
            if response.status_code != 200:
                return cls._create_error_metrics(url, f"HTTP {response.status_code}")
            
            # Parse content
            content = response.text
            issues = []
            score = 100
            
            # Extract SEO elements
            title = cls._extract_title(content)
            description = cls._extract_meta_description(content)
            h1_tags = cls._count_tags(content, 'h1')
            h2_tags = cls._count_tags(content, 'h2')
            word_count = cls._count_words(content)
            internal_links, external_links = cls._analyze_links(content, url)
            images_without_alt = cls._check_images(content)
            structured_data = cls._has_structured_data(content)
            canonical = cls._extract_canonical(content)
            robots = cls._extract_robots(content)
            
            # Check for issues
            if not title:
                issues.append("Missing page title")
                score -= 20
            elif len(title) < cls.IDEAL_TITLE_LENGTH[0]:
                issues.append(f"Title too short ({len(title)} chars)")
                score -= 10
            elif len(title) > cls.IDEAL_TITLE_LENGTH[1]:
                issues.append(f"Title too long ({len(title)} chars)")
                score -= 5
            
            if not description:
                issues.append("Missing meta description")
                score -= 15
            elif len(description) < cls.IDEAL_DESCRIPTION_LENGTH[0]:
                issues.append(f"Description too short ({len(description)} chars)")
                score -= 10
            elif len(description) > cls.IDEAL_DESCRIPTION_LENGTH[1]:
                issues.append(f"Description too long ({len(description)} chars)")
                score -= 5
            
            if h1_tags == 0:
                issues.append("Missing H1 tag")
                score -= 15
            elif h1_tags > 1:
                issues.append(f"Multiple H1 tags ({h1_tags})")
                score -= 10
            
            if word_count < cls.MIN_WORD_COUNT:
                issues.append(f"Low word count ({word_count} words)")
                score -= 10
            
            if load_time > cls.MAX_LOAD_TIME:
                issues.append(f"Slow page load ({load_time:.2f}s)")
                score -= 15
            
            if images_without_alt > 0:
                issues.append(f"{images_without_alt} images without alt text")
                score -= min(images_without_alt * 2, 10)
            
            if not structured_data:
                issues.append("No structured data found")
                score -= 5
            
            if internal_links < 3:
                issues.append("Too few internal links")
                score -= 5
            
            # Mobile friendliness check
            mobile_friendly = cls._check_mobile_friendly(content)
            if not mobile_friendly:
                issues.append("Not mobile-friendly")
                score -= 20
            
            # Create metrics object
            metrics = SEOMetrics(
                url=url,
                page_title=title or '',
                meta_description=description or '',
                h1_count=h1_tags,
                h2_count=h2_tags,
                word_count=word_count,
                internal_links=internal_links,
                external_links=external_links,
                images_without_alt=images_without_alt,
                page_load_time=load_time,
                mobile_friendly=mobile_friendly,
                has_structured_data=structured_data,
                canonical_url=canonical,
                robots_directive=robots,
                issues=issues,
                score=max(score, 0)
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing {url}: {str(e)}")
            return cls._create_error_metrics(url, str(e))
    
    @classmethod
    def generate_recommendations(cls, metrics):
        """Generate SEO recommendations based on metrics"""
        recommendations = []
        priority_map = {'high': [], 'medium': [], 'low': []}
        
        # Title recommendations
        if "Missing page title" in metrics.issues:
            priority_map['high'].append({
                'issue': 'Missing page title',
                'recommendation': 'Add a descriptive page title between 30-60 characters',
                'impact': 'Critical for search rankings and click-through rates'
            })
        elif "Title too short" in str(metrics.issues):
            priority_map['medium'].append({
                'issue': 'Title too short',
                'recommendation': 'Expand title to include more keywords (30-60 chars ideal)',
                'impact': 'Better keyword coverage and search visibility'
            })
        
        # Description recommendations
        if "Missing meta description" in metrics.issues:
            priority_map['high'].append({
                'issue': 'Missing meta description',
                'recommendation': 'Add a compelling meta description (120-155 characters)',
                'impact': 'Improves click-through rates from search results'
            })
        
        # Content recommendations
        if metrics.word_count < cls.MIN_WORD_COUNT:
            priority_map['high'].append({
                'issue': 'Low word count',
                'recommendation': f'Expand content to at least {cls.MIN_WORD_COUNT} words',
                'impact': 'Longer content typically ranks better for competitive keywords'
            })
        
        # Performance recommendations
        if metrics.page_load_time > cls.MAX_LOAD_TIME:
            priority_map['high'].append({
                'issue': 'Slow page load',
                'recommendation': 'Optimize images, enable caching, and minify resources',
                'impact': 'Page speed is a ranking factor and affects user experience'
            })
        
        # Technical SEO
        if metrics.images_without_alt > 0:
            priority_map['medium'].append({
                'issue': f'{metrics.images_without_alt} images without alt text',
                'recommendation': 'Add descriptive alt text to all images',
                'impact': 'Improves accessibility and image search rankings'
            })
        
        if not metrics.has_structured_data:
            priority_map['medium'].append({
                'issue': 'No structured data',
                'recommendation': 'Add Schema.org markup for rich snippets',
                'impact': 'Enhances search result appearance and click-through rates'
            })
        
        # Mobile optimization
        if not metrics.mobile_friendly:
            priority_map['high'].append({
                'issue': 'Not mobile-friendly',
                'recommendation': 'Implement responsive design for mobile devices',
                'impact': 'Critical - Google uses mobile-first indexing'
            })
        
        return priority_map
    
    @classmethod
    def _extract_title(cls, html):
        """Extract page title from HTML"""
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else None
    
    @classmethod
    def _extract_meta_description(cls, html):
        """Extract meta description from HTML"""
        match = re.search(
            r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
            html, re.IGNORECASE
        )
        return match.group(1).strip() if match else None
    
    @classmethod
    def _extract_canonical(cls, html):
        """Extract canonical URL from HTML"""
        match = re.search(
            r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']',
            html, re.IGNORECASE
        )
        return match.group(1) if match else None
    
    @classmethod
    def _extract_robots(cls, html):
        """Extract robots meta directive"""
        match = re.search(
            r'<meta\s+name=["\']robots["\']\s+content=["\'](.*?)["\']',
            html, re.IGNORECASE
        )
        return match.group(1) if match else 'index,follow'
    
    @classmethod
    def _count_tags(cls, html, tag):
        """Count occurrences of a specific HTML tag"""
        pattern = f'<{tag}[^>]*>'
        return len(re.findall(pattern, html, re.IGNORECASE))
    
    @classmethod
    def _count_words(cls, html):
        """Count words in visible text"""
        # Remove script and style content
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Count words
        words = text.split()
        return len(words)
    
    @classmethod
    def _analyze_links(cls, html, base_url):
        """Analyze internal and external links"""
        links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE)
        
        internal = 0
        external = 0
        base_domain = urlparse(base_url).netloc
        
        for link in links:
            if link.startswith('http'):
                if base_domain in link:
                    internal += 1
                else:
                    external += 1
            elif link.startswith('/'):
                internal += 1
        
        return internal, external
    
    @classmethod
    def _check_images(cls, html):
        """Check for images without alt text"""
        images = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
        without_alt = 0
        
        for img in images:
            if 'alt=' not in img.lower():
                without_alt += 1
        
        return without_alt
    
    @classmethod
    def _has_structured_data(cls, html):
        """Check if page has structured data"""
        return 'application/ld+json' in html or 'itemscope' in html
    
    @classmethod
    def _check_mobile_friendly(cls, html):
        """Basic mobile-friendliness check"""
        # Check for viewport meta tag
        has_viewport = bool(re.search(
            r'<meta\s+name=["\']viewport["\']',
            html, re.IGNORECASE
        ))
        
        # Check for responsive indicators
        has_responsive = 'responsive' in html.lower() or '@media' in html
        
        return has_viewport or has_responsive
    
    @classmethod
    def _create_error_metrics(cls, url, error):
        """Create metrics object for error cases"""
        return SEOMetrics(
            url=url,
            issues=[f"Error: {error}"],
            score=0
        )


class Command(BaseCommand):
    """Django management command for SEO monitoring"""
    help = 'Run SEO analysis on all pages'
    
    def handle(self, *args, **options):
        # List of URLs to monitor
        urls = [
            'https://www.openlinguify.com/',
            'https://www.openlinguify.com/features/',
            'https://www.openlinguify.com/course/',
            'https://www.openlinguify.com/auth/register/',
        ]
        
        for url in urls:
            self.stdout.write(f"Analyzing {url}...")
            metrics = SEOMonitor.analyze_page(url)
            metrics.save()
            
            # Generate recommendations
            recommendations = SEOMonitor.generate_recommendations(metrics)
            
            self.stdout.write(f"Score: {metrics.score}/100")
            self.stdout.write(f"Issues: {', '.join(metrics.issues)}")
            
            for priority, recs in recommendations.items():
                if recs:
                    self.stdout.write(f"\n{priority.upper()} Priority:")
                    for rec in recs:
                        self.stdout.write(f"  - {rec['recommendation']}")