from django.core.management.base import BaseCommand
from apps.course.models import MatchingExercise


class Command(BaseCommand):
    help = 'Update pairs_count to match actual vocabulary count for matching exercises'

    def add_arguments(self, parser):
        parser.add_argument(
            '--exercise-id',
            type=int,
            help='Specific exercise ID to update'
        )
        parser.add_argument(
            '--lesson-id',
            type=int,
            help='Update all exercises in a specific lesson'
        )
        parser.add_argument(
            '--fix-all',
            action='store_true',
            help='Fix all exercises with mismatched counts'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes'
        )

    def handle(self, *args, **options):
        exercise_id = options.get('exercise_id')
        lesson_id = options.get('lesson_id')
        fix_all = options.get('fix_all')
        dry_run = options.get('dry_run')
        
        self.stdout.write(self.style.WARNING("=== Update Pairs Count ==="))
        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY RUN MODE]"))
        
        if exercise_id:
            self.update_exercise(exercise_id, dry_run)
        elif lesson_id:
            self.update_lesson_exercises(lesson_id, dry_run)
        elif fix_all:
            self.fix_all_exercises(dry_run)
        else:
            self.stdout.write(self.style.ERROR("Please specify --exercise-id, --lesson-id, or --fix-all"))
    
    def update_exercise(self, exercise_id, dry_run=False):
        """Update a specific exercise"""
        try:
            exercise = MatchingExercise.objects.get(id=exercise_id)
            vocab_count = exercise.vocabulary_words.count()
            
            if vocab_count != exercise.pairs_count:
                self.stdout.write(f"\nExercise {exercise.id}: '{exercise.title_en}'")
                self.stdout.write(f"  Current pairs_count: {exercise.pairs_count}")
                self.stdout.write(f"  Actual vocabulary: {vocab_count}")
                
                if not dry_run:
                    exercise.pairs_count = vocab_count
                    exercise.save()
                    self.stdout.write(self.style.SUCCESS(f"  Updated pairs_count to {vocab_count}"))
                else:
                    self.stdout.write(self.style.WARNING(f"  Would update pairs_count to {vocab_count}"))
            else:
                self.stdout.write(f"Exercise {exercise.id} already correct ({vocab_count} pairs)")
                
        except MatchingExercise.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Exercise {exercise_id} not found"))
    
    def update_lesson_exercises(self, lesson_id, dry_run=False):
        """Update all exercises in a lesson"""
        from apps.course.models import Lesson, ContentLesson
        
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            matching_content = ContentLesson.objects.filter(
                lesson=lesson,
                content_type__icontains='matching'
            )
            
            updated_count = 0
            for mc in matching_content:
                exercises = MatchingExercise.objects.filter(content_lesson=mc)
                for exercise in exercises:
                    vocab_count = exercise.vocabulary_words.count()
                    if vocab_count != exercise.pairs_count:
                        self.stdout.write(f"\nExercise {exercise.id}: '{exercise.title_en}'")
                        self.stdout.write(f"  Current: {exercise.pairs_count}, Actual: {vocab_count}")
                        
                        if not dry_run:
                            exercise.pairs_count = vocab_count
                            exercise.save()
                            updated_count += 1
                            self.stdout.write(self.style.SUCCESS("  Updated"))
                        else:
                            self.stdout.write(self.style.WARNING("  Would update"))
            
            self.stdout.write(f"\nTotal exercises updated: {updated_count}")
            
        except Lesson.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Lesson {lesson_id} not found"))
    
    def fix_all_exercises(self, dry_run=False):
        """Fix all exercises with mismatched counts"""
        exercises = MatchingExercise.objects.all()
        mismatch_count = 0
        fixed_count = 0
        
        for exercise in exercises:
            vocab_count = exercise.vocabulary_words.count()
            if vocab_count != exercise.pairs_count:
                mismatch_count += 1
                self.stdout.write(f"\nExercise {exercise.id}: '{exercise.title_en}'")
                self.stdout.write(f"  Current: {exercise.pairs_count}, Actual: {vocab_count}")
                
                if not dry_run:
                    exercise.pairs_count = vocab_count
                    exercise.save()
                    fixed_count += 1
                    self.stdout.write(self.style.SUCCESS("  Fixed"))
                else:
                    self.stdout.write(self.style.WARNING("  Would fix"))
        
        self.stdout.write(f"\nFound {mismatch_count} mismatched exercises")
        if not dry_run:
            self.stdout.write(f"Fixed {fixed_count} exercises")
        else:
            self.stdout.write(f"Would fix {mismatch_count} exercises")