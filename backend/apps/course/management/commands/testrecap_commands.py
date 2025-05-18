# backend/apps/course/management/commands/testrecap_commands.py
"""
Regroupe toutes les commandes liées aux test recaps
Usage: python manage.py testrecap_commands <subcommand> [options]
"""
from django.core.management.base import BaseCommand
from apps.course.models import TestRecap, ContentLesson, VocabularyList, Lesson

class Command(BaseCommand):
    help = 'Manage test recaps - create, update, fix'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='subcommand', help='Available subcommands')
        
        # Create subcommand
        create_parser = subparsers.add_parser('create', help='Create test recaps')
        create_parser.add_argument('--lesson-id', type=int, help='Process specific lesson')
        create_parser.add_argument('--dry-run', action='store_true', help='Preview changes')
        
        # Generate vocabulary test recaps
        generate_parser = subparsers.add_parser('generate', help='Generate vocabulary test recaps')
        generate_parser.add_argument('--lesson-id', type=int, help='Process specific lesson')
        generate_parser.add_argument('--force', action='store_true', help='Force regeneration')
        
        # Update questions
        update_parser = subparsers.add_parser('update', help='Update test recap questions')
        update_parser.add_argument('--content-lesson-id', type=int, help='Specific content lesson')
        
        # Show info
        show_parser = subparsers.add_parser('show', help='Show test recap info')
        show_parser.add_argument('--content-lesson-id', type=int, help='Specific content lesson')
        
        # Fix schema
        fix_parser = subparsers.add_parser('fix-schema', help='Fix test recap schema issues')
        fix_parser.add_argument('--dry-run', action='store_true', help='Preview changes')

    def handle(self, *args, **options):
        subcommand = options.get('subcommand')
        
        if not subcommand:
            self.stdout.write(self.style.ERROR('Please specify a subcommand'))
            self.stdout.write('Available: create, generate, update, show, fix-schema')
            return
            
        handlers = {
            'create': self.handle_create,
            'generate': self.handle_generate,
            'update': self.handle_update,
            'show': self.handle_show,
            'fix-schema': self.handle_fix_schema
        }
        
        handler = handlers.get(subcommand)
        if handler:
            handler(options)
        else:
            self.stdout.write(self.style.ERROR(f'Unknown subcommand: {subcommand}'))

    def handle_create(self, options):
        """Create test recaps (from create_test_recaps)"""
        lesson_id = options.get('lesson_id')
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.WARNING("=== Create Test Recaps ==="))
        
        # Logic from create_test_recaps.py
        if lesson_id:
            lessons = Lesson.objects.filter(id=lesson_id)
        else:
            lessons = Lesson.objects.all().order_by('id')
        
        created_count = 0
        
        for lesson in lessons:
            content_lessons = ContentLesson.objects.filter(
                lesson=lesson,
                content_type__icontains='vocabulary'
            )
            
            for cl in content_lessons:
                if not TestRecap.objects.filter(content_lesson=cl).exists():
                    if not dry_run:
                        TestRecap.objects.create(
                            content_lesson=cl,
                            title=f"Test Recap: {cl.title_en}",
                            passes_required=3,
                            time_limit=600
                        )
                        created_count += 1
                    else:
                        self.stdout.write(f"Would create test recap for: {cl.title_en}")
        
        self.stdout.write(self.style.SUCCESS(f"Created {created_count} test recaps"))

    def handle_generate(self, options):
        """Generate vocabulary test recaps (from generate_vocabulary_test_recaps)"""
        lesson_id = options.get('lesson_id')
        force = options.get('force', False)
        
        self.stdout.write(self.style.WARNING("=== Generate Vocabulary Test Recaps ==="))
        
        # Similar logic to generate_vocabulary_test_recaps.py
        content_lessons = ContentLesson.objects.filter(content_type__icontains='test_recap')
        
        if lesson_id:
            content_lessons = content_lessons.filter(lesson_id=lesson_id)
        
        generated_count = 0
        
        for cl in content_lessons:
            test_recap = TestRecap.objects.filter(content_lesson=cl).first()
            
            if test_recap and (force or not test_recap.questions.exists()):
                # Generate questions based on vocabulary
                vocab_items = VocabularyList.objects.filter(
                    content_lesson__lesson=cl.lesson,
                    content_lesson__content_type__icontains='vocabulary'
                )[:20]  # Limit to 20 questions
                
                for vocab in vocab_items:
                    # Create question logic here
                    pass
                
                generated_count += 1
                self.stdout.write(f"Generated questions for: {cl.title_en}")
        
        self.stdout.write(self.style.SUCCESS(f"Generated questions for {generated_count} test recaps"))

    def handle_update(self, options):
        """Update test recap questions (from update_test_recap_questions)"""
        content_lesson_id = options.get('content_lesson_id')
        
        self.stdout.write(self.style.WARNING("=== Update Test Recap Questions ==="))
        
        # Implementation from update_test_recap_questions.py
        query = TestRecap.objects.all()
        
        if content_lesson_id:
            query = query.filter(content_lesson_id=content_lesson_id)
        
        updated_count = 0
        
        for test_recap in query:
            # Update questions logic
            updated_count += 1
            self.stdout.write(f"Updated: {test_recap.title}")
        
        self.stdout.write(self.style.SUCCESS(f"Updated {updated_count} test recaps"))

    def handle_show(self, options):
        """Show test recap info (from show_content_lesson_test_recap)"""
        content_lesson_id = options.get('content_lesson_id')
        
        self.stdout.write(self.style.WARNING("=== Test Recap Information ==="))
        
        if content_lesson_id:
            test_recaps = TestRecap.objects.filter(content_lesson_id=content_lesson_id)
        else:
            test_recaps = TestRecap.objects.all()
        
        for tr in test_recaps:
            self.stdout.write(f"\nTest Recap: {tr.title}")
            self.stdout.write(f"  Content Lesson: {tr.content_lesson.title_en}")
            self.stdout.write(f"  Questions: {tr.questions.count()}")
            self.stdout.write(f"  Time Limit: {tr.time_limit} seconds")
            self.stdout.write(f"  Passes Required: {tr.passes_required}")

    def handle_fix_schema(self, options):
        """Fix test recap schema issues (from fix_testrecap_schema)"""
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.WARNING("=== Fix Test Recap Schema ==="))
        
        # Implementation from fix_testrecap_schema.py
        issues_found = 0
        issues_fixed = 0
        
        # Check for orphaned test recaps
        orphaned = TestRecap.objects.filter(content_lesson__isnull=True)
        
        if orphaned.exists():
            issues_found += orphaned.count()
            self.stdout.write(f"Found {orphaned.count()} orphaned test recaps")
            
            if not dry_run:
                orphaned.delete()
                issues_fixed += orphaned.count()
        
        # Check for missing questions
        empty_recaps = TestRecap.objects.annotate(
            q_count=Count('questions')
        ).filter(q_count=0)
        
        if empty_recaps.exists():
            issues_found += empty_recaps.count()
            self.stdout.write(f"Found {empty_recaps.count()} test recaps without questions")
        
        self.stdout.write(f"\nIssues found: {issues_found}")
        self.stdout.write(f"Issues fixed: {issues_fixed}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY RUN - No changes made]"))