"""
Unified SEO management command
Handles all SEO operations: sitemaps, monitoring, validation
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
try:
    from core.seo.sitemaps.generator import SitemapGenerator
except ImportError:
    # Fallback for development
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from sitemaps.generator import SitemapGenerator
import requests
import json


class Command(BaseCommand):
    help = 'Manage SEO operations: sitemaps, validation, monitoring'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'operation',
            choices=['status', 'validate', 'ping', 'monitor'],
            help='SEO operation to perform'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )
        parser.add_argument(
            '--format',
            choices=['text', 'json'],
            default='text',
            help='Output format'
        )
    
    def handle(self, *args, **options):
        operation = options['operation']
        verbose = options['verbose']
        output_format = options['format']
        
        if operation == 'status':
            self.show_status(verbose, output_format)
        elif operation == 'validate':
            self.validate_sitemaps(verbose, output_format)
        elif operation == 'ping':
            self.ping_search_engines(verbose, output_format)
        elif operation == 'monitor':
            self.run_monitoring(verbose, output_format)
    
    def show_status(self, verbose=False, output_format='text'):
        """Show SEO system status"""
        stats = SitemapGenerator.get_sitemap_stats()
        
        if output_format == 'json':
            self.stdout.write(json.dumps(stats, indent=2))
            return
        
        self.stdout.write(self.style.SUCCESS('=== SEO System Status ==='))
        self.stdout.write(f"Total Sitemaps: {stats['total_sitemaps']}")
        self.stdout.write(f"Total Size: {stats['total_size_bytes'] / 1024:.1f} KB")
        
        if stats['last_updated']:
            last_updated = timezone.datetime.fromtimestamp(stats['last_updated'])
            self.stdout.write(f"Last Updated: {last_updated}")
        
        if verbose:
            self.stdout.write('\n--- Individual Sitemaps ---')
            for sitemap_type, info in stats['sitemaps'].items():
                size_kb = info['size_bytes'] / 1024
                modified = timezone.datetime.fromtimestamp(info['last_modified'])
                self.stdout.write(
                    f"{sitemap_type:15s} | {size_kb:6.1f} KB | {modified}"
                )
    
    def validate_sitemaps(self, verbose=False, output_format='text'):
        """Validate all sitemap files"""
        validation = SitemapGenerator.validate_all_sitemaps()
        
        if output_format == 'json':
            self.stdout.write(json.dumps(validation, indent=2))
            return
        
        self.stdout.write(self.style.SUCCESS('=== Sitemap Validation ==='))
        
        valid_count = sum(1 for v in validation.values() if v['valid'])
        total_count = len(validation)
        
        self.stdout.write(f"Valid: {valid_count}/{total_count}")
        
        for sitemap_type, result in validation.items():
            if result['valid']:
                status = self.style.SUCCESS('✓ VALID')
            else:
                status = self.style.ERROR('✗ INVALID')
            
            self.stdout.write(f"{sitemap_type:15s} | {status}")
            
            if not result['valid'] and verbose:
                self.stdout.write(f"  Error: {result['error']}")
    
    def ping_search_engines(self, verbose=False, output_format='text'):
        """Ping search engines about sitemap updates"""
        engines = {
            'Google': 'https://www.google.com/ping?sitemap={}',
            'Bing': 'https://www.bing.com/ping?sitemap={}',
            'Yandex': 'https://webmaster.yandex.com/ping?sitemap={}'
        }
        
        sitemap_url = 'https://openlinguify.com/sitemap-index.xml'
        results = {}
        
        if output_format == 'text':
            self.stdout.write(self.style.SUCCESS('=== Pinging Search Engines ==='))
        
        for engine, ping_url in engines.items():
            try:
                response = requests.get(
                    ping_url.format(sitemap_url),
                    timeout=10
                )
                
                success = response.status_code == 200
                results[engine] = {
                    'success': success,
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
                
                if output_format == 'text':
                    if success:
                        status = self.style.SUCCESS('✓ SUCCESS')
                    else:
                        status = self.style.ERROR(f'✗ FAILED ({response.status_code})')
                    
                    response_time = response.elapsed.total_seconds()
                    self.stdout.write(f"{engine:10s} | {status} | {response_time:.2f}s")
                
            except Exception as e:
                results[engine] = {
                    'success': False,
                    'error': str(e)
                }
                
                if output_format == 'text':
                    self.stdout.write(
                        f"{engine:10s} | {self.style.ERROR('✗ ERROR')} | {str(e)}"
                    )
        
        if output_format == 'json':
            self.stdout.write(json.dumps(results, indent=2))
    
    def run_monitoring(self, verbose=False, output_format='text'):
        """Run SEO monitoring and analysis"""
        # This would integrate with the monitoring system
        if output_format == 'text':
            self.stdout.write(self.style.SUCCESS('=== SEO Monitoring ==='))
            self.stdout.write('Monitoring system would run here...')
            # TODO: Integrate with monitoring.analyzer module
        
        results = {
            'timestamp': timezone.now().isoformat(),
            'status': 'monitoring_placeholder'
        }
        
        if output_format == 'json':
            self.stdout.write(json.dumps(results, indent=2))