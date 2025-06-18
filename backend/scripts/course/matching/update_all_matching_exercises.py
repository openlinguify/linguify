import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.course.models import ContentLesson, MatchingExercise, VocabularyList

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = """Update all matching exercises by recreating them with split functionality
    
    This command:
    1. Identifies all matching exercises connected to large vocabulary lists
    2. Deletes existing exercises (preserving lesson relationships)
    3. Recreates them with optimal split configuration
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
            '--vocab-threshold',
            type=int,
            default=8,
            help='Only process exercises with vocab lists larger than this (default: 8)'
        )
    
    def handle(self, *args, **options):
        pairs_per_exercise = options['pairs_per_exercise']
        dry_run = options['dry_run']
        vocab_threshold = options['vocab_threshold']
        
        self.stdout.write(self.style.WARNING(
            f"{'DRY RUN: ' if dry_run else ''}Updating all matching exercises with vocab > {vocab_threshold} items...\n"
        ))
        
        # Find all matching exercises that need updating
        exercises_to_update = self._find_exercises_to_update(vocab_threshold)
        
        if not exercises_to_update:
            self.stdout.write(self.style.SUCCESS("No exercises need updating."))
            return
        
        self.stdout.write(f"Found {len(exercises_to_update)} exercises to update:\n")
        
        success_count = 0
        error_count = 0
        
        for exercise in exercises_to_update:
            try:
                if self._update_exercise(exercise, pairs_per_exercise, dry_run):
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"Error updating {exercise}: {e}"))
        
        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"Successfully updated: {success_count}"))
        if error_count:
            self.stdout.write(self.style.ERROR(f"Failed to update: {error_count}"))
    
    def _find_exercises_to_update(self, vocab_threshold):
        """Find all matching exercises connected to large vocabulary lists"""
        exercises = []
        
        for exercise in MatchingExercise.objects.all().select_related('content_lesson__lesson'):
            vocab_list = self._get_exercise_vocabulary(exercise)
            if vocab_list and len(vocab_list) > vocab_threshold:
                exercises.append(exercise)
        
        return exercises
    
    def _get_exercise_vocabulary(self, exercise):
        """Get vocabulary list associated with an exercise"""
        if hasattr(exercise, 'vocabulary_lists'):
            # ManyToMany relationship
            return list(exercise.vocabulary_lists.all())
        
        # Try to find vocabulary through the lesson
        lesson = exercise.content_lesson.lesson
        vocab_contents = ContentLesson.objects.filter(
            lesson=lesson,
            content_type='vocabulary'
        )
        
        for content in vocab_contents:
            vocab_lists = VocabularyList.objects.filter(content_lesson=content)
            if vocab_lists.exists():
                return list(vocab_lists.all().prefetch_related('vocabularyitem_set'))
        
        return []
    
    def _update_exercise(self, exercise, pairs_per_exercise, dry_run):
        """Update a single exercise by recreating it with splits"""
        lesson = exercise.content_lesson.lesson
        vocab_lists = self._get_exercise_vocabulary(exercise)
        
        if not vocab_lists:
            self.stdout.write(self.style.WARNING(f"No vocabulary found for {exercise}"))
            return False
        
        # Calculate total vocabulary
        total_vocab = sum(v.vocabularyitem_set.count() for v in vocab_lists)
        
        self.stdout.write(
            f"\nProcessing: {lesson.title_en} (ID: {lesson.id})\n"
            f"  Current exercise: {exercise.title_en or exercise.title_fr}\n"
            f"  Vocabulary items: {total_vocab}\n"
            f"  Will create: {(total_vocab + pairs_per_exercise - 1) // pairs_per_exercise} exercises\n"
        )
        
        if dry_run:
            self.stdout.write(self.style.INFO("  [DRY RUN] Would delete and recreate"))
            return True
        
        try:
            with transaction.atomic():
                # Store the original content lesson
                content_lesson = exercise.content_lesson
                
                # Delete the existing exercise
                exercise.delete()
                self.stdout.write(self.style.WARNING("  Deleted existing exercise"))
                
                # Recreate with splits using the matching_commands
                from django.core.management import call_command
                call_command(
                    'matching_commands',
                    'create',
                    lesson_id=lesson.id,
                    split=True,
                    pairs_per_exercise=pairs_per_exercise,
                    verbosity=0
                )
                
                self.stdout.write(self.style.SUCCESS("  Created split exercises"))
                return True
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Error: {e}"))
            return False