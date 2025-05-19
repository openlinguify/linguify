from django.core.management.base import BaseCommand
from django.core.management import call_command
from apps.course.models import Lesson

class Command(BaseCommand):
    help = "Create matching exercises for ALL lessons using the existing create command"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--pairs-per-exercise',
            type=int,
            default=4,
            help='Number of pairs per exercise (default: 4)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip lessons that already have matching exercises'
        )
    
    def handle(self, *args, **options):
        pairs_per_exercise = options['pairs_per_exercise']
        dry_run = options['dry_run']
        skip_existing = options['skip_existing']
        
        self.stdout.write(self.style.WARNING(
            f"{'DRY RUN: ' if dry_run else ''}Creating matching exercises for ALL lessons...\n"
        ))
        
        # Get all lessons
        all_lessons = Lesson.objects.all().order_by('unit__order', 'order')
        total = all_lessons.count()
        
        self.stdout.write(f"Found {total} lessons\n")
        
        success = 0
        skipped = 0
        failed = 0
        
        for i, lesson in enumerate(all_lessons, 1):
            self.stdout.write(f"\n[{i}/{total}] Processing: {lesson.title_en} (ID: {lesson.id})")
            
            try:
                # Check if lesson already has matching exercises
                if skip_existing:
                    from apps.course.models import ContentLesson, MatchingExercise
                    existing = MatchingExercise.objects.filter(
                        content_lesson__lesson=lesson
                    ).exists()
                    
                    if existing:
                        self.stdout.write(f"  Skipping - already has matching exercises")
                        skipped += 1
                        continue
                
                # Call the create command for this lesson
                call_command(
                    'matching_commands',
                    'create',
                    lesson_id=lesson.id,
                    split=True,
                    pairs_per_exercise=pairs_per_exercise,
                    dry_run=dry_run,
                    verbosity=0
                )
                
                self.stdout.write(self.style.SUCCESS("  Success"))
                success += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Failed: {e}"))
                failed += 1
        
        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"\nTotal lessons: {total}")
        self.stdout.write(self.style.SUCCESS(f"Successful: {success}"))
        if skipped > 0:
            self.stdout.write(f"Skipped (existing): {skipped}")
        if failed > 0:
            self.stdout.write(self.style.ERROR(f"Failed: {failed}"))
        
        if dry_run:
            self.stdout.write("\nThis was a dry run. To execute for real:")
            self.stdout.write(self.style.SUCCESS(
                f"poetry run python manage.py create_all_matching_simple --pairs-per-exercise {pairs_per_exercise}"
            ))