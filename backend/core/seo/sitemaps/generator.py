"""
Centralized Sitemap Generator
Manages all sitemap types and generation strategies
"""

import os
from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils import timezone
from typing import Dict, List, Optional


class SitemapGenerator:
    """Main sitemap generator and manager"""
    
    SITEMAP_TYPES = {
        'index': 'sitemap-index.xml',
        'main': 'sitemap.xml',
        'static': 'sitemap-static.xml',
        'courses': 'sitemap-courses.xml',
        'learning': 'sitemap-learning.xml',
        'ugc': 'sitemap-ugc.xml',
        'images': 'sitemap-images.xml',
        'videos': 'sitemap-videos.xml',
        'en': 'sitemap-en.xml',
        'fr': 'sitemap-fr.xml',
        'es': 'sitemap-es.xml',
        'nl': 'sitemap-nl.xml',
    }
    
    @classmethod
    def get_sitemap_path(cls, sitemap_type: str) -> str:
        """Get the file path for a sitemap type"""
        filename = cls.SITEMAP_TYPES.get(sitemap_type)
        if not filename:
            raise ValueError(f"Unknown sitemap type: {sitemap_type}")
        
        return os.path.join(
            settings.BASE_DIR,
            'core', 'seo', 'sitemaps', 'static',
            filename
        )
    
    @classmethod
    def serve_sitemap(cls, sitemap_type: str) -> HttpResponse:
        """Serve a sitemap file with proper headers"""
        try:
            file_path = cls.get_sitemap_path(sitemap_type)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            response = HttpResponse(content, content_type='application/xml')
            response['Cache-Control'] = 'public, max-age=3600'  # 1 hour cache
            response['Last-Modified'] = cls._get_last_modified(file_path)
            response['ETag'] = f'"{hash(content)}"'
            
            return response
            
        except FileNotFoundError:
            raise Http404(f"Sitemap {sitemap_type} not found")
    
    @classmethod
    def serve_robots_txt(cls) -> HttpResponse:
        """Serve robots.txt file"""
        try:
            file_path = os.path.join(
                settings.BASE_DIR,
                'core', 'seo', 'sitemaps', 'static',
                'robots.txt'
            )
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            response = HttpResponse(content, content_type='text/plain')
            response['Cache-Control'] = 'public, max-age=86400'  # 24 hours
            
            return response
            
        except FileNotFoundError:
            raise Http404("robots.txt not found")
    
    @classmethod
    def list_available_sitemaps(cls) -> List[str]:
        """List all available sitemap types"""
        available = []
        for sitemap_type in cls.SITEMAP_TYPES.keys():
            try:
                path = cls.get_sitemap_path(sitemap_type)
                if os.path.exists(path):
                    available.append(sitemap_type)
            except (ValueError, FileNotFoundError):
                continue
        return available
    
    @classmethod
    def get_sitemap_stats(cls) -> Dict:
        """Get statistics about all sitemaps"""
        stats = {
            'total_sitemaps': 0,
            'total_size_bytes': 0,
            'sitemaps': {},
            'last_updated': None
        }
        
        for sitemap_type in cls.SITEMAP_TYPES.keys():
            try:
                path = cls.get_sitemap_path(sitemap_type)
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    modified = os.path.getmtime(path)
                    
                    stats['sitemaps'][sitemap_type] = {
                        'size_bytes': size,
                        'last_modified': modified,
                        'filename': cls.SITEMAP_TYPES[sitemap_type]
                    }
                    
                    stats['total_sitemaps'] += 1
                    stats['total_size_bytes'] += size
                    
                    if stats['last_updated'] is None or modified > stats['last_updated']:
                        stats['last_updated'] = modified
                        
            except (ValueError, FileNotFoundError):
                continue
        
        return stats
    
    @classmethod
    def validate_all_sitemaps(cls) -> Dict:
        """Validate all sitemap files"""
        from xml.etree import ElementTree as ET
        
        validation_results = {}
        
        for sitemap_type in cls.SITEMAP_TYPES.keys():
            try:
                path = cls.get_sitemap_path(sitemap_type)
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Basic XML validation
                    try:
                        ET.fromstring(content)
                        validation_results[sitemap_type] = {
                            'valid': True,
                            'error': None,
                            'size': len(content)
                        }
                    except ET.ParseError as e:
                        validation_results[sitemap_type] = {
                            'valid': False,
                            'error': str(e),
                            'size': len(content)
                        }
                        
            except (ValueError, FileNotFoundError) as e:
                validation_results[sitemap_type] = {
                    'valid': False,
                    'error': f"File not found: {str(e)}",
                    'size': 0
                }
        
        return validation_results
    
    @classmethod
    def _get_last_modified(cls, file_path: str) -> str:
        """Get formatted last modified date"""
        try:
            timestamp = os.path.getmtime(file_path)
            return timezone.datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime(
                '%a, %d %b %Y %H:%M:%S GMT'
            )
        except:
            return timezone.now().strftime('%a, %d %b %Y %H:%M:%S GMT')