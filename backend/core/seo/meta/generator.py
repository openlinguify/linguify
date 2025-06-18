"""
Advanced SEO meta tags system for maximum Google visibility
Includes Open Graph, Twitter Cards, and all essential meta tags
"""

from django.utils.translation import get_language
from django.utils import timezone
from urllib.parse import urljoin
from django.conf import settings
import re


class SEOMetaGenerator:
    """Generate comprehensive SEO meta tags for all page types"""
    
    DEFAULT_IMAGE = "https://www.openlinguify.com/static/images/og-default.png"
    SITE_NAME = "OpenLinguify"
    TWITTER_HANDLE = "@openlinguify"
    
    @classmethod
    def generate_base_tags(cls, request, title, description, keywords=None):
        """Generate base meta tags for any page"""
        current_url = cls._get_full_url(request)
        lang = get_language() or 'en'
        
        meta_tags = {
            # Essential Meta Tags
            'title': cls._optimize_title(title),
            'description': cls._optimize_description(description),
            'keywords': keywords or cls._generate_keywords(title, description),
            'author': 'OpenLinguify',
            'viewport': 'width=device-width, initial-scale=1.0',
            'robots': 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1',
            'googlebot': 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1',
            'bingbot': 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1',
            'revisit-after': '7 days',
            'language': lang,
            'content-language': lang,
            'distribution': 'global',
            'rating': 'general',
            'expires': 'never',
            'referrer': 'no-referrer-when-downgrade',
            
            # Canonical and alternates
            'canonical': current_url,
            
            # Mobile optimization
            'mobile-web-app-capable': 'yes',
            'apple-mobile-web-app-capable': 'yes',
            'apple-mobile-web-app-status-bar-style': 'black-translucent',
            'apple-mobile-web-app-title': cls.SITE_NAME,
            'application-name': cls.SITE_NAME,
            'msapplication-TileColor': '#2b5797',
            'msapplication-config': '/browserconfig.xml',
            'theme-color': '#ffffff',
            
            # Security
            'x-ua-compatible': 'IE=edge',
            'format-detection': 'telephone=no',
            
            # Performance hints
            'dns-prefetch': ['//fonts.googleapis.com', '//www.google-analytics.com'],
            'preconnect': ['//fonts.gstatic.com', '//www.google-analytics.com'],
        }
        
        return meta_tags
    
    @classmethod
    def generate_open_graph_tags(cls, request, title, description, image=None, page_type='website'):
        """Generate Open Graph tags for Facebook and other platforms"""
        current_url = cls._get_full_url(request)
        lang = get_language() or 'en'
        
        og_tags = {
            'og:title': cls._optimize_title(title, 60),
            'og:description': cls._optimize_description(description, 160),
            'og:type': page_type,
            'og:url': current_url,
            'og:site_name': cls.SITE_NAME,
            'og:locale': cls._get_og_locale(lang),
            'og:locale:alternate': cls._get_alternate_locales(lang),
            'og:image': image or cls.DEFAULT_IMAGE,
            'og:image:secure_url': image or cls.DEFAULT_IMAGE,
            'og:image:type': 'image/png',
            'og:image:width': '1200',
            'og:image:height': '630',
            'og:image:alt': f"{title} - {cls.SITE_NAME}",
            'og:updated_time': timezone.now().isoformat(),
            'fb:app_id': settings.FACEBOOK_APP_ID if hasattr(settings, 'FACEBOOK_APP_ID') else '',
            'fb:admins': settings.FACEBOOK_ADMINS if hasattr(settings, 'FACEBOOK_ADMINS') else '',
        }
        
        # Additional tags for articles
        if page_type == 'article':
            og_tags.update({
                'article:author': 'https://www.facebook.com/openlinguify',
                'article:publisher': 'https://www.facebook.com/openlinguify',
                'article:published_time': timezone.now().isoformat(),
                'article:modified_time': timezone.now().isoformat(),
                'article:section': 'Education',
                'article:tag': 'language learning, education, online courses'
            })
        
        return og_tags
    
    @classmethod
    def generate_twitter_card_tags(cls, request, title, description, image=None, card_type='summary_large_image'):
        """Generate Twitter Card tags"""
        twitter_tags = {
            'twitter:card': card_type,
            'twitter:site': cls.TWITTER_HANDLE,
            'twitter:creator': cls.TWITTER_HANDLE,
            'twitter:title': cls._optimize_title(title, 70),
            'twitter:description': cls._optimize_description(description, 200),
            'twitter:image': image or cls.DEFAULT_IMAGE,
            'twitter:image:alt': f"{title} - {cls.SITE_NAME}",
            'twitter:domain': 'openlinguify.com',
        }
        
        # App tags if mobile app exists
        twitter_tags.update({
            'twitter:app:name:iphone': cls.SITE_NAME,
            'twitter:app:name:ipad': cls.SITE_NAME,
            'twitter:app:name:googleplay': cls.SITE_NAME,
            'twitter:app:id:iphone': '',
            'twitter:app:id:ipad': '',
            'twitter:app:id:googleplay': '',
        })
        
        return twitter_tags
    
    @classmethod
    def generate_hreflang_tags(cls, request, available_languages=['en', 'fr', 'es', 'nl']):
        """Generate hreflang tags for multi-language support"""
        current_path = request.path
        hreflang_tags = []
        
        for lang in available_languages:
            if lang == 'en':
                # English as default
                hreflang_tags.append({
                    'rel': 'alternate',
                    'hreflang': 'en',
                    'href': f"https://www.openlinguify.com{current_path}"
                })
                hreflang_tags.append({
                    'rel': 'alternate',
                    'hreflang': 'x-default',
                    'href': f"https://www.openlinguify.com{current_path}"
                })
            else:
                hreflang_tags.append({
                    'rel': 'alternate',
                    'hreflang': lang,
                    'href': f"https://www.openlinguify.com/{lang}{current_path}"
                })
        
        return hreflang_tags
    
    @classmethod
    def generate_course_meta_tags(cls, request, course):
        """Specific meta tags for course pages"""
        title = f"{course.name} - Learn {course.language} Online"
        description = f"Master {course.language} with our {course.name} course. {course.description[:100]}..."
        
        base_tags = cls.generate_base_tags(request, title, description)
        og_tags = cls.generate_open_graph_tags(
            request, title, description, 
            image=course.image.url if hasattr(course, 'image') else None,
            page_type='course'
        )
        twitter_tags = cls.generate_twitter_card_tags(request, title, description)
        
        # Additional course-specific tags
        course_tags = {
            'course:duration': course.duration if hasattr(course, 'duration') else '',
            'course:level': course.level if hasattr(course, 'level') else 'beginner',
            'course:language': course.language if hasattr(course, 'language') else '',
            'course:rating': str(course.rating) if hasattr(course, 'rating') else '4.8',
        }
        
        return {**base_tags, **og_tags, **twitter_tags, **course_tags}
    
    @classmethod
    def generate_landing_page_meta(cls, request):
        """Optimized meta tags for landing page"""
        title = "Learn Languages Online - AI-Powered Language Learning Platform"
        description = "Master new languages with OpenLinguify's AI-powered lessons, interactive flashcards, and personalized learning paths. Start learning for free today!"
        keywords = "language learning, learn languages online, AI language tutor, interactive language lessons, language learning app, learn French, learn Spanish, learn Dutch, language courses"
        
        base_tags = cls.generate_base_tags(request, title, description, keywords)
        og_tags = cls.generate_open_graph_tags(request, title, description)
        twitter_tags = cls.generate_twitter_card_tags(request, title, description)
        
        return {**base_tags, **og_tags, **twitter_tags}
    
    @classmethod
    def _optimize_title(cls, title, max_length=60):
        """Optimize title for SEO"""
        if len(title) > max_length:
            title = title[:max_length-3] + "..."
        
        # Add site name if not present and space allows
        if cls.SITE_NAME not in title and len(title) + len(cls.SITE_NAME) + 3 <= max_length:
            title = f"{title} | {cls.SITE_NAME}"
        
        return title
    
    @classmethod
    def _optimize_description(cls, description, max_length=155):
        """Optimize description for SEO"""
        # Remove HTML tags
        description = re.sub('<.*?>', '', description)
        
        # Trim to length
        if len(description) > max_length:
            description = description[:max_length-3] + "..."
        
        return description.strip()
    
    @classmethod
    def _generate_keywords(cls, title, description):
        """Generate keywords from title and description"""
        base_keywords = [
            "language learning", "online courses", "AI tutor",
            "learn languages", "educational platform", "e-learning"
        ]
        
        # Extract important words from title and description
        text = f"{title} {description}".lower()
        words = re.findall(r'\b\w{4,}\b', text)
        
        # Filter common words and add to keywords
        important_words = [w for w in words if w not in ['with', 'from', 'this', 'that', 'your', 'learn']]
        
        return ', '.join(base_keywords + important_words[:10])
    
    @classmethod
    def _get_full_url(cls, request):
        """Get full URL from request"""
        return request.build_absolute_uri()
    
    @classmethod
    def _get_og_locale(cls, lang):
        """Convert language code to Open Graph locale"""
        locale_map = {
            'en': 'en_US',
            'fr': 'fr_FR',
            'es': 'es_ES',
            'nl': 'nl_NL'
        }
        return locale_map.get(lang, 'en_US')
    
    @classmethod
    def _get_alternate_locales(cls, current_lang):
        """Get alternate locales for Open Graph"""
        all_locales = ['en_US', 'fr_FR', 'es_ES', 'nl_NL']
        current_locale = cls._get_og_locale(current_lang)
        return [loc for loc in all_locales if loc != current_locale]
    
    @classmethod
    def render_meta_tags(cls, meta_dict):
        """Render meta tags as HTML"""
        html_tags = []
        
        for key, value in meta_dict.items():
            if key == 'title':
                html_tags.append(f'<title>{value}</title>')
            elif key == 'canonical':
                html_tags.append(f'<link rel="canonical" href="{value}" />')
            elif key == 'dns-prefetch':
                for domain in value:
                    html_tags.append(f'<link rel="dns-prefetch" href="{domain}" />')
            elif key == 'preconnect':
                for domain in value:
                    html_tags.append(f'<link rel="preconnect" href="{domain}" crossorigin />')
            elif key.startswith('og:') or key.startswith('twitter:') or key.startswith('fb:'):
                html_tags.append(f'<meta property="{key}" content="{value}" />')
            else:
                html_tags.append(f'<meta name="{key}" content="{value}" />')
        
        return '\n'.join(html_tags)