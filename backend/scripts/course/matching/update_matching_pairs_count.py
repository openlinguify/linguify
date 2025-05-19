# backend/apps/course/management/commands/update_matching_pairs_count.py
from django.core.management.base import BaseCommand
from apps.course.models import MatchingExercise, VocabularyList

class Command(BaseCommand):
    help = 'Update pairs_count for matching exercises to match available vocabulary'

    def add_arguments(self, parser):
        parser.add_argument('--lesson-id', type=int, help='Process specific lesson')
        parser.add_argument('--max-pairs', type=int, default=16, help='Maximum pairs count (default: 16)')
        parser.add_argument('--dry-run', action='store_true', help='Preview changes')

    def handle(self, *args, **options):
        lesson_id = options.get('lesson_id')
        max_pairs = options.get('max-pairs', 16)
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.WARNING("=== Update Matching Pairs Count ==="))
        
        # Get exercises to update
        exercises = MatchingExercise.objects.all()
        if lesson_id:
            exercises = exercises.filter(content_lesson__lesson_id=lesson_id)
        
        updated_count = 0
        
        for exercise in exercises:
            # Count available vocabulary
            vocab_count = exercise.vocabulary_words.count()
            
            # If no vocabulary associated, try to find available vocabulary
            if vocab_count == 0:
                parent_lesson = exercise.content_lesson.lesson
                vocab_items = VocabularyList.find_vocabulary_for_matching(
                    content_lesson=exercise.content_lesson,
                    parent_lesson=parent_lesson
                )
                vocab_count = vocab_items.count()
            
            # Determine new pairs count (minimum 4, maximum as specified)
            new_pairs_count = min(max(vocab_count, 4), max_pairs, 20)  # 20 is the model max
            
            if exercise.pairs_count != new_pairs_count:
                self.stdout.write(
                    f"Exercise {exercise.id}: {exercise.title_en}\n"
                    f"  Current pairs: {exercise.pairs_count}\n"
                    f"  Available vocabulary: {vocab_count}\n"
                    f"  New pairs count: {new_pairs_count}"
                )
                
                if not dry_run:
                    exercise.pairs_count = new_pairs_count
                    exercise.save()
                    updated_count += 1
        
        self.stdout.write(f"\nTotal exercises updated: {updated_count}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY RUN - No changes made]"))