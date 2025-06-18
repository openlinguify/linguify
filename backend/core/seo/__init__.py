"""
SEO Module for OpenLinguify
Comprehensive SEO management system
"""

__version__ = '1.0.0'
__author__ = 'OpenLinguify Team'

# Export main classes
try:
    from .meta.generator import SEOMetaGenerator
    from .sitemaps.generator import SitemapGenerator
    __all__ = ['SEOMetaGenerator', 'SitemapGenerator']
except ImportError:
    # Fallback if modules not available
    __all__ = []