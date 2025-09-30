"""
Django management command to generate and optimize sitemaps
Includes compression, caching, and search engine pinging
"""

from django.core.management.base import BaseCommand
from django.contrib.sitemaps import ping_google
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
import gzip
import os
import requests
from xml.etree import ElementTree as ET
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate all sitemaps and ping search engines'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--ping',
            action='store_true',
            help='Ping search engines after generation',
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Generate compressed (.gz) versions',
        )
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Validate sitemap XML structure',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Starting sitemap generation...')
        
        # Clear sitemap cache
        self._clear_sitemap_cache()
        
        # Generate sitemaps
        sitemap_urls = [
            '/sitemap.xml',
            '/sitemap-static.xml',
            '/sitemap-courses.xml',
            '/sitemap-images.xml',
            '/sitemap-videos.xml',
            '/sitemap-index.xml',
        ]
        
        base_url = 'https://www.openlinguify.com'
        generated_sitemaps = []
        
        for sitemap_url in sitemap_urls:
            self.stdout.write(f'Generating {sitemap_url}...')
            
            try:
                # Fetch sitemap content
                response = requests.get(f'{base_url}{sitemap_url}', timeout=30)
                
                if response.status_code == 200:
                    # Save sitemap
                    sitemap_path = os.path.join(
                        settings.BASE_DIR, 
                        f'staticfiles{sitemap_url}'
                    )
                    
                    os.makedirs(os.path.dirname(sitemap_path), exist_ok=True)
                    
                    with open(sitemap_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Validate XML if requested
                    if options['validate']:
                        if self._validate_sitemap(response.content):
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ {sitemap_url} is valid')
                            )
                        else:
                            self.stdout.write(
                                self.style.ERROR(f'✗ {sitemap_url} has XML errors')
                            )
                    
                    # Compress if requested
                    if options['compress']:
                        self._compress_sitemap(sitemap_path, response.content)
                    
                    generated_sitemaps.append(sitemap_url)
                    
                    # Get sitemap stats
                    stats = self._get_sitemap_stats(response.content)
                    self.stdout.write(
                        f'  URLs: {stats["urls"]}, '
                        f'Images: {stats["images"]}, '
                        f'Videos: {stats["videos"]}'
                    )
                    
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Failed to generate {sitemap_url}: '
                            f'HTTP {response.status_code}'
                        )
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error generating {sitemap_url}: {str(e)}')
                )
        
        # Ping search engines if requested
        if options['ping'] and generated_sitemaps:
            self._ping_search_engines(generated_sitemaps)
        
        # Generate summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSitemap generation complete! '
                f'Generated {len(generated_sitemaps)} sitemaps.'
            )
        )
    
    def _clear_sitemap_cache(self):
        """Clear all sitemap-related cache entries"""
        cache_keys = cache.keys('sitemap_*')
        if cache_keys:
            cache.delete_many(cache_keys)
            self.stdout.write(f'Cleared {len(cache_keys)} cache entries')
    
    def _validate_sitemap(self, content):
        """Validate sitemap XML structure"""
        try:
            ET.fromstring(content)
            return True
        except ET.ParseError:
            return False
    
    def _compress_sitemap(self, filepath, content):
        """Create gzip compressed version of sitemap"""
        gz_filepath = f'{filepath}.gz'
        
        with gzip.open(gz_filepath, 'wb') as f:
            f.write(content)
        
        # Calculate compression ratio
        original_size = len(content)
        compressed_size = os.path.getsize(gz_filepath)
        ratio = (1 - compressed_size / original_size) * 100
        
        self.stdout.write(
            f'  Compressed: {original_size} → {compressed_size} bytes '
            f'({ratio:.1f}% reduction)'
        )
    
    def _get_sitemap_stats(self, content):
        """Extract statistics from sitemap"""
        stats = {'urls': 0, 'images': 0, 'videos': 0}
        
        try:
            root = ET.fromstring(content)
            
            # Count URLs
            ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            stats['urls'] = len(root.findall('.//sm:url', ns))
            
            # Count images
            ns_image = {
                'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                'image': 'http://www.google.com/schemas/sitemap-image/1.1'
            }
            stats['images'] = len(root.findall('.//image:image', ns_image))
            
            # Count videos
            ns_video = {
                'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                'video': 'http://www.google.com/schemas/sitemap-video/1.1'
            }
            stats['videos'] = len(root.findall('.//video:video', ns_video))
            
        except:
            pass
        
        return stats
    
    def _ping_search_engines(self, sitemaps):
        """Ping search engines about sitemap updates"""
        engines = {
            'Google': 'https://www.google.com/ping?sitemap=',
            'Bing': 'https://www.bing.com/ping?sitemap=',
            'Yandex': 'https://webmaster.yandex.com/ping?sitemap='
        }
        
        self.stdout.write('\nPinging search engines...')
        
        for sitemap in sitemaps:
            sitemap_url = f'https://www.openlinguify.com{sitemap}'
            
            for engine, ping_url in engines.items():
                try:
                    response = requests.get(
                        f'{ping_url}{sitemap_url}',
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        self.stdout.write(
                            self.style.SUCCESS(f'  ✓ {engine}: {sitemap}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ? {engine}: {sitemap} '
                                f'(HTTP {response.status_code})'
                            )
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ {engine}: {sitemap} ({str(e)})')
                    )
        
        # Log the ping in database for monitoring
        self._log_sitemap_ping(sitemaps)
    
    def _log_sitemap_ping(self, sitemaps):
        """Log sitemap ping to database for monitoring"""
        from core.models import SitemapLog
        
        try:
            log_entry = SitemapLog.objects.create(
                action='ping',
                sitemaps_generated=len(sitemaps),
                timestamp=timezone.now(),
                details={
                    'sitemaps': sitemaps,
                    'user_agent': 'Django Sitemap Generator',
                    'status': 'success'
                }
            )
            self.stdout.write(f'Logged sitemap ping: {log_entry.id}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to log ping: {str(e)}'))
    
    def _generate_detailed_stats(self, sitemaps_data):
        """Generate comprehensive statistics"""
        stats = {
            'total_sitemaps': len(sitemaps_data),
            'total_urls': 0,
            'total_images': 0,
            'total_videos': 0,
            'generation_time': timezone.now(),
            'file_sizes': {},
            'compression_ratios': {},
            'validation_results': {}
        }
        
        for sitemap_path, content in sitemaps_data.items():
            # Calculate file size
            stats['file_sizes'][sitemap_path] = len(content)
            
            # Get URL/image/video counts
            sitemap_stats = self._get_sitemap_stats(content)
            stats['total_urls'] += sitemap_stats['urls']
            stats['total_images'] += sitemap_stats['images']
            stats['total_videos'] += sitemap_stats['videos']
            
            # Validate XML
            stats['validation_results'][sitemap_path] = self._validate_sitemap(content)
        
        return stats
    
    def _save_generation_report(self, stats):
        """Save detailed generation report"""
        from core.models import SitemapGenerationReport
        
        try:
            report = SitemapGenerationReport.objects.create(
                generation_date=stats['generation_time'],
                total_sitemaps=stats['total_sitemaps'],
                total_urls=stats['total_urls'],
                total_images=stats['total_images'],
                total_videos=stats['total_videos'],
                file_sizes=stats['file_sizes'],
                validation_results=stats['validation_results'],
                performance_metrics={
                    'generation_duration': getattr(self, '_generation_duration', 0),
                    'memory_usage': self._get_memory_usage(),
                    'cache_hits': getattr(self, '_cache_hits', 0)
                }
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Generated report: {report.id}')
            )
            return report
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to save report: {str(e)}')
            )
            return None
    
    def _get_memory_usage(self):
        """Get current memory usage"""
        import psutil
        import os
        
        try:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # MB
        except:
            return 0
    
    def _optimize_sitemap_performance(self):
        """Apply performance optimizations"""
        # Warm up cache
        self.stdout.write('Warming up cache...')
        cache.set('sitemap_warmup', True, 300)
        
        # Pre-fetch database queries
        from django.db import connection
        connection.queries_log.clear()
        
        # Set optimal settings for generation
        import gc
        gc.collect()
    
    def _validate_all_sitemaps(self, base_url):
        """Comprehensive sitemap validation"""
        validation_results = {}
        
        sitemaps_to_validate = [
            '/sitemap.xml',
            '/sitemap-index.xml',
            '/sitemap-static.xml',
            '/sitemap-courses.xml',
            '/sitemap-images.xml',
            '/sitemap-videos.xml'
        ]
        
        for sitemap_url in sitemaps_to_validate:
            self.stdout.write(f'Validating {sitemap_url}...')
            
            try:
                response = requests.get(f'{base_url}{sitemap_url}', timeout=30)
                
                if response.status_code == 200:
                    # XML validation
                    xml_valid = self._validate_sitemap(response.content)
                    
                    # Schema validation
                    schema_valid = self._validate_sitemap_schema(response.content)
                    
                    # URL accessibility validation
                    url_checks = self._validate_urls_accessibility(response.content)
                    
                    validation_results[sitemap_url] = {
                        'xml_valid': xml_valid,
                        'schema_valid': schema_valid,
                        'url_accessibility': url_checks,
                        'size_bytes': len(response.content),
                        'encoding': response.encoding
                    }
                    
                    if xml_valid and schema_valid:
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ {sitemap_url} - Valid')
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'✗ {sitemap_url} - Invalid')
                        )
                else:
                    validation_results[sitemap_url] = {
                        'error': f'HTTP {response.status_code}'
                    }
                    
            except Exception as e:
                validation_results[sitemap_url] = {
                    'error': str(e)
                }
        
        return validation_results
    
    def _validate_sitemap_schema(self, content):
        """Validate sitemap against XML schema"""
        try:
            from lxml import etree
            
            # Load sitemap schema
            schema_url = 'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd'
            schema_doc = etree.parse(schema_url)
            schema = etree.XMLSchema(schema_doc)
            
            # Parse and validate sitemap
            sitemap_doc = etree.fromstring(content)
            return schema.validate(sitemap_doc)
            
        except ImportError:
            # Fallback basic validation if lxml not available
            return self._validate_sitemap(content)
        except Exception:
            return False
    
    def _validate_urls_accessibility(self, sitemap_content, sample_size=10):
        """Validate that URLs in sitemap are accessible"""
        try:
            root = ET.fromstring(sitemap_content)
            ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = [url.text for url in root.findall('.//sm:loc', ns)]
            
            # Sample random URLs to check
            import random
            sample_urls = random.sample(urls, min(sample_size, len(urls)))
            
            accessible_count = 0
            for url in sample_urls:
                try:
                    response = requests.head(url, timeout=5)
                    if response.status_code < 400:
                        accessible_count += 1
                except:
                    pass
            
            return {
                'total_checked': len(sample_urls),
                'accessible': accessible_count,
                'accessibility_rate': accessible_count / len(sample_urls) if sample_urls else 0
            }
            
        except Exception:
            return {'error': 'Failed to validate URL accessibility'}
    
    def _monitor_search_engine_status(self):
        """Monitor search engine crawler status"""
        status_urls = {
            'Google': 'https://www.google.com/robots.txt',
            'Bing': 'https://www.bing.com/robots.txt',
            'Yandex': 'https://yandex.com/robots.txt'
        }
        
        crawler_status = {}
        
        for engine, url in status_urls.items():
            try:
                response = requests.get(url, timeout=5)
                crawler_status[engine] = {
                    'available': response.status_code == 200,
                    'response_time': response.elapsed.total_seconds()
                }
            except Exception as e:
                crawler_status[engine] = {
                    'available': False,
                    'error': str(e)
                }
        
        return crawler_status