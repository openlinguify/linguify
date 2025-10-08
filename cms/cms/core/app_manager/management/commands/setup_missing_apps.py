# app_manager/management/commands/setup_missing_apps.py
from django.core.management.base import BaseCommand
from app_manager.models import App

class Command(BaseCommand):
    help = 'Setup missing Linguify applications that were not in the initial setup'
    
    def handle(self, *args, **options):
        apps_data = [
            {
                'code': 'language_ai',
                'display_name': 'Language AI',
                'description': 'AI-powered language assistant for conversations, translations, and language learning support',
                'icon_name': 'Bot',
                'color': '#06B6D4',
                'route_path': '/language_ai',
                'category': 'Intelligence IA',
                'version': '1.0.0',
                'installable': True,
                'order': 5,
                'manifest_data': {
                    'name': 'Language AI',
                    'summary': 'AI-powered language assistant',
                    'description': 'Practice conversations with an AI language assistant. Get translations, explanations, and personalized language learning support.',
                    'category': 'Intelligence IA',
                    'version': '1.0.0',
                    'author': 'Linguify Team',
                    'website': 'https://linguify.com',
                    'license': 'AGPL-3',
                    'installable': True,
                    'application': True,
                    'frontend_components': {
                        'icon': 'Bot',
                        'route': '/language_ai',
                        'color': '#06B6D4'
                    },
                    'web_urls': [
                        {
                            'path': '/language_ai/',
                            'name': 'Language AI',
                            'component': 'LanguageAIMain'
                        }
                    ]
                }
            },
            {
                'code': 'chat',
                'display_name': 'Chat',
                'description': 'Real-time chat with language partners and tutors',
                'icon_name': 'MessageSquare',
                'color': '#EC4899',
                'route_path': '/chat',
                'category': 'Communication',
                'version': '1.0.0',
                'installable': True,
                'order': 6,
                'manifest_data': {
                    'name': 'Chat',
                    'summary': 'Real-time language chat',
                    'description': 'Connect with language partners and tutors through real-time chat. Practice your target language with native speakers.',
                    'category': 'Communication',
                    'version': '1.0.0',
                    'author': 'Linguify Team',
                    'website': 'https://linguify.com',
                    'license': 'AGPL-3',
                    'installable': True,
                    'application': True,
                    'frontend_components': {
                        'icon': 'MessageSquare',
                        'route': '/chat',
                        'color': '#EC4899'
                    },
                    'web_urls': [
                        {
                            'path': '/chat/',
                            'name': 'Chat',
                            'component': 'ChatMain'
                        }
                    ]
                }
            },
            {
                'code': 'jobs',
                'display_name': 'Jobs & Careers',
                'description': 'Find language-related job opportunities and career resources',
                'icon_name': 'Briefcase',
                'color': '#14B8A6',
                'route_path': '/jobs',
                'category': 'Productivity',
                'version': '1.0.0',
                'installable': True,
                'order': 7,
                'manifest_data': {
                    'name': 'Jobs & Careers',
                    'summary': 'Language career opportunities',
                    'description': 'Explore language-related job opportunities, career paths, and professional development resources for multilingual professionals.',
                    'category': 'Productivity',
                    'version': '1.0.0',
                    'author': 'Linguify Team',
                    'website': 'https://linguify.com',
                    'license': 'AGPL-3',
                    'installable': True,
                    'application': True,
                    'frontend_components': {
                        'icon': 'Briefcase',
                        'route': '/jobs',
                        'color': '#14B8A6'
                    },
                    'web_urls': [
                        {
                            'path': '/jobs/',
                            'name': 'Jobs',
                            'component': 'JobsMain'
                        },
                        {
                            'path': '/jobs/search',
                            'name': 'Job Search',
                            'component': 'JobSearch'
                        }
                    ]
                }
            },
            {
                'code': 'flashcard',
                'display_name': 'Flashcards',
                'description': 'Create and study flashcard decks for vocabulary and phrases',
                'icon_name': 'Square',
                'color': '#F97316',
                'route_path': '/flashcard',
                'category': 'Learning',
                'version': '1.0.0',
                'installable': True,
                'order': 8,
                'manifest_data': {
                    'name': 'Flashcards',
                    'summary': 'Digital flashcard system',
                    'description': 'Create, organize, and study flashcard decks. Use spaced repetition to memorize vocabulary, phrases, and language patterns effectively.',
                    'category': 'Learning',
                    'version': '1.0.0',
                    'author': 'Linguify Team',
                    'website': 'https://linguify.com',
                    'license': 'AGPL-3',
                    'installable': True,
                    'application': True,
                    'frontend_components': {
                        'icon': 'Square',
                        'route': '/flashcard',
                        'color': '#F97316'
                    },
                    'web_urls': [
                        {
                            'path': '/flashcard/',
                            'name': 'Flashcards',
                            'component': 'FlashcardMain'
                        },
                        {
                            'path': '/flashcard/decks',
                            'name': 'My Decks',
                            'component': 'FlashcardDecks'
                        },
                        {
                            'path': '/flashcard/study',
                            'name': 'Study',
                            'component': 'FlashcardStudy'
                        }
                    ]
                }
            },
            {
                'code': 'progress',
                'display_name': 'Progress & Statistics',
                'description': 'Track your learning progress and view detailed statistics',
                'icon_name': 'TrendingUp',
                'color': '#6366F1',
                'route_path': '/progress',
                'category': 'Analytics',
                'version': '1.0.0',
                'installable': True,
                'order': 9,
                'manifest_data': {
                    'name': 'Progress & Statistics',
                    'summary': 'Learning analytics dashboard',
                    'description': 'Monitor your language learning journey with detailed progress tracking, statistics, and insights into your study habits.',
                    'category': 'Analytics',
                    'version': '1.0.0',
                    'author': 'Linguify Team',
                    'website': 'https://linguify.com',
                    'license': 'AGPL-3',
                    'installable': True,
                    'application': True,
                    'frontend_components': {
                        'icon': 'TrendingUp',
                        'route': '/progress',
                        'color': '#6366F1'
                    },
                    'web_urls': [
                        {
                            'path': '/progress/',
                            'name': 'Progress',
                            'component': 'ProgressMain'
                        },
                        {
                            'path': '/progress/stats',
                            'name': 'Statistics',
                            'component': 'ProgressStats'
                        },
                        {
                            'path': '/progress/achievements',
                            'name': 'Achievements',
                            'component': 'ProgressAchievements'
                        }
                    ]
                }
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for app_data in apps_data:
            app, created = App.objects.get_or_create(
                code=app_data['code'],
                defaults=app_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created app: {app.display_name} ({app.code})')
                )
            else:
                # Update existing app with new data
                for key, value in app_data.items():
                    if key != 'code':  # Don't update the code
                        setattr(app, key, value)
                app.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated app: {app.display_name} ({app.code})')
                )
        
        # Show summary
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'Setup complete! Created {created_count} apps, updated {updated_count} apps.'
            )
        )
        
        # List all apps
        self.stdout.write('')
        self.stdout.write('All apps in the system:')
        all_apps = App.objects.all().order_by('order')
        for app in all_apps:
            status = '✓' if app.is_enabled else '✗'
            self.stdout.write(
                f'  {status} {app.order}. {app.display_name} ({app.code}) - {app.category}'
            )