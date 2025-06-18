# backend/apps/course/management/commands/course_maintenance.py
"""
Regroupe toutes les commandes de maintenance et diagnostic
Usage: python manage.py course_maintenance <subcommand> [options]
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db.models import Count, Q
from apps.course.models import (
    Lesson, ContentLesson, VocabularyList, 
    MatchingExercise, SpeakingExercise, TestRecap
)

class Command(BaseCommand):
    help = 'Course maintenance and diagnostic commands'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='subcommand', help='Available subcommands')
        
        # Diagnostic
        diag_parser = subparsers.add_parser('diagnostic', help='Run diagnostic checks')
        diag_parser.add_argument('--lesson-id', type=int, help='Check specific lesson')
        diag_parser.add_argument('--fix-suggestions', action='store_true', help='Show fix commands')
        
        # Fix orphaned content
        orphan_parser = subparsers.add_parser('fix-orphaned', help='Fix orphaned content')
        orphan_parser.add_argument('--dry-run', action='store_true', help='Preview changes')
        
        # Setup all
        setup_parser = subparsers.add_parser('setup-all', help='Run all setup commands')
        setup_parser.add_argument('--dry-run', action='store_true', help='Preview changes')
        setup_parser.add_argument('--force', action='store_true', help='Force update')
        setup_parser.add_argument('--lesson-id', type=int, help='Process specific lesson')
        setup_parser.add_argument('--skip-matching', action='store_true', help='Skip matching')
        setup_parser.add_argument('--skip-speaking', action='store_true', help='Skip speaking')
        setup_parser.add_argument('--skip-testrecap', action='store_true', help='Skip test recap')

    def handle(self, *args, **options):
        subcommand = options.get('subcommand')
        
        if not subcommand:
            self.stdout.write(self.style.ERROR('Please specify a subcommand'))
            self.stdout.write('Available: diagnostic, fix-orphaned, setup-all')
            return
            
        handlers = {
            'diagnostic': self.handle_diagnostic,
            'fix-orphaned': self.handle_fix_orphaned,
            'setup-all': self.handle_setup_all
        }
        
        handler = handlers.get(subcommand)
        if handler:
            handler(options)
        else:
            self.stdout.write(self.style.ERROR(f'Unknown subcommand: {subcommand}'))

    def handle_diagnostic(self, options):
        """Run diagnostic checks (from course_diagnostic)"""
        lesson_id = options.get('lesson_id')
        show_fixes = options.get('fix_suggestions', False)
        
        self.stdout.write(self.style.WARNING("=== Course Diagnostic Report ==="))
        
        # Get lessons to check
        if lesson_id:
            lessons = Lesson.objects.filter(id=lesson_id)
            if not lessons.exists():
                self.stdout.write(self.style.ERROR(f"Lesson {lesson_id} not found"))
                return
        else:
            lessons = Lesson.objects.all().order_by('id')
        
        issues = []
        stats = {
            'total_lessons': 0,
            'total_vocabulary': 0,
            'total_matching': 0,
            'total_speaking': 0,
            'total_testrecaps': 0,
            'orphaned_content': 0,
            'missing_matching': 0,
            'missing_associations': 0,
            'missing_testrecaps': 0
        }
        
        for lesson in lessons:
            stats['total_lessons'] += 1
            self.stdout.write(f"\nChecking Lesson {lesson.id}: {lesson.title_en}")
            
            # Get content lessons
            content_lessons = ContentLesson.objects.filter(lesson=lesson).order_by('order')
            
            # Check vocabulary
            vocab_content = content_lessons.filter(content_type__icontains='vocabulary')
            vocab_count = 0
            for vc in vocab_content:
                vc_count = VocabularyList.objects.filter(content_lesson=vc).count()
                vocab_count += vc_count
                stats['total_vocabulary'] += vc_count
                
                if vc_count == 0:
                    issues.append(f"Empty vocabulary content: {vc.title_en} (ID: {vc.id})")
            
            # Check matching exercises
            matching_content = content_lessons.filter(content_type__icontains='matching')
            has_vocabulary = vocab_count > 0
            
            if has_vocabulary and not matching_content.exists():
                stats['missing_matching'] += 1
                issues.append(f"Lesson {lesson.id} has vocabulary but no matching content")
            
            for mc in matching_content:
                exercises = MatchingExercise.objects.filter(content_lesson=mc)
                if not exercises.exists():
                    issues.append(f"Matching content without exercises: {mc.title_en}")
                else:
                    for ex in exercises:
                        stats['total_matching'] += 1
                        assoc_count = ex.vocabulary_words.count()
                        if assoc_count == 0:
                            stats['missing_associations'] += 1
                            issues.append(f"Matching exercise {ex.id} has no vocabulary associations")
            
            # Check speaking exercises
            speaking_content = content_lessons.filter(content_type__icontains='speaking')
            for sc in speaking_content:
                exercises = SpeakingExercise.objects.filter(content_lesson=sc)
                stats['total_speaking'] += exercises.count()
            
            # Check test recaps
            test_recap_content = content_lessons.filter(content_type__icontains='test_recap')
            if has_vocabulary and not test_recap_content.exists():
                stats['missing_testrecaps'] += 1
                issues.append(f"Lesson {lesson.id} has vocabulary but no test recap")
            
            for trc in test_recap_content:
                test_recaps = TestRecap.objects.filter(content_lesson=trc)
                stats['total_testrecaps'] += test_recaps.count()
        
        # Check for orphaned content
        orphaned = ContentLesson.objects.filter(lesson__isnull=True)
        stats['orphaned_content'] = orphaned.count()
        if orphaned.exists():
            for oc in orphaned:
                issues.append(f"Orphaned content lesson: {oc.title_en} (ID: {oc.id})")
        
        # Display results
        self.stdout.write("\n" + self.style.WARNING("=== Statistics ==="))
        for key, value in stats.items():
            formatted_key = key.replace('_', ' ').title()
            self.stdout.write(f"{formatted_key}: {value}")
        
        # Display issues
        if issues:
            self.stdout.write("\n" + self.style.ERROR(f"=== Issues Found ({len(issues)}) ==="))
            for issue in issues:
                self.stdout.write(self.style.ERROR(f"• {issue}"))
        else:
            self.stdout.write("\n" + self.style.SUCCESS("=== No Issues Found ==="))
        
        # Show fix suggestions
        if show_fixes and issues:
            self.stdout.write("\n" + self.style.NOTICE("=== Suggested Fixes ==="))
            
            if stats['missing_matching'] > 0 or stats['missing_associations'] > 0:
                self.stdout.write("• Fix matching exercises:")
                self.stdout.write("  poetry run python manage.py matching_commands create")
            
            if stats['missing_testrecaps'] > 0:
                self.stdout.write("• Generate test recaps:")
                self.stdout.write("  poetry run python manage.py testrecap_commands generate")
            
            if stats['orphaned_content'] > 0:
                self.stdout.write("• Fix orphaned content:")
                self.stdout.write("  poetry run python manage.py course_maintenance fix-orphaned")
            
            self.stdout.write("\n• Run complete setup:")
            self.stdout.write("  poetry run python manage.py course_maintenance setup-all")
        
        # Overall health
        health_score = 100
        if stats['missing_associations'] > 0:
            health_score -= 20
        if stats['missing_matching'] > 0:
            health_score -= 20
        if stats['orphaned_content'] > 0:
            health_score -= 10
        if stats['missing_testrecaps'] > 0:
            health_score -= 10
        
        self.stdout.write("\n" + self.style.WARNING("=== Overall Health ==="))
        if health_score >= 90:
            self.stdout.write(self.style.SUCCESS(f"Health Score: {health_score}% - Excellent"))
        elif health_score >= 70:
            self.stdout.write(self.style.WARNING(f"Health Score: {health_score}% - Good"))
        else:
            self.stdout.write(self.style.ERROR(f"Health Score: {health_score}% - Needs Attention"))

    def handle_fix_orphaned(self, options):
        """Fix orphaned content lessons (from fix_orphaned_content_lessons)"""
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.WARNING("=== Fix Orphaned Content Lessons ==="))
        
        orphaned = ContentLesson.objects.filter(lesson__isnull=True)
        count = orphaned.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("No orphaned content lessons found"))
            return
        
        self.stdout.write(f"Found {count} orphaned content lessons")
        
        for content in orphaned:
            self.stdout.write(f"  • {content.title_en} (ID: {content.id})")
        
        if not dry_run:
            orphaned.delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {count} orphaned content lessons"))
        else:
            self.stdout.write(self.style.WARNING("[DRY RUN - No changes made]"))

    def handle_setup_all(self, options):
        """Run all setup commands (from course_setup_all)"""
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        lesson_id = options.get('lesson_id')
        skip_matching = options.get('skip_matching', False)
        skip_speaking = options.get('skip_speaking', False)
        skip_testrecap = options.get('skip_testrecap', False)
        
        self.stdout.write(self.style.WARNING("=== Course Setup All ==="))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY RUN MODE]"))
        
        tasks = []
        
        # Define tasks to run
        if not skip_matching:
            tasks.append({
                'name': 'Create and Associate Matching Exercises',
                'command': 'matching_commands',
                'args': ['create']
            })
        
        if not skip_speaking:
            tasks.append({
                'name': 'Associate Speaking Exercises',
                'command': 'speaking_auto_associate',
                'args': []
            })
        
        if not skip_testrecap:
            tasks.append({
                'name': 'Generate Vocabulary Test Recaps',
                'command': 'testrecap_commands',
                'args': ['generate']
            })
        
        # Execute tasks
        for i, task in enumerate(tasks, 1):
            self.stdout.write(f"\n[{i}/{len(tasks)}] {task['name']}")
            self.stdout.write(self.style.NOTICE("=" * 50))
            
            try:
                # Build command arguments
                cmd_args = task['args'].copy()
                if dry_run:
                    cmd_args.append('--dry-run')
                if force:
                    cmd_args.append('--force')
                if lesson_id:
                    cmd_args.extend(['--lesson-id', str(lesson_id)])
                
                # Call the command
                call_command(task['command'], *cmd_args)
                
                self.stdout.write(self.style.SUCCESS(f"✓ {task['name']} completed"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ {task['name']} failed: {str(e)}"))
                if not force:
                    self.stdout.write(self.style.ERROR("Stopping due to error. Use --force to continue."))
                    break
        
        # Summary
        self.stdout.write("\n" + self.style.WARNING("=== Setup Summary ==="))
        self.stdout.write(f"Tasks run: {len(tasks)}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN COMPLETE]"))
        else:
            self.stdout.write(self.style.SUCCESS("\n[SETUP COMPLETE]"))