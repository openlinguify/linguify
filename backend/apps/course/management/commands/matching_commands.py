# backend/apps/course/management/commands/matching_commands.py
"""
Regroupe toutes les commandes liées aux exercices de matching
Usage: python manage.py matching_commands <subcommand> [options]
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.course.models import MatchingExercise, ContentLesson, VocabularyList, Lesson

class Command(BaseCommand):
    help = 'Manage matching exercises - create, associate, fix'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='subcommand', help='Available subcommands')
        
        # Create and associate subcommand
        create_parser = subparsers.add_parser('create', help='Create and associate matching exercises')
        create_parser.add_argument('--dry-run', action='store_true', help='Preview changes')
        create_parser.add_argument('--force', action='store_true', help='Force update')
        create_parser.add_argument('--lesson-id', type=int, help='Process specific lesson')
        create_parser.add_argument('--pairs', type=int, default=8, help='Number of pairs')
        create_parser.add_argument('--split', action='store_true', help='Split large vocabulary into multiple exercises')
        create_parser.add_argument('--pairs-per-exercise', type=int, default=5, help='Pairs per exercise when splitting')
        
        # Associate only subcommand
        assoc_parser = subparsers.add_parser('associate', help='Associate vocabulary with existing exercises')
        assoc_parser.add_argument('--force', action='store_true', help='Replace existing associations')
        assoc_parser.add_argument('--debug', action='store_true', help='Show debug info')
        assoc_parser.add_argument('--lesson', type=int, help='Content lesson ID')
        
        # Fix associations subcommand
        fix_parser = subparsers.add_parser('fix', help='Fix vocabulary associations')
        fix_parser.add_argument('--lesson-id', type=int, help='Process specific lesson')
        fix_parser.add_argument('--force', action='store_true', help='Force update')
        fix_parser.add_argument('--verbose', action='store_true', help='Detailed output')
        
        # Reset all exercises subcommand
        reset_parser = subparsers.add_parser('reset', help='Delete and recreate all matching exercises')
        reset_parser.add_argument('--confirm', action='store_true', help='Confirm deletion and recreation')
        reset_parser.add_argument('--pairs-per-exercise', type=int, default=5, help='Pairs per exercise')
        reset_parser.add_argument('--dry-run', action='store_true', help='Show what would be done')

    def handle(self, *args, **options):
        subcommand = options.get('subcommand')
        
        if not subcommand:
            self.stdout.write(self.style.ERROR('Please specify a subcommand: create, associate, or fix'))
            self.stdout.write('Use --help for more information')
            return
            
        if subcommand == 'create':
            self.handle_create(options)
        elif subcommand == 'associate':
            self.handle_associate(options)
        elif subcommand == 'fix':
            self.handle_fix(options)
        elif subcommand == 'reset':
            self.handle_reset(options)
        else:
            self.stdout.write(self.style.ERROR(f'Unknown subcommand: {subcommand}'))

    def handle_create(self, options):
        """Create and associate matching exercises (combines create_and_associate_matching)"""
        dry_run = options.get('dry_run', False)
        force_update = options.get('force', False)
        lesson_id = options.get('lesson_id')
        default_pairs = options.get('pairs', 8)
        split_exercises = options.get('split', False)
        pairs_per_exercise = options.get('pairs_per_exercise', 5)
        
        self.stdout.write(self.style.WARNING("=== Create and Associate Matching Exercises ==="))
        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY RUN MODE]"))
        
        # Implementation from create_and_associate_matching.py
        lessons = Lesson.objects.filter(id=lesson_id) if lesson_id else Lesson.objects.all().order_by('id')
        
        stats = {
            'lessons_processed': 0,
            'matching_created': 0,
            'exercises_created': 0,
            'associations_made': 0
        }
        
        for lesson in lessons:
            self.stdout.write(f"\nProcessing Lesson: {lesson.id} - {lesson.title_en}")
            stats['lessons_processed'] += 1
            
            # Get vocabulary content
            vocab_content = ContentLesson.objects.filter(
                lesson=lesson,
                content_type__icontains='vocabulary'
            ).order_by('order')
            
            if not vocab_content.exists():
                continue
                
            total_vocab = sum(VocabularyList.objects.filter(content_lesson=vc).count() 
                            for vc in vocab_content)
            
            if total_vocab == 0:
                continue
                
            # Check for matching content
            matching_content = ContentLesson.objects.filter(
                lesson=lesson,
                content_type__icontains='matching'
            ).first()
            
            # Create if doesn't exist
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
                    estimated_duration=5,
                    order=next_order
                )
                stats['matching_created'] += 1
            
            if not matching_content:
                continue
                
            # Create exercise(s) if needed
            exercises = MatchingExercise.objects.filter(content_lesson=matching_content)
            
            if not exercises.exists() and not dry_run:
                if split_exercises and total_vocab > pairs_per_exercise:
                    # Create multiple smaller exercises
                    import math
                    num_exercises = math.ceil(total_vocab / pairs_per_exercise)
                    all_vocabulary = []
                    
                    # Collect all vocabulary
                    for vc in vocab_content:
                        vocab_items = list(VocabularyList.objects.filter(content_lesson=vc))
                        all_vocabulary.extend(vocab_items)
                    
                    created_exercises = []
                    for i in range(num_exercises):
                        start_idx = i * pairs_per_exercise
                        end_idx = min((i + 1) * pairs_per_exercise, total_vocab)
                        
                        # Calculate the actual number of pairs for this exercise
                        actual_pairs = end_idx - start_idx
                        
                        exercise = MatchingExercise.objects.create(
                            content_lesson=matching_content,
                            title_en=f"{lesson.title_en} - Match Set {i+1}",
                            title_fr=f"{lesson.title_fr} - Série {i+1}",
                            title_es=f"{lesson.title_es} - Serie {i+1}",
                            title_nl=f"{lesson.title_nl} - Set {i+1}",
                            pairs_count=actual_pairs,  # Set actual pairs count
                            difficulty='medium',
                            order=i+1
                        )
                        
                        # Associate specific vocabulary slice
                        vocab_slice = all_vocabulary[start_idx:end_idx]
                        exercise.vocabulary_words.set(vocab_slice)
                        created_exercises.append(exercise)
                        stats['exercises_created'] += 1
                        
                        self.stdout.write(f"    Created exercise {i+1} with {actual_pairs} pairs")
                    
                    exercises = created_exercises
                else:
                    # Create single exercise
                    exercise = MatchingExercise.objects.create(
                        content_lesson=matching_content,
                        title_en=f"{lesson.title_en} - Match Vocabulary",
                        title_fr=f"{lesson.title_fr} - Associez le vocabulaire",
                        title_es=f"{lesson.title_es} - Emparejar vocabulario",
                        title_nl=f"{lesson.title_nl} - Koppel woordenschat",
                        pairs_count=min(default_pairs, total_vocab),
                        difficulty='medium'
                    )
                    exercises = [exercise]
                    stats['exercises_created'] += 1
            
            # Associate vocabulary (only if not already done during splitting)
            if not split_exercises:
                for exercise in exercises:
                    if exercise.vocabulary_words.count() == 0 or force_update:
                        if not dry_run:
                            result = exercise.auto_associate_vocabulary(force_update)
                            stats['associations_made'] += result
            else:
                # Count associations from split exercises
                for exercise in exercises:
                    stats['associations_made'] += exercise.vocabulary_words.count()
        
        # Summary
        self.stdout.write("\n" + self.style.WARNING("=== Summary ==="))
        for key, value in stats.items():
            self.stdout.write(f"{key.replace('_', ' ').title()}: {value}")

    def handle_associate(self, options):
        """Associate vocabulary with existing exercises (from matching_auto_associate)"""
        force_update = options.get('force', False)
        debug_mode = options.get('debug', False)
        specific_lesson = options.get('lesson')
        
        self.stdout.write(f"Parameters: lesson={specific_lesson}, force={force_update}, debug={debug_mode}")
        
        exercises_count, exercises_updated, words_added = MatchingExercise.auto_associate_all(
            content_lesson_id=specific_lesson,
            force_update=force_update
        )
        
        if debug_mode:
            self.show_debug_info(specific_lesson)
        
        self.stdout.write(self.style.SUCCESS(f"Processed {exercises_count} exercises"))
        self.stdout.write(self.style.SUCCESS(f"Updated {exercises_updated} exercises"))
        self.stdout.write(self.style.SUCCESS(f"Added {words_added} associations"))

    def handle_fix(self, options):
        """Fix vocabulary associations (from fix_matching_associations)"""
        lesson_id = options.get('lesson_id')
        force_update = options.get('force', False)
        verbose = options.get('verbose', False)
        
        self.stdout.write(self.style.WARNING("=== Fix Matching Associations ==="))
        
        lessons = Lesson.objects.filter(id=lesson_id) if lesson_id else Lesson.objects.all()
        
        total_fixed = 0
        
        for lesson in lessons:
            self.stdout.write(f"\nLesson: {lesson.id} - {lesson.title_en}")
            
            # Find issues and fix them
            content_lessons = ContentLesson.objects.filter(lesson=lesson)
            vocab_count = VocabularyList.objects.filter(
                content_lesson__in=content_lessons.filter(content_type__icontains='vocabulary')
            ).count()
            
            matching_content = content_lessons.filter(content_type__icontains='matching')
            
            for mc in matching_content:
                exercises = MatchingExercise.objects.filter(content_lesson=mc)
                
                for exercise in exercises:
                    current = exercise.vocabulary_words.count()
                    if current == 0 or (force_update and current < exercise.pairs_count):
                        if force_update:
                            exercise.vocabulary_words.clear()
                        
                        result = exercise.auto_associate_vocabulary(True)
                        if result > 0:
                            total_fixed += 1
                            self.stdout.write(self.style.SUCCESS(f"  Fixed exercise {exercise.id}: {result} associations"))
        
        self.stdout.write(self.style.SUCCESS(f"\nTotal exercises fixed: {total_fixed}"))

    def show_debug_info(self, content_lesson_id=None):
        """Show debug information"""
        # Implementation from matching_auto_associate
        self.stdout.write("\n=== Debug Information ===")
        
        vocab_count = VocabularyList.objects.count()
        matching_count = MatchingExercise.objects.count()
        
        self.stdout.write(f"Total vocabulary items: {vocab_count}")
        self.stdout.write(f"Total matching exercises: {matching_count}")
        
        if content_lesson_id:
            try:
                content_lesson = ContentLesson.objects.get(id=content_lesson_id)
                self.stdout.write(f"\nContent lesson: {content_lesson.title_en}")
                self.stdout.write(f"Type: {content_lesson.content_type}")
                
                exercises = MatchingExercise.objects.filter(content_lesson=content_lesson)
                for ex in exercises:
                    self.stdout.write(f"Exercise {ex.id}: {ex.vocabulary_words.count()} words")
            except ContentLesson.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Content lesson {content_lesson_id} not found"))
    
    def handle_reset(self, options):
        """Reset all matching exercises by deleting and recreating them"""
        if not options['confirm'] and not options['dry_run']:
            self.stdout.write(self.style.ERROR(
                "Please use --confirm to proceed or --dry-run to preview"
            ))
            return
        
        pairs_per_exercise = options['pairs_per_exercise']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.WARNING(
            f"{'DRY RUN: ' if dry_run else ''}Resetting ALL matching exercises..."
        ))
        
        # Get all lessons with matching exercises
        lessons_with_matching = set()
        for exercise in MatchingExercise.objects.all():
            lessons_with_matching.add(exercise.content_lesson.lesson)
        
        self.stdout.write(f"\nFound {len(lessons_with_matching)} lessons with matching exercises")
        
        success_count = 0
        error_count = 0
        
        for lesson in lessons_with_matching:
            try:
                self.stdout.write(f"\nProcessing: {lesson.title_en} (ID: {lesson.id})")
                
                if dry_run:
                    self.stdout.write("  [DRY RUN] Would delete and recreate exercises")
                    success_count += 1
                    continue
                
                # Delete all matching exercises for this lesson
                matching_contents = ContentLesson.objects.filter(
                    lesson=lesson,
                    content_type='matching'
                )
                
                exercise_count = 0
                for content in matching_contents:
                    exercises = MatchingExercise.objects.filter(content_lesson=content)
                    exercise_count += exercises.count()
                    exercises.delete()
                
                if exercise_count > 0:
                    self.stdout.write(f"  Deleted {exercise_count} existing exercises")
                    
                    # Recreate with split
                    self.handle_create({
                        'lesson_id': lesson.id,
                        'split': True,
                        'pairs_per_exercise': pairs_per_exercise,
                        'dry_run': False,
                        'force': True
                    })
                    
                    self.stdout.write(self.style.SUCCESS("  Recreated with split"))
                    success_count += 1
                
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"  Error: {e}"))
        
        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"Successfully reset: {success_count} lessons"))
        if error_count:
            self.stdout.write(self.style.ERROR(f"Failed: {error_count} lessons"))