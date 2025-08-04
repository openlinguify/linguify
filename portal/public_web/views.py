"""
Public Web Views for Open Linguify
Handles public-facing pages, SEO, and dynamic app content
"""
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse
from django.core.cache import cache
from django.utils.cache import get_cache_key
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.core.mail import send_mail
from datetime import datetime, timedelta
import logging

from .utils import manifest_parser

logger = logging.getLogger(__name__)


class BaseSEOView(TemplateView):
    """Base view for SEO-optimized pages with caching"""
    
    # Override in subclasses
    page_title = "Open Linguify"
    meta_description = "Open source educational platform"
    meta_keywords = "openlinguify, open linguify, education"
    cache_timeout = 300  # 5 minutes default
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.get_page_title(),
            'meta_description': self.get_meta_description(),
            'meta_keywords': self.get_meta_keywords(),
            'canonical_url': self.get_canonical_url(),
        })
        return context
    
    def get_page_title(self):
        """Get the page title, can be overridden for dynamic titles"""
        return _(self.page_title)
    
    def get_meta_description(self):
        """Get the meta description, can be overridden for dynamic descriptions"""
        return _(self.meta_description)
    
    def get_meta_keywords(self):
        """Get the meta keywords"""
        return _(self.meta_keywords)
    
    def get_canonical_url(self):
        """Get canonical URL for SEO"""
        return self.request.build_absolute_uri(self.request.path)


class LandingView(BaseSEOView):
    """Page d'accueil publique optimisée - Portail Linguify"""
    template_name = 'public_web/landing.html'
    page_title = 'OpenLinguify - Learn languages with AI-powered tools'
    meta_description = 'OpenLinguify (openlinguify) - Open source platform for learning languages with AI tutors, flashcards, interactive quizzes and more.'
    meta_keywords = 'openlinguify, open linguify, language learning platform, AI tutors, flashcards, education'
    
    def get(self, request):
        # Pas de redirection automatique sur le portail
        # Les utilisateurs doivent choisir leur produit
        
        # Récupérer la configuration des produits
        products = []
        for key, product in settings.LINGUIFY_PRODUCTS.items():
            product_data = product.copy()
            product_data['key'] = key
            # Utiliser l'URL de dev ou prod selon DEBUG
            product_data['url'] = product['dev_url'] if settings.DEBUG else product['prod_url']
            products.append(product_data)
        
        # Cache key pour les données de la landing page
        cache_key = f'landing_apps_{request.LANGUAGE_CODE}'
        featured_apps = cache.get(cache_key)
        
        if featured_apps is None:
            # Récupérer les applications principales pour la landing
            try:
                all_apps = manifest_parser.get_public_apps()
                featured_apps = sorted(all_apps, key=lambda x: x.get('menu_order', 999))[:4]
                cache.set(cache_key, featured_apps, 300)  # Cache 5 minutes
            except Exception as e:
                logger.warning(f"Failed to load apps for landing page: {e}")
                featured_apps = []
        
        context = self.get_context_data()
        context['featured_apps'] = featured_apps
        context['products'] = products
        
        return render(request, self.template_name, context)


@method_decorator([
    cache_page(300),  # Cache 5 minutes
    vary_on_headers('Accept-Language')
], name='dispatch')
class FeaturesView(BaseSEOView):
    """Page des fonctionnalités avec cache"""
    template_name = 'public_web/features.html'
    page_title = 'Features - Open Linguify Educational Platform'
    meta_description = 'Discover all Open Linguify features: AI-powered conversations, smart flashcards, interactive quizzes, note-taking and more.'
    meta_keywords = 'features, AI tutors, flashcards, quizzes, language learning, education tools'


@method_decorator([
    cache_page(600),  # Cache 10 minutes
    vary_on_headers('Accept-Language')
], name='dispatch')
class AboutView(BaseSEOView):
    """Page à propos avec cache"""
    template_name = 'public_web/about.html'
    page_title = 'About - Open Linguify Open Source Educational Platform'
    meta_description = 'Learn about Open Linguify, the open source educational platform revolutionizing language learning with AI technology.'
    meta_keywords = 'about, open source, educational platform, language learning, AI technology'


@method_decorator([
    cache_page(300),
    vary_on_headers('Accept-Language')
], name='dispatch')

class ContactView(BaseSEOView):
    """Page contact sans cache (peut contenir des formulaires)"""
    template_name = 'public_web/contact.html'
    page_title = 'Contact - Open Linguify Support & Information'
    meta_description = 'Contact the Open Linguify team for support, partnerships, or questions about our educational platform.'
    meta_keywords = 'contact, support, partnerships, help, customer service'


class ReportBugView(View):
    """Page pour signaler un bug avec envoi d'email"""
    
    def get(self, request):
        context = {
            'title': _('Report a Bug - Open Linguify'),
            'meta_description': _('Report bugs and issues with Open Linguify platform to help us improve your experience.'),
            'meta_keywords': _('bug report, issues, support, help, feedback'),
        }
        return render(request, 'public_web/report_bug.html', context)
    
    def post(self, request):
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        url = request.POST.get('url', '').strip()
        browser = request.POST.get('browser', '').strip()
        
        if not all([name, email, subject, description]):
            context = {
                'title': _('Report a Bug - Open Linguify'),
                'error': _('Please fill in all required fields.'),
                'name': name,
                'email': email,
                'subject': subject,
                'description': description,
                'url': url,
                'browser': browser,
            }
            return render(request, 'public_web/report_bug.html', context)
        
        try:
            email_subject = f'[Bug Report] {subject}'
            email_body = f"""
New bug report from Open Linguify:

Name: {name}
Email: {email}
Subject: {subject}

Description:
{description}

Additional Information:
URL: {url or 'Not provided'}
Browser: {browser or 'Not provided'}
User IP: {request.META.get('REMOTE_ADDR', 'Unknown')}
User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            send_mail(
                subject=email_subject,
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['louisphilippelalou@outlook.com'],
                fail_silently=False,
            )
            
            context = {
                'title': _('Bug Report Sent - Open Linguify'),
                'success': _('Thank you for your bug report. We will review it and get back to you if needed.'),
            }
            return render(request, 'public_web/report_bug.html', context)
            
        except Exception as e:
            logger.error(f"Failed to send bug report email: {e}")
            context = {
                'title': _('Report a Bug - Open Linguify'),
                'error': _('An error occurred while sending your report. Please try again later.'),
                'name': name,
                'email': email,
                'subject': subject,
                'description': description,
                'url': url,
                'browser': browser,
            }
            return render(request, 'public_web/report_bug.html', context)


# Legal Pages - Cache plus long car rarement modifiées
@method_decorator([
    cache_page(3600),  # Cache 1 heure
    vary_on_headers('Accept-Language')
], name='dispatch')
class PrivacyView(BaseSEOView):
    """Page politique de confidentialité"""
    template_name = 'public_web/legal/privacy.html'
    page_title = 'Privacy Policy - Open Linguify Data Protection'
    meta_description = 'Open Linguify privacy policy: how we protect and handle your personal data on our educational platform.'


@method_decorator([
    cache_page(3600),
    vary_on_headers('Accept-Language')
], name='dispatch')
class TermsView(BaseSEOView):
    """Page conditions d'utilisation"""
    template_name = 'public_web/legal/terms.html'
    page_title = 'Terms of Service - Open Linguify User Agreement'
    meta_description = 'Open Linguify terms of service and user agreement for our educational platform and learning tools.'


@method_decorator([
    cache_page(3600),
    vary_on_headers('Accept-Language')
], name='dispatch')
class CookiesView(BaseSEOView):
    """Page politique des cookies"""
    template_name = 'public_web/legal/cookies.html'
    page_title = 'Cookie Policy - Open Linguify Cookie Usage'
    meta_description = 'Learn about how Open Linguify uses cookies to improve your experience on our educational platform.'


@method_decorator([
    cache_page(1800),  # Cache 30 minutes
    vary_on_headers('Accept-Language')
], name='dispatch')
class BrandView(BaseSEOView):
    """Page d'information sur la marque pour le SEO"""
    template_name = 'public_web/brand.html'
    page_title = 'OpenLinguify Brand - Open Source Educational Platform'
    meta_description = 'Learn about OpenLinguify (openlinguify), the open source educational platform revolutionizing language learning with AI.'
    meta_keywords = 'openlinguify, OpenLinguify, Open Linguify, brand information, open source education'


# SEO Utility Views
class RobotsTxtView(View):
    """Vue pour robots.txt optimisée"""
    
    def get(self, request):
        # Construire le contenu dynamiquement basé sur l'environnement
        base_url = request.build_absolute_uri('/').rstrip('/')
        
        content = f"""User-agent: *
Allow: /

# Important pages to index
Allow: /notebook/
Allow: /course/
Allow: /revision/
Allow: /features/
Allow: /apps/
Allow: /brand/

# Sitemaps
Sitemap: {base_url}/sitemap.xml

# Static files
Allow: /static/
Allow: /media/

# Favicon
Allow: /static/images/favicon.png

# Disallow admin and private areas
Disallow: /admin/
Disallow: /api/  # Block API endpoints except documentation
Disallow: /dashboard/
Disallow: /settings/
Disallow: /profile/

# SEO optimizations
Crawl-delay: 1
"""
        
        return HttpResponse(content, content_type='text/plain')


class SitemapXmlView(View):
    """Vue pour sitemap.xml optimisée avec cache"""
    
    def get(self, request):
        cache_key = f'sitemap_xml_{request.LANGUAGE_CODE}'
        cached_content = cache.get(cache_key)
        
        if cached_content:
            return HttpResponse(cached_content, content_type='application/xml')
        
        try:
            base_url = request.build_absolute_uri('/').rstrip('/')
            
            # URLs statiques avec priorités
            static_urls = [
                {'url': f'{base_url}/', 'priority': '1.0', 'changefreq': 'daily'},
                {'url': f'{base_url}/features/', 'priority': '0.9', 'changefreq': 'weekly'},
                {'url': f'{base_url}/about/', 'priority': '0.8', 'changefreq': 'monthly'},
                {'url': f'{base_url}/contact/', 'priority': '0.7', 'changefreq': 'monthly'},
                {'url': f'{base_url}/apps/', 'priority': '0.9', 'changefreq': 'weekly'},
                {'url': f'{base_url}/blog/', 'priority': '0.8', 'changefreq': 'weekly'},
                {'url': f'{base_url}/privacy/', 'priority': '0.5', 'changefreq': 'yearly'},
                {'url': f'{base_url}/terms/', 'priority': '0.5', 'changefreq': 'yearly'},
                {'url': f'{base_url}/cookies/', 'priority': '0.5', 'changefreq': 'yearly'},
                {'url': f'{base_url}/brand/', 'priority': '0.6', 'changefreq': 'monthly'},
            ]
            
            # URLs dynamiques des applications
            try:
                apps = manifest_parser.get_public_apps()
                for app in apps:
                    static_urls.append({
                        'url': f'{base_url}/apps/{app["slug"]}/',
                        'priority': '0.8',
                        'changefreq': 'weekly'
                    })
            except Exception as e:
                logger.warning(f"Failed to load apps for sitemap: {e}")
            
            # Générer le XML
            xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
            xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            
            for url_data in static_urls:
                xml_content += f"""  <url>
    <loc>{url_data['url']}</loc>
    <changefreq>{url_data['changefreq']}</changefreq>
    <priority>{url_data['priority']}</priority>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
  </url>
"""
            
            xml_content += '</urlset>'
            
            # Cache pendant 1 heure
            cache.set(cache_key, xml_content, 3600)
            
            return HttpResponse(xml_content, content_type='application/xml')
            
        except Exception as e:
            logger.error(f"Error generating sitemap: {e}")
            return HttpResponse("Error generating sitemap", status=500)


# Dynamic App Views
class DynamicAppsListView(View):
    """Dynamic view for listing all available apps with caching"""
    
    def get(self, request):
        language_code = getattr(request, 'LANGUAGE_CODE', 'en')
        cache_key = f'apps_list_{language_code}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            apps, context = cached_data
        else:
            try:
                apps = manifest_parser.get_public_apps()
                context = {
                    'title': _('Applications - Open Linguify Educational Tools'),
                    'meta_description': _('Discover all Open Linguify applications: AI tutors, flashcards, quizzes, note-taking and more educational tools.'),
                    'meta_keywords': _('applications, educational tools, AI tutors, flashcards, quizzes, learning apps'),
                }
                cache.set(cache_key, (apps, context), 300)  # Cache 5 minutes
            except Exception as e:
                logger.error(f"Error loading apps list: {e}")
                apps = []
                context = {
                    'title': _('Applications - Open Linguify'),
                    'meta_description': _('Educational applications'),
                }
        
        context['apps'] = apps
        return render(request, 'public_web/apps/apps_list.html', context)


class DynamicAppDetailView(View):
    """Dynamic view for individual app pages with improved error handling"""
    
    def get(self, request, app_slug):
        language_code = getattr(request, 'LANGUAGE_CODE', 'en')
        cache_key = f'app_detail_{app_slug}_{language_code}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            app, context, template_name = cached_data
        else:
            try:
                app = manifest_parser.get_app_by_slug(app_slug)
                if not app:
                    raise Http404(_("Application not found"))
                
                # Contexte SEO optimisé
                context = {
                    'title': f'{app["name"]} - Open Linguify',
                    'meta_description': f'Discover {app["name"]} on Open Linguify - {app.get("summary", app.get("description", ""))[:160]}',
                    'meta_keywords': f'{app["name"]}, {app.get("category", "")}, educational tool, language learning',
                    'app': app,
                    'canonical_url': request.build_absolute_uri(),
                }
                
                # Déterminer le template à utiliser
                template_name = self._get_template_name(app_slug)
                
                # Cache pendant 10 minutes
                cache.set(cache_key, (app, context, template_name), 600)
                
            except Exception as e:
                logger.error(f"Error loading app detail for {app_slug}: {e}")
                raise Http404(_("Application not found"))
        
        return render(request, template_name, context)
    
    def _get_template_name(self, app_slug):
        """Determine which template to use for the app"""
        # Ordre de priorité des templates
        template_candidates = [
            f'public_web/apps/app_{app_slug}.html',
            'public_web/apps/app_detail.html',
        ]
        
        for template in template_candidates:
            try:
                get_template(template)
                return template
            except TemplateDoesNotExist:
                continue
        
        # Fallback par défaut
        return 'public_web/apps/app_detail.html'


# API Views for performance monitoring
class HealthCheckView(View):
    """Health check endpoint for monitoring"""
    
    def get(self, request):
        try:
            # Test basic functionality
            apps_count = len(manifest_parser.get_public_apps())
            
            return JsonResponse({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'apps_loaded': apps_count,
                'cache_active': bool(cache.get('health_check_test')),
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JsonResponse({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
            }, status=500)


class ClearCacheView(View):
    """Cache clearing utility for administrators"""
    
    def post(self, request):
        if not request.user.is_staff:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        try:
            # Clear manifest parser cache
            manifest_parser.clear_cache()
            
            # Clear specific cache keys
            cache_patterns = [
                'landing_apps_*',
                'apps_list_*',
                'app_detail_*',
                'sitemap_xml_*',
            ]
            
            cleared_count = 0
            for pattern in cache_patterns:
                # Note: This is a simplified approach
                # In production, consider using cache.delete_many() or similar
                cache.clear()  # For now, clear all cache
                cleared_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Cache cleared successfully',
                'patterns_cleared': cleared_count,
            })
            
        except Exception as e:
            logger.error(f"Cache clearing failed: {e}")
            return JsonResponse({
                'error': f'Cache clearing failed: {str(e)}'
            }, status=500)


# Error handlers
def custom_404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'public_web/errors/404.html', {
        'title': 'Page Not Found - Open Linguify',
        'meta_description': 'The page you are looking for could not be found.',
    }, status=404)


def custom_500(request):
    """Custom 500 error handler"""
    return render(request, 'public_web/errors/500.html', {
        'title': 'Server Error - Open Linguify',
        'meta_description': 'An internal server error occurred.',
    }, status=500)