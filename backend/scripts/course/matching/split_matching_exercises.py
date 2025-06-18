# backend/apps/course/management/commands/split_matching_exercises.py
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.course.models import MatchingExercise, ContentLesson, VocabularyList, Lesson
import math

class Command(BaseCommand):
    help = 'Split large vocabulary lists into multiple smaller matching exercises'

    def add_arguments(self, parser):
        parser.add_argument('--lesson-id', type=int, help='Process specific lesson')
        parser.add_argument('--pairs-per-exercise', type=int, default=5, 
                          help='Number of pairs per exercise (default: 5)')
        parser.add_argument('--max-pairs', type=int, default=8, 
                          help='Maximum pairs per exercise (default: 8)')
        parser.add_argument('--min-pairs', type=int, default=4, 
                          help='Minimum pairs per exercise (default: 4)')
        parser.add_argument('--dry-run', action='store_true', help='Preview changes')
        parser.add_argument('--force', action='store_true', 
                          help='Delete existing exercises and recreate')

    def handle(self, *args, **options):
        lesson_id = options.get('lesson_id')
        pairs_per_exercise = options.get('pairs_per_exercise', 5)
        max_pairs = options.get('max_pairs', 8)
        min_pairs = options.get('min_pairs', 4)
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        
        # Validate parameters
        if pairs_per_exercise < min_pairs:
            pairs_per_exercise = min_pairs
        if pairs_per_exercise > max_pairs:
            pairs_per_exercise = max_pairs
        
        self.stdout.write(self.style.WARNING("=== Split Matching Exercises ==="))
        self.stdout.write(f"Pairs per exercise: {pairs_per_exercise}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY RUN MODE]"))
        
        # Get lessons to process
        if lesson_id:
            lessons = Lesson.objects.filter(id=lesson_id)
        else:
            lessons = Lesson.objects.all().order_by('id')
        
        stats = {
            'lessons_processed': 0,
            'exercises_created': 0,
            'exercises_deleted': 0,
            'vocabulary_processed': 0
        }
        
        for lesson in lessons:
            self.stdout.write(f"\nProcessing Lesson {lesson.id}: {lesson.title_en}")
            stats['lessons_processed'] += 1
            
            # Get vocabulary content lessons
            vocab_content = ContentLesson.objects.filter(
                lesson=lesson,
                content_type__icontains='vocabulary'
            ).order_by('order')
            
            # Get all vocabulary for this lesson
            all_vocabulary = []
            for vc in vocab_content:
                vocab_items = list(VocabularyList.objects.filter(content_lesson=vc))
                all_vocabulary.extend(vocab_items)
            
            if not all_vocabulary:
                self.stdout.write("  No vocabulary found, skipping")
                continue
            
            total_vocab = len(all_vocabulary)
            stats['vocabulary_processed'] += total_vocab
            self.stdout.write(f"  Found {total_vocab} vocabulary items")
            
            # Calculate number of exercises needed
            num_exercises = math.ceil(total_vocab / pairs_per_exercise)
            self.stdout.write(f"  Will create {num_exercises} exercises")
            
            # Get or create matching content lesson
            matching_content = ContentLesson.objects.filter(
                lesson=lesson,
                content_type__icontains='matching'
            ).first()
            
            if not matching_content and not dry_run:
                max_order = ContentLesson.objects.filter(lesson=lesson).order_by('-order').first()
                next_order = (max_order.order + 1) if max_order else 1
                
                matching_content = ContentLesson.objects.create(
                    lesson=lesson,
                    content_type='matching',
                    title_en=f"{lesson.title_en} - Matching",
                    title_fr=f"{lesson.title_fr} - Association",
                    title_es=f"{lesson.title_es} - Emparejamiento",  
                    title_nl=f"{lesson.title_nl} - Koppelen",
                    instruction_en="Match the words with their translations",
                    instruction_fr="Associez les mots avec leurs traductions",
                    instruction_es="Relaciona las palabras con sus traducciones",
                    instruction_nl="Koppel de woorden aan hun vertalingen",
                    estimated_duration=num_exercises * 3,  # 3 minutes per exercise
                    order=next_order
                )
            
            if not matching_content:
                continue
            
            # Delete existing exercises if force is True
            if force and not dry_run:
                existing = MatchingExercise.objects.filter(content_lesson=matching_content)
                stats['exercises_deleted'] += existing.count()
                existing.delete()
                self.stdout.write(f"  Deleted {existing.count()} existing exercises")
            
            # Create multiple exercises
            with transaction.atomic():
                for i in range(num_exercises):
                    start_idx = i * pairs_per_exercise
                    end_idx = min((i + 1) * pairs_per_exercise, total_vocab)
                    exercise_vocab = all_vocabulary[start_idx:end_idx]
                    
                    if not dry_run:
                        # Create the exercise
                        exercise = MatchingExercise.objects.create(
                            content_lesson=matching_content,
                            title_en=f"{lesson.title_en} - Match Set {i+1}",
                            title_fr=f"{lesson.title_fr} - Série {i+1}",
                            title_es=f"{lesson.title_es} - Serie {i+1}",
                            title_nl=f"{lesson.title_nl} - Set {i+1}",
                            pairs_count=len(exercise_vocab),
                            difficulty='medium',
                            order=i+1
                        )
                        
                        # Associate vocabulary
                        exercise.vocabulary_words.set(exercise_vocab)
                        stats['exercises_created'] += 1
                        
                        self.stdout.write(
                            f"    Created exercise {i+1}/{num_exercises}: "
                            f"{len(exercise_vocab)} pairs"
                        )
                    else:
                        self.stdout.write(
                            f"    Would create exercise {i+1}/{num_exercises}: "
                            f"{len(exercise_vocab)} pairs"
                        )
        
        # Summary
        self.stdout.write("\n" + self.style.WARNING("=== Summary ==="))
        for key, value in stats.items():
            self.stdout.write(f"{key.replace('_', ' ').title()}: {value}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN COMPLETE - No changes made]"))