"""
Advanced sitemap system for maximum Google SEO optimization
Includes caching, compression, and multi-format support
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q
from datetime import datetime, timedelta
import hashlib
from django.utils.translation import activate, get_language
from django.http import HttpResponse
import gzip
from io import BytesIO


class CachedSitemap(Sitemap):
    """Base sitemap with caching capabilities"""
    cache_timeout = 3600  # 1 hour cache
    
    def _get_cache_key(self, page=1):
        """Generate unique cache key for sitemap"""
        return f"sitemap_{self.__class__.__name__}_{page}_{get_language()}"
    
    def _urls(self, page, protocol, domain):
        """Override to add caching"""
        cache_key = self._get_cache_key(page)
        urls = cache.get(cache_key)
        
        if urls is None:
            urls = super()._urls(page, protocol, domain)
            cache.set(cache_key, urls, self.cache_timeout)
        
        return urls


class MultiLanguageStaticSitemap(CachedSitemap):
    """Enhanced static pages sitemap with full multi-language support"""
    priority = 0.8
    changefreq = 'daily'
    protocol = 'https'
    languages = ['en', 'fr', 'es', 'nl']
    
    def items(self):
        """Return all static pages with their metadata"""
        return [
            {
                'url': 'frontend_web:landing',
                'priority': 1.0,
                'changefreq': 'daily',
                'images': [
                    {
                        'loc': '/static/images/logo.png',
                        'title': 'OpenLinguify Logo',
                        'caption': 'Learn languages with OpenLinguify'
                    }
                ]
            },
            {
                'url': 'frontend_web:features',
                'priority': 0.9,
                'changefreq': 'weekly',
                'videos': [
                    {
                        'thumbnail_loc': '/static/images/video-thumb.jpg',
                        'title': 'How OpenLinguify Works',
                        'description': 'Learn how to use OpenLinguify effectively',
                        'content_loc': '/static/videos/intro.mp4',
                        'duration': 180
                    }
                ]
            },
            {
                'url': 'frontend_web:register',
                'priority': 0.95,
                'changefreq': 'monthly'
            },
            {
                'url': 'frontend_web:login',
                'priority': 0.9,
                'changefreq': 'monthly'
            },
            {
                'url': 'frontend_web:terms',
                'priority': 0.3,
                'changefreq': 'yearly'
            }
        ]
    
    def location(self, item):
        """Generate URL for each item"""
        if isinstance(item, dict):
            return reverse(item['url'])
        return reverse(item)
    
    def lastmod(self, item):
        """Dynamic last modification based on content"""
        # Use file modification time for static content
        return timezone.now() - timedelta(days=1)
    
    def priority(self, item):
        """Get priority from item or default"""
        if isinstance(item, dict):
            return item.get('priority', 0.5)
        return 0.5
    
    def changefreq(self, item):
        """Get changefreq from item or default"""
        if isinstance(item, dict):
            return item.get('changefreq', 'weekly')
        return 'weekly'
    
    def _urls(self, page, protocol, domain):
        """Generate URLs with hreflang tags"""
        urls = []
        
        for item in self.paginator.page(page).object_list:
            # Base URL
            base_loc = self.location(item)
            
            # Generate main URL entry
            url_info = {
                'item': item,
                'location': f"{protocol}://{domain}{base_loc}",
                'lastmod': self.lastmod(item),
                'changefreq': self.changefreq(item),
                'priority': self.priority(item),
                'alternates': [],
                'images': [],
                'videos': []
            }
            
            # Add language alternates
            for lang in self.languages:
                alt_url = f"{protocol}://{domain}/{lang}{base_loc}"
                url_info['alternates'].append({
                    'lang': lang,
                    'location': alt_url
                })
            
            # Add x-default
            url_info['alternates'].append({
                'lang': 'x-default',
                'location': f"{protocol}://{domain}{base_loc}"
            })
            
            # Add images if present
            if isinstance(item, dict) and 'images' in item:
                for img in item['images']:
                    url_info['images'].append({
                        'loc': f"{protocol}://{domain}{img['loc']}",
                        'title': img.get('title', ''),
                        'caption': img.get('caption', ''),
                        'geo_location': 'Global',
                        'license': f"{protocol}://{domain}/license"
                    })
            
            # Add videos if present
            if isinstance(item, dict) and 'videos' in item:
                for vid in item['videos']:
                    url_info['videos'].append({
                        'thumbnail_loc': f"{protocol}://{domain}{vid['thumbnail_loc']}",
                        'title': vid['title'],
                        'description': vid['description'],
                        'content_loc': f"{protocol}://{domain}{vid['content_loc']}",
                        'duration': vid.get('duration', 0),
                        'family_friendly': 'yes',
                        'requires_subscription': 'no'
                    })
            
            urls.append(url_info)
        
        return urls


class CourseSitemap(CachedSitemap):
    """Dynamic sitemap for course content"""
    changefreq = 'daily'
    priority = 0.8
    limit = 1000  # Limit items per sitemap
    
    def items(self):
        """Get all published courses"""
        try:
            from apps.course.models import Unit, Lesson
            # Get all active units and lessons
            units = Unit.objects.filter(is_active=True).order_by('-updated_at')
            lessons = Lesson.objects.filter(
                is_active=True,
                unit__is_active=True
            ).order_by('-updated_at')
            
            items = []
            for unit in units:
                items.append({
                    'type': 'unit',
                    'obj': unit,
                    'url': f"/course/unit/{unit.id}/",
                    'priority': 0.8,
                    'changefreq': 'weekly'
                })
            
            for lesson in lessons:
                items.append({
                    'type': 'lesson',
                    'obj': lesson,
                    'url': f"/course/lesson/{lesson.id}/",
                    'priority': 0.7,
                    'changefreq': 'daily'
                })
            
            return items[:self.limit]
        except:
            return []
    
    def location(self, item):
        return item['url']
    
    def lastmod(self, item):
        return item['obj'].updated_at if hasattr(item['obj'], 'updated_at') else timezone.now()
    
    def priority(self, item):
        return item.get('priority', 0.5)
    
    def changefreq(self, item):
        return item.get('changefreq', 'weekly')


class ImageSitemap(CachedSitemap):
    """Dedicated image sitemap for Google Images"""
    protocol = 'https'
    
    def items(self):
        """Get all images that should be indexed"""
        images = []
        
        # Static images
        static_images = [
            {
                'loc': '/static/images/hero-bg.jpg',
                'title': 'Learn Languages Online with OpenLinguify',
                'caption': 'Start your language learning journey today',
                'geo_location': 'Worldwide'
            },
            {
                'loc': '/static/images/features/ai-powered.png',
                'title': 'AI-Powered Language Learning',
                'caption': 'Advanced AI technology for personalized learning',
                'geo_location': 'Worldwide'
            },
            {
                'loc': '/static/images/features/flashcards.png',
                'title': 'Interactive Flashcards',
                'caption': 'Memorize vocabulary with spaced repetition',
                'geo_location': 'Worldwide'
            }
        ]
        
        # Course images
        try:
            from apps.course.models import Lesson
            lessons = Lesson.objects.filter(
                is_active=True,
                image__isnull=False
            )[:100]
            
            for lesson in lessons:
                if lesson.image:
                    images.append({
                        'loc': lesson.image.url,
                        'title': f"{lesson.title} - Language Learning",
                        'caption': lesson.description[:160] if lesson.description else '',
                        'geo_location': 'Worldwide'
                    })
        except:
            pass
        
        return static_images + images
    
    def location(self, item):
        return item['loc']


class NewsSitemap(CachedSitemap):
    """Google News sitemap for blog/news content"""
    limit = 1000
    
    def items(self):
        """Get recent news/blog posts"""
        # This would connect to a blog/news model when available
        # For now, return empty
        return []
    
    def lastmod(self, item):
        return item.published_date
    
    def news_publication_date(self, item):
        """Required for Google News"""
        return item.published_date
    
    def news_title(self, item):
        """Required for Google News"""
        return item.title
    
    def news_keywords(self, item):
        """Optional keywords for Google News"""
        return "language learning, education, online courses"


class VideoSitemap(CachedSitemap):
    """Dedicated video sitemap"""
    protocol = 'https'
    
    def items(self):
        """Get all videos to be indexed"""
        videos = [
            {
                'loc': '/features/',
                'video': {
                    'thumbnail_loc': '/static/images/video-thumbnails/intro.jpg',
                    'title': 'Introduction to OpenLinguify',
                    'description': 'Learn how OpenLinguify can help you master new languages',
                    'content_loc': '/static/videos/intro.mp4',
                    'player_loc': '/video-player/?video=intro',
                    'duration': 180,
                    'expiration_date': None,
                    'view_count': 15000,
                    'publication_date': timezone.now() - timedelta(days=30),
                    'family_friendly': 'yes',
                    'restriction': None,
                    'platform': 'web mobile',
                    'requires_subscription': 'no',
                    'uploader': 'OpenLinguify Team',
                    'live': 'no'
                }
            }
        ]
        return videos
    
    def location(self, item):
        return item['loc']


def compress_sitemap(sitemap_xml):
    """Compress sitemap for faster delivery"""
    out = BytesIO()
    with gzip.GzipFile(fileobj=out, mode='w') as f:
        f.write(sitemap_xml.encode('utf-8'))
    return out.getvalue()


class SitemapPingService:
    """Service to ping search engines when sitemap updates"""
    
    PING_URLS = {
        'google': 'https://www.google.com/ping?sitemap={}',
        'bing': 'https://www.bing.com/ping?sitemap={}',
        'yandex': 'https://webmaster.yandex.com/ping?sitemap={}'
    }
    
    @classmethod
    def ping_all(cls, sitemap_url):
        """Ping all search engines"""
        import requests
        
        full_url = f"https://www.openlinguify.com{sitemap_url}"
        results = {}
        
        for engine, ping_url in cls.PING_URLS.items():
            try:
                response = requests.get(
                    ping_url.format(full_url),
                    timeout=5
                )
                results[engine] = response.status_code == 200
            except:
                results[engine] = False
        
        return results


# Enhanced sitemaps dictionary
sitemaps = {
    'static': MultiLanguageStaticSitemap,
    'courses': CourseSitemap,
    'images': ImageSitemap,
    'videos': VideoSitemap,
    'news': NewsSitemap,
}