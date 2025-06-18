from django.core.management.base import BaseCommand
from django.db import transaction
from apps.course.models import Lesson, ContentLesson, MatchingExercise, VocabularyList
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = """Recreate ALL matching exercises for EVERY lesson in the system.
    
    This command will:
    1. Find all lessons in the system
    2. For each lesson with vocabulary, delete existing matching exercises
    3. Create new matching exercises with split functionality
    """
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--pairs-per-exercise',
            type=int,
            default=5,
            help='Number of pairs per exercise (default: 5)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        parser.add_argument(
            '--skip-empty',
            action='store_true',
            help='Skip lessons without vocabulary'
        )
    
    def handle(self, *args, **options):
        pairs_per_exercise = options['pairs_per_exercise']
        dry_run = options['dry_run']
        skip_empty = options['skip_empty']
        
        self.stdout.write(self.style.WARNING(
            f"{'DRY RUN: ' if dry_run else ''}Recreating ALL matching exercises for EVERY lesson...\n"
        ))
        
        # Get all lessons
        all_lessons = Lesson.objects.all().order_by('unit__order', 'order')
        
        self.stdout.write(f"Found {all_lessons.count()} lessons in total\n")
        
        processed = 0
        skipped = 0
        errors = 0
        
        for lesson in all_lessons:
            try:
                # Check if lesson has vocabulary (try multiple methods)
                total_vocab = 0
                
                # Method 1: Check through content lessons
                vocab_contents = ContentLesson.objects.filter(
                    lesson=lesson,
                    content_type='vocabulary'
                )
                for content in vocab_contents:
                    vocab_lists = VocabularyList.objects.filter(content_lesson=content)
                    for vocab_list in vocab_lists:
                        total_vocab += vocab_list.vocabularyitem_set.count()
                
                # Method 2: Check if lesson already has VocabularyList items linked
                if total_vocab == 0:
                    # Check all content lessons for this lesson
                    all_contents = ContentLesson.objects.filter(lesson=lesson)
                    for content in all_contents:
                        vocab_lists = VocabularyList.objects.filter(content_lesson=content)
                        for vocab_list in vocab_lists:
                            total_vocab += vocab_list.vocabularyitem_set.count()
                            
                # If still no vocabulary found, use the matching_commands create to check
                if total_vocab == 0:
                    # Try a dry run of the create command to see if it finds vocabulary
                    from io import StringIO
                    from django.core.management import call_command
                    output = StringIO()
                    try:
                        call_command(
                            'matching_commands',
                            'create',
                            lesson_id=lesson.id,
                            dry_run=True,
                            verbosity=0,
                            stdout=output
                        )
                        output_str = output.getvalue()
                        # Check if vocabulary was found in the output
                        if "vocabulary" in output_str.lower() and "found" in output_str.lower():
                            # Extract number from output if possible
                            import re
                            match = re.search(r'(\d+)\s+vocabulary', output_str.lower())
                            if match:
                                total_vocab = int(match.group(1))
                    except:
                        pass
                
                if total_vocab == 0 and skip_empty:
                    skipped += 1
                    continue
                
                self.stdout.write(f"\nProcessing: {lesson.title_en} (ID: {lesson.id})")
                self.stdout.write(f"  Vocabulary items: {total_vocab}")
                
                if dry_run:
                    self.stdout.write(self.style.INFO("  [DRY RUN] Would recreate matching exercises"))
                    processed += 1
                    continue
                
                # Delete existing matching exercises for this lesson
                matching_contents = ContentLesson.objects.filter(
                    lesson=lesson,
                    content_type='matching'
                )
                
                deleted_count = 0
                for content in matching_contents:
                    exercises = MatchingExercise.objects.filter(content_lesson=content)
                    deleted_count += exercises.count()
                    exercises.delete()
                
                if deleted_count > 0:
                    self.stdout.write(f"  Deleted {deleted_count} existing exercises")
                
                # Create new matching exercises with split
                if total_vocab > 0:
                    from django.core.management import call_command
                    
                    with transaction.atomic():
                        call_command(
                            'matching_commands',
                            'create',
                            lesson_id=lesson.id,
                            split=True,
                            pairs_per_exercise=pairs_per_exercise,
                            verbosity=0
                        )
                    
                    # Count new exercises
                    new_count = MatchingExercise.objects.filter(
                        content_lesson__lesson=lesson
                    ).count()
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"  Created {new_count} new exercises" + 
                        (f" ({total_vocab // pairs_per_exercise} sets of {pairs_per_exercise} pairs)" if new_count > 1 else "")
                    ))
                else:
                    self.stdout.write("  No vocabulary found, skipping creation")
                
                processed += 1
                
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f"  Error processing lesson {lesson.id}: {e}"))
        
        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"\nTotal lessons: {all_lessons.count()}")
        self.stdout.write(self.style.SUCCESS(f"Processed: {processed}"))
        if skipped > 0:
            self.stdout.write(f"Skipped (no vocabulary): {skipped}")
        if errors > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {errors}"))
        
        self.stdout.write("\nTo run this command for real:")
        self.stdout.write(self.style.SUCCESS(
            f"poetry run python manage.py recreate_all_matching --pairs-per-exercise {pairs_per_exercise}"
        ))