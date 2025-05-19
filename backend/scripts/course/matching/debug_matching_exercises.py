from django.core.management.base import BaseCommand
from django.db import models
from apps.course.models import MatchingExercise, VocabularyList, ContentLesson, Lesson


class Command(BaseCommand):
    help = 'Debug matching exercises and their vocabulary associations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--lesson-id',
            type=int,
            help='Specific lesson ID to debug'
        )
        parser.add_argument(
            '--exercise-id',
            type=int,
            help='Specific exercise ID to debug'
        )

    def handle(self, *args, **options):
        lesson_id = options.get('lesson_id')
        exercise_id = options.get('exercise_id')
        
        self.stdout.write(self.style.WARNING("=== Debug Matching Exercises ==="))
        
        if exercise_id:
            self.debug_specific_exercise(exercise_id)
        elif lesson_id:
            self.debug_lesson(lesson_id)
        else:
            self.debug_all()
    
    def debug_specific_exercise(self, exercise_id):
        """Debug a specific matching exercise"""
        try:
            exercise = MatchingExercise.objects.get(id=exercise_id)
            self.stdout.write(f"\nExercise {exercise.id}:")
            self.stdout.write(f"  Title: {exercise.title_en}")
            self.stdout.write(f"  Pairs count: {exercise.pairs_count}")
            self.stdout.write(f"  Vocabulary words: {exercise.vocabulary_words.count()}")
            
            # Show vocabulary details
            self.stdout.write(f"\n  Vocabulary items:")
            for i, vocab in enumerate(exercise.vocabulary_words.all(), 1):
                self.stdout.write(f"    {i}. {vocab.word_en} - {vocab.word_fr}")
            
            # Show exercise data
            self.stdout.write(f"\n  Exercise data (en/fr):")
            data = exercise.get_exercise_data('en', 'fr')
            target_words = data.get('target_words', [])
            native_words = data.get('native_words', [])
            self.stdout.write(f"    Target words: {len(target_words)} items")
            self.stdout.write(f"    Native words: {len(native_words)} items")
            
        except MatchingExercise.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Exercise {exercise_id} not found"))
    
    def debug_lesson(self, lesson_id):
        """Debug all matching exercises in a lesson"""
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            self.stdout.write(f"\nLesson: {lesson.id} - {lesson.title_en}")
            
            # Count vocabulary
            vocab_content = ContentLesson.objects.filter(
                lesson=lesson,
                content_type__icontains='vocabulary'
            )
            total_vocab = 0
            for vc in vocab_content:
                count = VocabularyList.objects.filter(content_lesson=vc).count()
                total_vocab += count
                self.stdout.write(f"  Vocabulary in '{vc.title_en}': {count} items")
            
            self.stdout.write(f"  Total vocabulary: {total_vocab} items")
            
            # Check matching exercises
            matching_content = ContentLesson.objects.filter(
                lesson=lesson,
                content_type__icontains='matching'
            )
            
            for mc in matching_content:
                self.stdout.write(f"\n  Matching content: {mc.title_en}")
                exercises = MatchingExercise.objects.filter(content_lesson=mc).order_by('order')
                
                for exercise in exercises:
                    self.stdout.write(f"    Exercise {exercise.id}: '{exercise.title_en}'")
                    self.stdout.write(f"      - pairs_count: {exercise.pairs_count}")
                    self.stdout.write(f"      - vocabulary_words: {exercise.vocabulary_words.count()}")
                    
                    # Check exercise data
                    data = exercise.get_exercise_data('en', 'fr')
                    target_words = data.get('target_words', [])
                    self.stdout.write(f"      - target_words in data: {len(target_words)}")
                    
        except Lesson.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Lesson {lesson_id} not found"))
    
    def debug_all(self):
        """Show summary of all matching exercises"""
        self.stdout.write("\nSummary of all matching exercises:")
        
        # Group by pairs_count
        count_groups = MatchingExercise.objects.values('pairs_count').annotate(
            count=models.Count('id')
        ).order_by('pairs_count')
        
        for group in count_groups:
            self.stdout.write(f"  {group['pairs_count']} pairs: {group['count']} exercises")
        
        # Find exercises with mismatched pairs
        mismatch_count = 0
        for exercise in MatchingExercise.objects.all():
            vocab_count = exercise.vocabulary_words.count()
            if vocab_count != exercise.pairs_count:
                mismatch_count += 1
                
        self.stdout.write(f"\nExercises with mismatched vocabulary count: {mismatch_count}")
        
        # Show recent exercises
        self.stdout.write("\nMost recent 5 exercises:")
        recent = MatchingExercise.objects.order_by('-id')[:5]
        for ex in recent:
            self.stdout.write(f"  {ex.id}: {ex.title_en} - {ex.pairs_count} pairs, {ex.vocabulary_words.count()} vocab")