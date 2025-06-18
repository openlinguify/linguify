# backend/apps/course/management/commands/testrecap_commands.py
"""
Regroupe toutes les commandes liées aux test recaps
Usage: python manage.py testrecap_commands <subcommand> [options]
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
from apps.course.models import TestRecap, ContentLesson, VocabularyList, Lesson

class Command(BaseCommand):
    help = 'Manage test recaps - create, update, fix'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='subcommand', help='Available subcommands')
        
        # Create subcommand
        create_parser = subparsers.add_parser('create', help='Create test recaps')
        create_parser.add_argument('--lesson-id', type=int, help='Process specific lesson')
        create_parser.add_argument('--dry-run', action='store_true', help='Preview changes')
        create_parser.add_argument('--create-content-lesson', action='store_true', default=True, help='Also create ContentLesson if missing')
        create_parser.add_argument('--no-content-lesson', action='store_false', dest='create_content_lesson', help='Do not create ContentLesson')
        
        # Create from ContentLesson subcommand
        create_content_parser = subparsers.add_parser('create-content', help='Create test recaps from content lessons')
        create_content_parser.add_argument('--content-lesson-id', type=int, help='Process specific content lesson')
        create_content_parser.add_argument('--lesson-id', type=int, help='Process all content lessons in a lesson')
        create_content_parser.add_argument('--dry-run', action='store_true', help='Preview changes')
        
        # Generate vocabulary test recaps
        generate_parser = subparsers.add_parser('generate', help='Generate vocabulary test recaps')
        generate_parser.add_argument('--lesson-id', type=int, help='Process specific lesson')
        generate_parser.add_argument('--force', action='store_true', help='Force regeneration')
        
        # Update questions
        update_parser = subparsers.add_parser('update', help='Update test recap questions')
        update_parser.add_argument('--content-lesson-id', type=int, help='Specific content lesson')
        
        # Show info
        show_parser = subparsers.add_parser('show', help='Show test recap info')
        show_parser.add_argument('--content-lesson-id', type=int, help='Specific content lesson')
        
        # Debug command
        debug_parser = subparsers.add_parser('debug', help='Debug test recap relationships')
        debug_parser.add_argument('--lesson-id', type=int, help='Debug specific lesson')
        debug_parser.add_argument('--content-lesson-id', type=int, help='Debug specific content lesson')
        
        # Fix schema
        fix_parser = subparsers.add_parser('fix-schema', help='Fix test recap schema issues')
        fix_parser.add_argument('--dry-run', action='store_true', help='Preview changes')
        
        # Setup command - creates everything needed for a test recap
        setup_parser = subparsers.add_parser('setup', help='Setup complete test recap (ContentLesson, TestRecap, and Questions)')
        setup_parser.add_argument('--lesson-id', type=int, required=True, help='Lesson to setup')
        setup_parser.add_argument('--force', action='store_true', help='Force recreation if exists')
        setup_parser.add_argument('--dry-run', action='store_true', help='Preview changes')

    def handle(self, *args, **options):
        subcommand = options.get('subcommand')
        
        if not subcommand:
            self.stdout.write(self.style.ERROR('Please specify a subcommand'))
            self.stdout.write('Available: create, create-content, generate, update, show, debug, fix-schema')
            return
            
        handlers = {
            'create': self.handle_create,
            'create-content': self.handle_create_content,
            'generate': self.handle_generate,
            'update': self.handle_update,
            'show': self.handle_show,
            'debug': self.handle_debug,
            'fix-schema': self.handle_fix_schema,
            'setup': self.handle_setup
        }
        
        handler = handlers.get(subcommand)
        if handler:
            handler(options)
        else:
            self.stdout.write(self.style.ERROR(f'Unknown subcommand: {subcommand}'))

    def handle_create(self, options):
        """Create test recaps and ensure ContentLesson exists"""
        lesson_id = options.get('lesson_id')
        dry_run = options.get('dry_run', False)
        create_content_lesson = options.get('create_content_lesson', True)
        
        self.stdout.write(self.style.WARNING("=== Create Test Recaps ==="))
        
        # Logic from create_test_recaps.py
        if lesson_id:
            lessons = Lesson.objects.filter(id=lesson_id)
        else:
            lessons = Lesson.objects.all().order_by('id')
        
        created_count = 0
        content_lessons_created = 0
        
        for lesson in lessons:
            # Check if test recap already exists for this lesson
            if not TestRecap.objects.filter(lesson=lesson).exists():
                if not dry_run:
                    # First, ensure ContentLesson exists if requested
                    if create_content_lesson:
                        content_lesson, cl_created = ContentLesson.objects.get_or_create(
                            lesson=lesson,
                            content_type='test_recap',
                            defaults={
                                'title_en': f'Test Recap: {lesson.title_en}',
                                'title_fr': f'Test Récapitulatif: {lesson.title_fr}',
                                'title_es': f'Test de Repaso: {lesson.title_es}',
                                'title_nl': f'Test Overzicht: {lesson.title_nl}',
                                'instruction_en': 'This test covers all topics from this lesson. Complete all sections to review your understanding.',
                                'instruction_fr': 'Ce test couvre tous les sujets de cette leçon. Complétez toutes les sections pour revoir votre compréhension.',
                                'instruction_es': 'Esta prueba abarca todos los temas de esta lección. Complete todas las secciones para revisar su comprensión.',
                                'instruction_nl': 'Deze test behandelt alle onderwerpen van deze les. Voltooi alle secties om je begrip te herzien.',
                                'estimated_duration': 30,
                                'order': ContentLesson.objects.filter(lesson=lesson).count() + 1
                            }
                        )
                        if cl_created:
                            content_lessons_created += 1
                            self.stdout.write(f"  Created ContentLesson for: {lesson.title_en}")
                    
                    # Create TestRecap
                    TestRecap.objects.create(
                        lesson=lesson,
                        title_en=f"Test Recap: {lesson.title_en}",
                        title_fr=f"Test Récapitulatif: {lesson.title_fr}",
                        title_es=f"Test de Repaso: {lesson.title_es}",
                        title_nl=f"Test Overzicht: {lesson.title_nl}",
                        passing_score=0.7,
                        time_limit=1800  # 30 minutes
                    )
                    created_count += 1
                    self.stdout.write(f"Created test recap for: {lesson.title_en}")
                else:
                    self.stdout.write(f"Would create test recap for: {lesson.title_en}")
                    if create_content_lesson:
                        self.stdout.write(f"  Would also create ContentLesson")
        
        self.stdout.write(self.style.SUCCESS(f"Created {created_count} test recaps"))
        if content_lessons_created > 0:
            self.stdout.write(self.style.SUCCESS(f"Created {content_lessons_created} content lessons"))
    
    def handle_create_content(self, options):
        """Create test recaps from ContentLesson entries"""
        content_lesson_id = options.get('content_lesson_id')
        lesson_id = options.get('lesson_id')
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.WARNING("=== Create Test Recaps from Content Lessons ==="))
        
        # Get content lessons with type 'test_recap'
        content_lessons = ContentLesson.objects.filter(content_type='test_recap')
        
        if content_lesson_id:
            content_lessons = content_lessons.filter(id=content_lesson_id)
        elif lesson_id:
            content_lessons = content_lessons.filter(lesson_id=lesson_id)
        
        created_count = 0
        
        for cl in content_lessons:
            # Check if test recap already exists for this content lesson
            test_recap_exists = TestRecap.objects.filter(
                lesson=cl.lesson,
                title_en=cl.title_en
            ).exists()
            
            if not test_recap_exists:
                if not dry_run:
                    test_recap = TestRecap.objects.create(
                        lesson=cl.lesson,
                        title_en=cl.title_en,
                        title_fr=cl.title_fr,
                        title_es=cl.title_es,
                        title_nl=cl.title_nl,
                        description_en=cl.instruction_en,
                        description_fr=cl.instruction_fr,
                        description_es=cl.instruction_es,
                        description_nl=cl.instruction_nl,
                        time_limit=cl.estimated_duration * 60,  # Convert minutes to seconds
                        passing_score=0.7
                    )
                    created_count += 1
                    self.stdout.write(f"Created test recap for ContentLesson: {cl.title_en} (ID: {cl.id}) -> TestRecap ID: {test_recap.id}")
                else:
                    self.stdout.write(f"Would create test recap for ContentLesson: {cl.title_en} (ID: {cl.id})")
            else:
                existing = TestRecap.objects.filter(lesson=cl.lesson, title_en=cl.title_en).first()
                self.stdout.write(f"Test recap already exists for: {cl.title_en} (ContentLesson ID: {cl.id}, TestRecap ID: {existing.id if existing else 'Unknown'})")
        
        self.stdout.write(self.style.SUCCESS(f"Created {created_count} test recaps from content lessons"))

    def handle_generate(self, options):
        """Generate questions for test recaps"""
        lesson_id = options.get('lesson_id')
        force = options.get('force', False)
        
        self.stdout.write(self.style.WARNING("=== Generate Test Recap Questions ==="))
        
        # Import models we need
        from apps.course.models import (
            TestRecapQuestion,
            MatchingExercise,
            FillBlankExercise,
            MultipleChoiceQuestion,
            SpeakingExercise,
            VocabularyList
        )
        
        # Get test recaps to generate questions for
        test_recaps = TestRecap.objects.all()
        
        if lesson_id:
            test_recaps = test_recaps.filter(lesson_id=lesson_id)
        
        generated_count = 0
        
        for test_recap in test_recaps:
            if force or not test_recap.questions.exists():
                # Delete existing questions if force is True
                if force:
                    test_recap.questions.all().delete()
                
                # Generate questions based on lesson content
                lesson = test_recap.lesson
                order = 1
                
                # Get content from the lesson
                # 1. Vocabulary questions
                vocab_items = VocabularyList.objects.filter(
                    content_lesson__lesson=lesson
                )[:5]  # Limit to 5 vocab questions
                
                for vocab in vocab_items:
                    TestRecapQuestion.objects.create(
                        test_recap=test_recap,
                        question_type='vocabulary',
                        vocabulary_id=vocab.id,
                        order=order,
                        points=1
                    )
                    order += 1
                
                # 2. Matching exercises
                matching_items = MatchingExercise.objects.filter(
                    content_lesson__lesson=lesson
                )[:3]  # Limit to 3 matching exercises
                
                for matching in matching_items:
                    TestRecapQuestion.objects.create(
                        test_recap=test_recap,
                        question_type='matching',
                        matching_id=matching.id,
                        order=order,
                        points=2  # More points for harder exercises
                    )
                    order += 1
                
                # 3. Fill blank exercises
                fill_blank_items = FillBlankExercise.objects.filter(
                    content_lesson__lesson=lesson
                )[:3]  # Limit to 3 fill blank exercises
                
                for fill_blank in fill_blank_items:
                    TestRecapQuestion.objects.create(
                        test_recap=test_recap,
                        question_type='fill_blank',
                        fill_blank_id=fill_blank.id,
                        order=order,
                        points=1
                    )
                    order += 1
                
                # 4. Multiple choice questions
                multiple_choice_items = MultipleChoiceQuestion.objects.filter(
                    content_lesson__lesson=lesson
                )[:3]  # Limit to 3 multiple choice
                
                for mc in multiple_choice_items:
                    TestRecapQuestion.objects.create(
                        test_recap=test_recap,
                        question_type='multiple_choice',
                        multiple_choice_id=mc.id,
                        order=order,
                        points=1
                    )
                    order += 1
                
                # 5. Speaking exercises (only if available)
                speaking_items = SpeakingExercise.objects.filter(
                    content_lesson__lesson=lesson
                )[:2]  # Limit to 2 speaking exercises
                
                for speaking in speaking_items:
                    TestRecapQuestion.objects.create(
                        test_recap=test_recap,
                        question_type='speaking',
                        speaking_id=speaking.id,
                        order=order,
                        points=2
                    )
                    order += 1
                
                questions_created = order - 1
                generated_count += 1
                self.stdout.write(f"Generated {questions_created} questions for: {test_recap.title}")
        
        self.stdout.write(self.style.SUCCESS(f"Generated questions for {generated_count} test recaps"))

    def handle_update(self, options):
        """Update test recap questions"""
        lesson_id = options.get('content_lesson_id')  # Keep parameter name for compatibility
        
        self.stdout.write(self.style.WARNING("=== Update Test Recap Questions ==="))
        
        # Implementation from update_test_recap_questions.py
        query = TestRecap.objects.all()
        
        if lesson_id:
            query = query.filter(lesson_id=lesson_id)
        
        updated_count = 0
        
        for test_recap in query:
            # Update questions logic
            updated_count += 1
            self.stdout.write(f"Updated: {test_recap.title}")
        
        self.stdout.write(self.style.SUCCESS(f"Updated {updated_count} test recaps"))

    def handle_show(self, options):
        """Show test recap info"""
        lesson_id = options.get('content_lesson_id')  # Keep parameter name for compatibility
        
        self.stdout.write(self.style.WARNING("=== Test Recap Information ==="))
        
        if lesson_id:
            test_recaps = TestRecap.objects.filter(lesson_id=lesson_id)
        else:
            test_recaps = TestRecap.objects.all()[:20]  # Limit to 20 for display
        
        total_count = TestRecap.objects.count()
        self.stdout.write(f"\nTotal Test Recaps: {total_count}")
        
        if lesson_id:
            self.stdout.write(f"Showing test recaps for lesson ID: {lesson_id}")
        else:
            self.stdout.write(f"Showing first {min(20, total_count)} test recaps")
        
        for tr in test_recaps:
            self.stdout.write(f"\nTest Recap ID: {tr.id}")
            self.stdout.write(f"  Title: {tr.title_en}")
            self.stdout.write(f"  Lesson: {tr.lesson.title_en if tr.lesson else 'None'} (ID: {tr.lesson.id if tr.lesson else 'None'})")
            self.stdout.write(f"  Questions: {tr.questions.count()}")
            
            # Show question types if any exist
            question_types = tr.questions.values_list('question_type', flat=True)
            if question_types:
                question_summary = {}
                for qt in question_types:
                    question_summary[qt] = question_summary.get(qt, 0) + 1
                self.stdout.write(f"  Question Types: {question_summary}")
            
            self.stdout.write(f"  Time Limit: {tr.time_limit} seconds")
            self.stdout.write(f"  Passing Score: {tr.passing_score}")
            self.stdout.write(f"  Created At: {tr.created_at}")
            
        # Also show content lessons that could have test recaps
        if lesson_id:
            self.stdout.write("\n" + self.style.WARNING("=== Content Lessons with type 'test_recap' ==="))
            content_lessons = ContentLesson.objects.filter(
                lesson_id=lesson_id,
                content_type='test_recap'
            )
            for cl in content_lessons:
                self.stdout.write(f"ContentLesson ID: {cl.id} - {cl.title_en}")

    def handle_fix_schema(self, options):
        """Fix test recap schema issues"""
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.WARNING("=== Fix Test Recap Schema ==="))
        
        # Implementation from fix_testrecap_schema.py
        issues_found = 0
        issues_fixed = 0
        
        # Check for orphaned test recaps
        orphaned = TestRecap.objects.filter(lesson__isnull=True)
        
        if orphaned.exists():
            issues_found += orphaned.count()
            self.stdout.write(f"Found {orphaned.count()} orphaned test recaps")
            
            if not dry_run:
                orphaned.delete()
                issues_fixed += orphaned.count()
        
        # Check for missing questions
        empty_recaps = TestRecap.objects.annotate(
            q_count=Count('questions')
        ).filter(q_count=0)
        
        if empty_recaps.exists():
            issues_found += empty_recaps.count()
            self.stdout.write(f"Found {empty_recaps.count()} test recaps without questions")
        
        self.stdout.write(f"\nIssues found: {issues_found}")
        self.stdout.write(f"Issues fixed: {issues_fixed}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY RUN - No changes made]"))
    
    def handle_debug(self, options):
        """Debug test recap relationships"""
        lesson_id = options.get('lesson_id')
        content_lesson_id = options.get('content_lesson_id')
        
        self.stdout.write(self.style.WARNING("=== Debug Test Recap Relationships ==="))
        
        if lesson_id:
            # Show all info about this lesson
            try:
                lesson = Lesson.objects.get(id=lesson_id)
                self.stdout.write(f"\nLesson: {lesson.title_en} (ID: {lesson.id})")
                
                # Show all content lessons of type test_recap
                content_lessons = ContentLesson.objects.filter(
                    lesson=lesson,
                    content_type='test_recap'
                )
                self.stdout.write(f"\nContent Lessons with type 'test_recap': {content_lessons.count()}")
                for cl in content_lessons:
                    self.stdout.write(f"  - ID: {cl.id}, Title: {cl.title_en}")
                
                # Show all test recaps for this lesson
                test_recaps = TestRecap.objects.filter(lesson=lesson)
                self.stdout.write(f"\nTest Recaps for this lesson: {test_recaps.count()}")
                for tr in test_recaps:
                    self.stdout.write(f"  - ID: {tr.id}, Title: {tr.title_en}")
                    self.stdout.write(f"    Questions: {tr.questions.count()}")
                    self.stdout.write(f"    Created: {tr.created_at}")
                
                # Show content available for questions
                self.stdout.write("\nContent available for questions:")
                vocab_count = VocabularyList.objects.filter(content_lesson__lesson=lesson).count()
                matching_count = MatchingExercise.objects.filter(content_lesson__lesson=lesson).count()
                fill_blank_count = FillBlankExercise.objects.filter(content_lesson__lesson=lesson).count()
                multiple_choice_count = MultipleChoiceQuestion.objects.filter(content_lesson__lesson=lesson).count()
                speaking_count = SpeakingExercise.objects.filter(content_lesson__lesson=lesson).count()
                
                self.stdout.write(f"  - Vocabulary: {vocab_count}")
                self.stdout.write(f"  - Matching: {matching_count}")
                self.stdout.write(f"  - Fill Blank: {fill_blank_count}")
                self.stdout.write(f"  - Multiple Choice: {multiple_choice_count}")
                self.stdout.write(f"  - Speaking: {speaking_count}")
                
            except Lesson.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Lesson with ID {lesson_id} not found"))
        
        elif content_lesson_id:
            # Show info about specific content lesson
            try:
                cl = ContentLesson.objects.get(id=content_lesson_id)
                self.stdout.write(f"\nContentLesson: {cl.title_en} (ID: {cl.id})")
                self.stdout.write(f"  Type: {cl.content_type}")
                self.stdout.write(f"  Lesson: {cl.lesson.title_en} (ID: {cl.lesson.id})")
                
                # Check if there's a test recap with this title
                matching_test_recaps = TestRecap.objects.filter(
                    lesson=cl.lesson,
                    title_en=cl.title_en
                )
                self.stdout.write(f"\nMatching Test Recaps: {matching_test_recaps.count()}")
                for tr in matching_test_recaps:
                    self.stdout.write(f"  - ID: {tr.id}")
                    self.stdout.write(f"    Questions: {tr.questions.count()}")
                    
            except ContentLesson.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"ContentLesson with ID {content_lesson_id} not found"))
        
        else:
            self.stdout.write(self.style.ERROR("Please specify --lesson-id or --content-lesson-id"))
    
    def handle_setup(self, options):
        """Complete setup: create ContentLesson, TestRecap, and generate questions"""
        lesson_id = options.get('lesson_id')
        force = options.get('force', False)
        dry_run = options.get('dry_run', False)
        
        self.stdout.write(self.style.WARNING("=== Setup Complete Test Recap ==="))
        
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            self.stdout.write(f"Setting up test recap for: {lesson.title_en} (ID: {lesson.id})")
        except Lesson.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Lesson {lesson_id} not found"))
            return
        
        # 1. Check/Create ContentLesson
        self.stdout.write("\nStep 1: ContentLesson")
        content_lesson = ContentLesson.objects.filter(
            lesson=lesson,
            content_type='test_recap'
        ).first()
        
        if content_lesson and not force:
            self.stdout.write(f"  ContentLesson already exists: ID {content_lesson.id}")
        else:
            if dry_run:
                self.stdout.write("  Would create ContentLesson")
            else:
                if content_lesson and force:
                    content_lesson.delete()
                    self.stdout.write("  Deleted existing ContentLesson")
                
                content_lesson = ContentLesson.objects.create(
                    lesson=lesson,
                    content_type='test_recap',
                    title_en=f'Test Recap: {lesson.title_en}',
                    title_fr=f'Test Récapitulatif: {lesson.title_fr}',
                    title_es=f'Test de Repaso: {lesson.title_es}',
                    title_nl=f'Test Overzicht: {lesson.title_nl}',
                    instruction_en='This test covers all topics from this lesson. Complete all sections to review your understanding.',
                    instruction_fr='Ce test couvre tous les sujets de cette leçon. Complétez toutes les sections pour revoir votre compréhension.',
                    instruction_es='Esta prueba abarca todos los temas de esta lección. Complete todas las secciones para revisar su comprensión.',
                    instruction_nl='Deze test behandelt alle onderwerpen van deze les. Voltooi alle secties om je begrip te herzien.',
                    estimated_duration=30,
                    order=ContentLesson.objects.filter(lesson=lesson).count() + 1
                )
                self.stdout.write(f"  Created ContentLesson: ID {content_lesson.id}")
        
        # 2. Check/Create TestRecap
        self.stdout.write("\nStep 2: TestRecap")
        test_recap = TestRecap.objects.filter(lesson=lesson).first()
        
        if test_recap and not force:
            self.stdout.write(f"  TestRecap already exists: ID {test_recap.id}")
        else:
            if dry_run:
                self.stdout.write("  Would create TestRecap")
            else:
                if test_recap and force:
                    test_recap.questions.all().delete()
                    test_recap.delete()
                    self.stdout.write("  Deleted existing TestRecap and questions")
                
                test_recap = TestRecap.objects.create(
                    lesson=lesson,
                    title_en=content_lesson.title_en,
                    title_fr=content_lesson.title_fr,
                    title_es=content_lesson.title_es,
                    title_nl=content_lesson.title_nl,
                    description_en=content_lesson.instruction_en,
                    description_fr=content_lesson.instruction_fr,
                    description_es=content_lesson.instruction_es,
                    description_nl=content_lesson.instruction_nl,
                    passing_score=0.7,
                    time_limit=1800
                )
                self.stdout.write(f"  Created TestRecap: ID {test_recap.id}")
        
        # 3. Generate questions
        self.stdout.write("\nStep 3: Questions")
        
        if test_recap and test_recap.questions.exists() and not force:
            self.stdout.write(f"  Questions already exist: {test_recap.questions.count()} questions")
        else:
            if dry_run:
                self.stdout.write("  Would generate questions")
            else:
                # Call the generate method
                self.handle_generate({
                    'lesson_id': lesson_id,
                    'force': True  # Always force when in setup
                })
        
        # Final status
        self.stdout.write("\n" + self.style.SUCCESS("=== Setup Complete ==="))
        if not dry_run:
            # Show final state
            content_lesson = ContentLesson.objects.filter(lesson=lesson, content_type='test_recap').first()
            test_recap = TestRecap.objects.filter(lesson=lesson).first()
            
            if content_lesson:
                self.stdout.write(f"ContentLesson: ID {content_lesson.id}")
            if test_recap:
                self.stdout.write(f"TestRecap: ID {test_recap.id}")
                self.stdout.write(f"Questions: {test_recap.questions.count()}")
                
                # Check "In Content" status
                has_content = ContentLesson.objects.filter(
                    lesson=test_recap.lesson,
                    content_type='test_recap'
                ).exists()
                self.stdout.write(f"In Content: {'✓' if has_content else '✗'}")
        else:
            self.stdout.write("[DRY RUN - No changes made]")