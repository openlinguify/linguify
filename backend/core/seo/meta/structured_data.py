"""
Schema.org structured data generator for maximum Google SEO
Implements JSON-LD format for rich snippets and knowledge graph
"""

import json
from django.utils import timezone
from django.conf import settings
from datetime import datetime


class StructuredDataGenerator:
    """Generate structured data for different page types"""
    
    @staticmethod
    def organization():
        """Organization schema for brand knowledge panel"""
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "@id": "https://www.openlinguify.com/#organization",
            "name": "OpenLinguify",
            "alternateName": "Open Linguify",
            "url": "https://www.openlinguify.com/",
            "logo": {
                "@type": "ImageObject",
                "url": "https://www.openlinguify.com/static/images/logo.png",
                "width": 600,
                "height": 60,
                "caption": "OpenLinguify Logo"
            },
            "image": "https://www.openlinguify.com/static/images/og-image.png",
            "description": "OpenLinguify is the leading AI-powered language learning platform",
            "founder": {
                "@type": "Person",
                "name": "OpenLinguify Team"
            },
            "foundingDate": "2025",
            "sameAs": [
                "https://www.facebook.com/openlinguify",
                "https://twitter.com/openlinguify",
                "https://www.linkedin.com/company/openlinguify",
                "https://www.youtube.com/openlinguify",
                "https://www.instagram.com/openlinguify",
                "https://github.com/openlinguify"
            ],
            "contactPoint": [
                {
                    "@type": "ContactPoint",
                    "contactType": "customer support",
                    "email": "support@openlinguify.com",
                    "availableLanguage": ["English", "French", "Spanish", "Dutch"],
                    "areaServed": "Worldwide"
                }
            ],
            "address": {
                "@type": "PostalAddress",
                "addressCountry": "Global",
                "postalCode": "Online",
                "streetAddress": "Internet"
            }
        }
    
    @staticmethod
    def website():
        """WebSite schema for sitelinks search box"""
        return {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "@id": "https://www.openlinguify.com/#website",
            "url": "https://www.openlinguify.com/",
            "name": "OpenLinguify",
            "description": "Learn languages online with AI-powered lessons",
            "publisher": {
                "@id": "https://www.openlinguify.com/#organization"
            },
            "potentialAction": {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": "https://www.openlinguify.com/search?q={search_term_string}"
                },
                "query-input": "required name=search_term_string"
            },
            "inLanguage": ["en", "fr", "es", "nl"]
        }
    
    @staticmethod
    def breadcrumb(items):
        """BreadcrumbList schema for navigation"""
        breadcrumb_items = []
        
        for i, item in enumerate(items, 1):
            breadcrumb_items.append({
                "@type": "ListItem",
                "position": i,
                "name": item['name'],
                "item": item['url']
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": breadcrumb_items
        }
    
    @staticmethod
    def course(course_data):
        """Course schema for educational content"""
        return {
            "@context": "https://schema.org",
            "@type": "Course",
            "name": course_data.get('name', 'Language Course'),
            "description": course_data.get('description', ''),
            "provider": {
                "@id": "https://www.openlinguify.com/#organization"
            },
            "courseCode": course_data.get('code', ''),
            "coursePrerequisites": course_data.get('prerequisites', 'None'),
            "hasCourseInstance": {
                "@type": "CourseInstance",
                "courseMode": "online",
                "coursePlatform": "OpenLinguify",
                "courseWorkload": course_data.get('workload', 'PT1H'),
                "inLanguage": course_data.get('language', 'en')
            },
            "educationalLevel": course_data.get('level', 'beginner'),
            "teaches": course_data.get('teaches', 'Language Skills'),
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": course_data.get('rating', 4.8),
                "reviewCount": course_data.get('review_count', 1250),
                "bestRating": 5,
                "worstRating": 1
            },
            "offers": {
                "@type": "Offer",
                "price": course_data.get('price', '0'),
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "validFrom": timezone.now().isoformat()
            }
        }
    
    @staticmethod
    def faq_page(faqs):
        """FAQPage schema for FAQ rich results"""
        questions = []
        
        for faq in faqs:
            questions.append({
                "@type": "Question",
                "name": faq['question'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq['answer']
                }
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": questions
        }
    
    @staticmethod
    def how_to(steps_data):
        """HowTo schema for tutorial content"""
        steps = []
        
        for i, step in enumerate(steps_data['steps'], 1):
            steps.append({
                "@type": "HowToStep",
                "position": i,
                "name": step['name'],
                "text": step['text'],
                "url": step.get('url', ''),
                "image": step.get('image', '')
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": steps_data['name'],
            "description": steps_data['description'],
            "image": steps_data.get('image', ''),
            "totalTime": steps_data.get('total_time', 'PT30M'),
            "estimatedCost": {
                "@type": "MonetaryAmount",
                "currency": "USD",
                "value": "0"
            },
            "supply": [],
            "tool": [],
            "step": steps
        }
    
    @staticmethod
    def software_application():
        """SoftwareApplication schema for app listings"""
        return {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "OpenLinguify",
            "applicationCategory": "EducationalApplication",
            "applicationSubCategory": "Language Learning",
            "operatingSystem": "Web, iOS, Android",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": 4.8,
                "ratingCount": 15420,
                "bestRating": 5,
                "worstRating": 1
            },
            "author": {
                "@id": "https://www.openlinguify.com/#organization"
            },
            "screenshot": [
                "https://www.openlinguify.com/static/images/screenshots/dashboard.png",
                "https://www.openlinguify.com/static/images/screenshots/lessons.png",
                "https://www.openlinguify.com/static/images/screenshots/flashcards.png"
            ],
            "featureList": [
                "AI-powered lessons",
                "Interactive flashcards",
                "Speech recognition",
                "Progress tracking",
                "Multi-language support",
                "Offline mode"
            ],
            "softwareVersion": "2.0",
            "datePublished": "2025-01-01",
            "dateModified": timezone.now().isoformat()
        }
    
    @staticmethod
    def article(article_data):
        """Article schema for blog posts"""
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article_data['title'],
            "description": article_data['description'],
            "image": article_data.get('image', ''),
            "author": {
                "@type": "Person",
                "name": article_data.get('author', 'OpenLinguify Team')
            },
            "publisher": {
                "@id": "https://www.openlinguify.com/#organization"
            },
            "datePublished": article_data.get('published_date', timezone.now()).isoformat(),
            "dateModified": article_data.get('modified_date', timezone.now()).isoformat(),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": article_data['url']
            },
            "wordCount": article_data.get('word_count', 1000),
            "keywords": article_data.get('keywords', 'language learning'),
            "articleSection": article_data.get('section', 'Education'),
            "inLanguage": article_data.get('language', 'en')
        }
    
    @staticmethod
    def video_object(video_data):
        """VideoObject schema for video content"""
        return {
            "@context": "https://schema.org",
            "@type": "VideoObject",
            "name": video_data['title'],
            "description": video_data['description'],
            "thumbnailUrl": video_data['thumbnail'],
            "uploadDate": video_data.get('upload_date', timezone.now()).isoformat(),
            "duration": video_data.get('duration', 'PT5M'),
            "contentUrl": video_data['url'],
            "embedUrl": video_data.get('embed_url', ''),
            "interactionStatistic": {
                "@type": "InteractionCounter",
                "interactionType": "https://schema.org/WatchAction",
                "userInteractionCount": video_data.get('views', 0)
            },
            "publisher": {
                "@id": "https://www.openlinguify.com/#organization"
            }
        }
    
    @staticmethod
    def review(review_data):
        """Review schema for testimonials"""
        return {
            "@context": "https://schema.org",
            "@type": "Review",
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": review_data['rating'],
                "bestRating": 5,
                "worstRating": 1
            },
            "author": {
                "@type": "Person",
                "name": review_data['author']
            },
            "reviewBody": review_data['text'],
            "datePublished": review_data.get('date', timezone.now()).isoformat(),
            "publisher": {
                "@id": "https://www.openlinguify.com/#organization"
            }
        }
    
    @staticmethod
    def event(event_data):
        """Event schema for webinars/classes"""
        return {
            "@context": "https://schema.org",
            "@type": "Event",
            "name": event_data['name'],
            "description": event_data['description'],
            "startDate": event_data['start_date'].isoformat(),
            "endDate": event_data['end_date'].isoformat(),
            "eventStatus": "https://schema.org/EventScheduled",
            "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",
            "location": {
                "@type": "VirtualLocation",
                "url": event_data.get('url', 'https://www.openlinguify.com/events/')
            },
            "organizer": {
                "@id": "https://www.openlinguify.com/#organization"
            },
            "offers": {
                "@type": "Offer",
                "price": event_data.get('price', '0'),
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "url": event_data.get('registration_url', '')
            },
            "performer": {
                "@type": "Person",
                "name": event_data.get('instructor', 'OpenLinguify Instructor')
            }
        }
    
    @staticmethod
    def generate_script_tag(data):
        """Generate script tag for JSON-LD"""
        return f'<script type="application/ld+json">{json.dumps(data, indent=2)}</script>'
    
    @staticmethod
    def generate_multiple(data_list):
        """Generate multiple structured data scripts"""
        scripts = []
        for data in data_list:
            scripts.append(StructuredDataGenerator.generate_script_tag(data))
        return '\n'.join(scripts)