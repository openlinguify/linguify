"""
Management command to safely access production database
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection


class Command(BaseCommand):
    help = 'Safely access production database with ORM'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-prod',
            action='store_true',
            help='Force access to production (dangerous!)',
        )

    def handle(self, *args, **options):
        # Safety check
        if not options['force_prod'] and settings.DEBUG:
            self.stdout.write(
                self.style.ERROR(
                    '🚨 This appears to be a development environment!'
                )
            )
            self.stdout.write(
                'Add --force-prod if you really want to access production data.'
            )
            return

        # Show database info
        db_config = settings.DATABASES['default']
        self.stdout.write(
            self.style.SUCCESS(
                f"🔗 Connected to: {db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}"
            )
        )

        # Test connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                self.stdout.write(f"📊 Database: {version}")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Connection failed: {e}")
            )
            return

        # Import commonly used models
        from apps.authentication.models import User
        from app_manager.models import App
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write("🚀 Production ORM Access Ready!")
        self.stdout.write("="*50)
        
        # Show some stats
        try:
            user_count = User.objects.count()
            app_count = App.objects.filter(is_enabled=True).count()
            
            self.stdout.write(f"👥 Total users: {user_count}")
            self.stdout.write(f"📱 Enabled apps: {app_count}")
            
            # Show recent users
            recent_users = User.objects.filter(is_active=True).order_by('-created_at')[:5]
            self.stdout.write("\n🔥 Recent active users:")
            for user in recent_users:
                self.stdout.write(f"  - {user.username} ({user.email})")
            
            # Show CV stats if jobs app is available
            try:
                from core.jobs.models import JobApplication
                total_applications = JobApplication.objects.count()
                applications_with_cv = JobApplication.objects.exclude(resume_file='').count()
                recent_applications = JobApplication.objects.order_by('-applied_at')[:3]
                
                self.stdout.write(f"\n📄 Job Applications: {total_applications} total, {applications_with_cv} with CVs")
                self.stdout.write("📋 Recent applications:")
                for app in recent_applications:
                    cv_status = "✅ CV" if app.has_resume() else "❌ No CV"
                    position = app.position.title if app.position else "Spontaneous"
                    self.stdout.write(f"  - {app.full_name} → {position} ({cv_status})")
                    
            except ImportError:
                self.stdout.write("\n📄 Jobs app not available")
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️ Could not fetch stats: {e}")
            )

        self.stdout.write("\n💡 Example commands:")
        self.stdout.write("  from apps.authentication.models import User")
        self.stdout.write("  users = User.objects.all()")
        self.stdout.write("  ")
        self.stdout.write("  # 📄 Access CVs:")
        self.stdout.write("  from core.jobs.models import JobApplication")
        self.stdout.write("  apps_with_cv = JobApplication.objects.exclude(resume_file='')")
        self.stdout.write("  latest_cv = apps_with_cv.latest('applied_at')")
        self.stdout.write("  print(f'Latest CV: {latest_cv.full_name} - {latest_cv.resume_file}')")
        self.stdout.write("  ")
        self.stdout.write("  # 🔧 Manage apps:")
        self.stdout.write("  community_app = App.objects.get(code='community')")
        self.stdout.write("  community_app.is_enabled = False  # Disable community in prod")
        self.stdout.write("  community_app.save()")
        
        self.stdout.write("\n📝 Pour accéder aux CVs via l'admin:")
        self.stdout.write("  1. Changez DJANGO_ENV=\"production\" dans .env")
        self.stdout.write("  2. python manage.py runserver")
        self.stdout.write("  3. Allez sur http://localhost:8000/admin/jobs/jobapplication/")
        
        self.stdout.write("\n⚠️  BE CAREFUL: You're in PRODUCTION!")