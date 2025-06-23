"""
URL Configuration for Public Web
Handles public-facing URLs with SEO optimizations, redirects, and multilingual support
"""
from django.urls import path, re_path
from django.views.generic import RedirectView
from django.conf import settings
from . import views

app_name = 'public_web'

# Main public URLs
urlpatterns = [
    # Landing and core pages
    path('', views.LandingView.as_view(), name='landing'),
    path('features/', views.FeaturesView.as_view(), name='features'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('blog/', views.BlogView.as_view(), name='blog'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('report-bug/', views.ReportBugView.as_view(), name='report_bug'),
    
    # SEO brand variations - all redirect to main landing
    path('openlinguify/', RedirectView.as_view(pattern_name='public_web:landing', permanent=True), name='openlinguify_redirect'),
    path('open-linguify/', RedirectView.as_view(pattern_name='public_web:landing', permanent=True), name='open_linguify_redirect'),
    path('linguify/', RedirectView.as_view(pattern_name='public_web:landing', permanent=True), name='linguify_redirect'),
    
    # Brand information page (separate from redirects for SEO diversity)
    path('brand/', views.BrandView.as_view(), name='brand'),
    
    # Legal pages with current structure
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('cookies/', views.CookiesView.as_view(), name='cookies'),
    
    # Legacy legal URLs - redirect to current structure
    path('legal/privacy/', RedirectView.as_view(pattern_name='public_web:privacy', permanent=True), name='legal_privacy_redirect'),
    path('legal/terms/', RedirectView.as_view(pattern_name='public_web:terms', permanent=True), name='legal_terms_redirect'),
    path('legal/cookies/', RedirectView.as_view(pattern_name='public_web:cookies', permanent=True), name='legal_cookies_redirect'),
    
    # Legacy annexes URLs - redirect to current structure  
    path('annexes/terms/', RedirectView.as_view(pattern_name='public_web:terms', permanent=True), name='annexes_terms_redirect'),
    path('annexes/privacy/', RedirectView.as_view(pattern_name='public_web:privacy', permanent=True), name='annexes_privacy_redirect'),
    path('annexes/cookies/', RedirectView.as_view(pattern_name='public_web:cookies', permanent=True), name='annexes_cookies_redirect'),
    
    # Apps section - dynamic system
    path('apps/', views.DynamicAppsListView.as_view(), name='apps'),
    
    # Legacy app URLs - redirect to dynamic system (MUST be before dynamic pattern)
    path('apps/courses/', RedirectView.as_view(url='/apps/course/', permanent=True), name='legacy_courses_redirect'),
    # Remove self-redirecting URLs - these are handled by the dynamic pattern below
    
    # Dynamic app detail (MUST be after legacy redirects)
    path('apps/<slug:app_slug>/', views.DynamicAppDetailView.as_view(), name='dynamic_app_detail'),
    
    # SEO and technical files
    path('robots.txt', views.RobotsTxtView.as_view(), name='robots_txt'),
    path('sitemap.xml', views.SitemapXmlView.as_view(), name='sitemap_xml'),
    
    # Health and monitoring endpoints
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    path('admin/clear-cache/', views.ClearCacheView.as_view(), name='clear_cache'),
]

# Additional SEO-friendly URL patterns
seo_patterns = [
    # Alternative spellings and common misspellings
    re_path(r'^open[-_]?linguify/?$', RedirectView.as_view(pattern_name='public_web:landing', permanent=True), name='seo_variations'),
    
    # Common educational platform searches
    path('learning-platform/', RedirectView.as_view(pattern_name='public_web:features', permanent=True), name='learning_platform_redirect'),
    path('language-learning/', RedirectView.as_view(pattern_name='public_web:features', permanent=True), name='language_learning_redirect'),
    
    # Common variations for apps page
    path('applications/', RedirectView.as_view(pattern_name='public_web:apps', permanent=True), name='applications_redirect'),
    path('tools/', RedirectView.as_view(pattern_name='public_web:apps', permanent=True), name='tools_redirect'),
    
    # Legacy blog patterns (if any)
    path('news/', RedirectView.as_view(pattern_name='public_web:blog', permanent=True), name='news_redirect'),
    path('updates/', RedirectView.as_view(pattern_name='public_web:blog', permanent=True), name='updates_redirect'),
]

# Conditional patterns for development/staging
if settings.DEBUG:
    debug_patterns = [
        # Test endpoints only available in debug mode
        path('test/cache/', views.ClearCacheView.as_view(), name='test_cache'),
        path('test/health/', views.HealthCheckView.as_view(), name='test_health'),
    ]
    urlpatterns.extend(debug_patterns)

# Add SEO patterns to main patterns
urlpatterns.extend(seo_patterns)

# Optional: Add language-specific redirects if using multiple languages
if hasattr(settings, 'LANGUAGES') and len(settings.LANGUAGES) > 1:
    language_patterns = [
        # Handle common language codes that might be in URLs
        re_path(r'^(?P<lang>en|fr|es|nl|de|it)/?$', 
                RedirectView.as_view(pattern_name='public_web:landing', permanent=False), 
                name='language_redirect'),
    ]
    # Note: These would need more sophisticated handling in a real multilingual setup
    # urlpatterns.extend(language_patterns)

# Error handling patterns (custom error pages)
handler404 = 'public_web.views.custom_404'
handler500 = 'public_web.views.custom_500'