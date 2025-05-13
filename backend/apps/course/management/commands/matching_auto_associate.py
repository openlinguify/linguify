# backend/apps/course/management/commands/matching_auto_associate.py
from django.core.management.base import BaseCommand
from django.db import connection
from apps.course.models import MatchingExercise, ContentLesson, VocabularyList

class Command(BaseCommand):
    help = 'Automatically associate vocabulary items with matching exercises'

    def add_arguments(self, parser):
        parser.add_argument('--lesson', type=int, help='Process only a specific content lesson ID')
        parser.add_argument('--force', action='store_true', help='Replace existing associations instead of preserving them')
        parser.add_argument('--debug', action='store_true', help='Show additional debug information')
        parser.add_argument('--fix-sequence', action='store_true', help='Fix database sequence for vocabulary and matching tables')

    def handle(self, *args, **options):
        specific_lesson = options.get('lesson')
        force_update = options.get('force', False)
        debug_mode = options.get('debug', False)
        fix_sequence = options.get('fix_sequence', False)
        
        # Fix database sequences if requested
        if fix_sequence:
            self.fix_id_sequences()
        
        # Log the parameters
        self.stdout.write(f"Parameters: lesson={specific_lesson}, force={force_update}, debug={debug_mode}")
        
        # Use the new class method to perform auto-association
        exercises_count, exercises_updated, words_added = MatchingExercise.auto_associate_all(
            content_lesson_id=specific_lesson,
            force_update=force_update
        )
        
        # Show additional debug info if requested
        if debug_mode:
            self.show_debug_info(specific_lesson)
        
        # Summary output
        self.stdout.write(self.style.SUCCESS(f"=== Summary ==="))
        self.stdout.write(self.style.SUCCESS(f"Processed {exercises_count} matching exercises"))
        self.stdout.write(self.style.SUCCESS(f"Updated {exercises_updated} exercises"))
        self.stdout.write(self.style.SUCCESS(f"Added {words_added} vocabulary associations"))
    
    def fix_id_sequences(self):
        """Fix PostgreSQL sequences for VocabularyList and MatchingExercise tables"""
        self.stdout.write("Fixing database sequences...")
        
        with connection.cursor() as cursor:
            # Fix VocabularyList sequence
            cursor.execute("""
                SELECT setval('course_vocabularylist_id_seq', 
                COALESCE((SELECT MAX(id) FROM course_vocabularylist), 1));
            """)
            vocab_result = cursor.fetchone()
            
            # Fix MatchingExercise sequence
            cursor.execute("""
                SELECT setval('course_matchingexercise_id_seq', 
                COALESCE((SELECT MAX(id) FROM course_matchingexercise), 1));
            """)
            matching_result = cursor.fetchone()
        
        self.stdout.write(f"  - VocabularyList sequence reset to {vocab_result[0]}")
        self.stdout.write(f"  - MatchingExercise sequence reset to {matching_result[0]}")
        self.stdout.write(self.style.SUCCESS("Database sequences updated successfully"))
    
    def show_debug_info(self, specific_lesson=None):
        """Show debug information about vocabulary and matching exercises"""
        self.stdout.write("\n=== Debug Information ===")
        
        # Count of VocabularyList items
        vocab_query = VocabularyList.objects.all()
        self.stdout.write(f"Total vocabulary items: {vocab_query.count()}")
        
        # Count of MatchingExercise items
        matching_query = MatchingExercise.objects.all()
        self.stdout.write(f"Total matching exercises: {matching_query.count()}")
        
        # Show statistics for the specific lesson if provided
        if specific_lesson:
            content_lesson = ContentLesson.objects.get(id=specific_lesson)
            parent_lesson = content_lesson.lesson if content_lesson else None
            
            self.stdout.write(f"\nLesson info for content_lesson_id={specific_lesson}:")
            self.stdout.write(f"  - Title: {content_lesson.title_en}")
            self.stdout.write(f"  - Parent lesson: {parent_lesson}")
            
            # Count vocabulary in this lesson
            lesson_vocab = VocabularyList.objects.filter(content_lesson=content_lesson)
            self.stdout.write(f"  - Vocabulary in this lesson: {lesson_vocab.count()}")
            
            # Count vocabulary in parent lesson
            if parent_lesson:
                vocab_lessons = ContentLesson.objects.filter(
                    lesson=parent_lesson,
                    content_type__iexact='vocabulary'
                )
                self.stdout.write(f"  - Vocabulary lessons in parent lesson: {vocab_lessons.count()}")
                
                vocab_count = 0
                for vl in vocab_lessons:
                    lesson_count = VocabularyList.objects.filter(content_lesson=vl).count()
                    vocab_count += lesson_count
                    self.stdout.write(f"    - {vl.title_en}: {lesson_count} words")
                
                self.stdout.write(f"  - Total vocabulary in parent lesson: {vocab_count}")
            
            # Count matching exercises in this lesson
            matching_exercises = MatchingExercise.objects.filter(content_lesson=content_lesson)
            self.stdout.write(f"  - Matching exercises in this lesson: {matching_exercises.count()}")
            
            # Show details for each matching exercise
            for ex in matching_exercises:
                vocab_count = ex.vocabulary_words.count()
                self.stdout.write(f"    - Exercise {ex.id}: {vocab_count} vocabulary items (pairs_count={ex.pairs_count})")