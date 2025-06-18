"""
Dynamic sitemap generation for OpenLinguify
Supports multi-language URLs and automatic updates
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings
from datetime import datetime
from django.utils import timezone


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'monthly'
    protocol = 'https'
    
    # Define languages supported
    languages = ['en', 'fr', 'es', 'nl']
    
    def items(self):
        # Static pages that should be in the sitemap
        return [
            'frontend_web:landing',
            'frontend_web:features',
            'frontend_web:login',
            'frontend_web:register',
            'frontend_web:terms',
        ]
    
    def location(self, item):
        # Generate URL for each item
        return reverse(item)
    
    def lastmod(self, item):
        # Return last modification date
        return timezone.now()
    
    def priority(self, item):
        # Set priority based on page importance
        priorities = {
            'frontend_web:landing': 1.0,
            'frontend_web:register': 0.9,
            'frontend_web:login': 0.9,
            'frontend_web:features': 0.8,
            'frontend_web:terms': 0.3,
        }
        return priorities.get(item, 0.5)
    
    def changefreq(self, item):
        # Set change frequency based on page type
        frequencies = {
            'frontend_web:landing': 'weekly',
            'frontend_web:features': 'monthly',
            'frontend_web:login': 'monthly',
            'frontend_web:register': 'monthly',
            'frontend_web:terms': 'yearly',
        }
        return frequencies.get(item, 'monthly')


class LearningModuleSitemap(Sitemap):
    """Sitemap for learning modules"""
    priority = 0.7
    changefreq = 'weekly'
    protocol = 'https'
    
    def items(self):
        # Learning module pages
        return [
            'learning:units_list',
            'notebook_web:main',
            'revision_web:main',
        ]
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return timezone.now()


class MultiLanguageSitemap(Sitemap):
    """Base class for multi-language sitemaps with hreflang support"""
    protocol = 'https'
    languages = ['en', 'fr', 'es', 'nl']
    
    def _urls(self, page, protocol, domain):
        urls = []
        for item in self.paginator.page(page).object_list:
            # Generate URL for each language
            for lang in self.languages:
                loc = f"{protocol}://{domain}/{lang}{self.location(item)}"
                priority = self.priority(item)
                url_info = {
                    'item': item,
                    'location': loc,
                    'lastmod': self.lastmod(item),
                    'changefreq': self.changefreq(item),
                    'priority': priority,
                    'alternates': []
                }
                
                # Add hreflang alternates
                for alt_lang in self.languages:
                    if alt_lang != lang:
                        alt_loc = f"{protocol}://{domain}/{alt_lang}{self.location(item)}"
                        url_info['alternates'].append({
                            'lang': alt_lang,
                            'location': alt_loc
                        })
                
                # Add x-default
                url_info['alternates'].append({
                    'lang': 'x-default',
                    'location': f"{protocol}://{domain}{self.location(item)}"
                })
                
                urls.append(url_info)
        
        return urls


# Sitemap configuration dictionary
sitemaps = {
    'static': StaticViewSitemap,
    'learning': LearningModuleSitemap,
}