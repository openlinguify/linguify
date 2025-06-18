#!/usr/bin/env python
"""
Test script to verify SEO module imports work correctly
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

def test_seo_imports():
    """Test all SEO module imports"""
    print("Testing SEO module imports...")
    
    try:
        # Test main SEO module
        from core.seo import SitemapGenerator, SEOMetaGenerator
        print("✓ Main SEO module imports working")
        
        # Test sitemap generator
        from core.seo.sitemaps.generator import SitemapGenerator
        print("✓ Sitemap generator import working")
        
        # Test meta generator
        from core.seo.meta.generator import SEOMetaGenerator
        print("✓ Meta generator import working")
        
        # Test structured data
        from core.seo.meta.structured_data import StructuredDataGenerator
        print("✓ Structured data import working")
        
        # Test middleware
        from core.seo.middleware.optimization import SEOOptimizationMiddleware, PreloadMiddleware
        print("✓ Middleware imports working")
        
        # Test views
        from core.seo.views import serve_sitemap, serve_robots_txt, sitemap_status
        print("✓ Views imports working")
        
        print("\n🎉 All SEO imports are working correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_sitemap_files():
    """Test sitemap file accessibility"""
    print("\nTesting sitemap files...")
    
    try:
        available = SitemapGenerator.list_available_sitemaps()
        print(f"✓ Available sitemaps: {', '.join(available)}")
        
        stats = SitemapGenerator.get_sitemap_stats()
        print(f"✓ Total sitemaps: {stats['total_sitemaps']}")
        print(f"✓ Total size: {stats['total_size_bytes'] / 1024:.1f} KB")
        
        validation = SitemapGenerator.validate_all_sitemaps()
        valid_count = sum(1 for v in validation.values() if v['valid'])
        print(f"✓ Valid sitemaps: {valid_count}/{len(validation)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sitemap test error: {e}")
        return False

if __name__ == "__main__":
    success = True
    success &= test_seo_imports()
    success &= test_sitemap_files()
    
    if success:
        print("\n🚀 SEO system is ready for deployment!")
        sys.exit(0)
    else:
        print("\n💥 SEO system has issues that need fixing")
        sys.exit(1)