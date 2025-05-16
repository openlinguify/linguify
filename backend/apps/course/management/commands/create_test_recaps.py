import logging
import random
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.course.models import Lesson, ContentLesson, TestRecap, TestRecapQuestion
from apps.course.models import (
    MultipleChoiceQuestion, 
    FillBlankExercise, 
    MatchingExercise, 
    VocabularyList
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates test recap items for existing lessons'

    def add_arguments(self, parser):
        parser.add_argument(
            '--lesson_id',
            type=int,
            help='Specify a single lesson ID to create a test recap for'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Limit the number of lesson test recaps created (default: 10)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Create test recaps even if they already exist'
        )

    def handle(self, *args, **options):
        lesson_id = options.get('lesson_id')
        limit = options.get('limit')
        force = options.get('force')

        if lesson_id:
            lessons = Lesson.objects.filter(id=lesson_id)
            if not lessons.exists():
                self.stdout.write(self.style.ERROR(f'Lesson with ID {lesson_id} does not exist'))
                return
        else:
            # Get lessons that have content lessons
            lessons = Lesson.objects.filter(
                content_lessons__isnull=False
            ).distinct().order_by('?')[:limit]

        created_count = 0
        skipped_count = 0
        error_count = 0

        for lesson in lessons:
            try:
                with transaction.atomic():
                    # Check if a test recap already exists for this lesson
                    existing_recap = TestRecap.objects.filter(lesson=lesson).first()
                    
                    if existing_recap and not force:
                        self.stdout.write(f'Skipping lesson {lesson.id}: Test recap already exists')
                        skipped_count += 1
                        continue
                    
                    # Create or get content lesson for test recap
                    content_lesson = ContentLesson.objects.filter(
                        lesson=lesson,
                        content_type='test_recap'
                    ).first()
                    
                    if not content_lesson:
                        content_lesson = ContentLesson.objects.create(
                            lesson=lesson,
                            content_type='test_recap',
                            title_en=f"Test Recap: {lesson.title_en}",
                            title_fr=f"Test Récapitulatif: {lesson.title_fr}",
                            title_es=f"Test de Repaso: {lesson.title_es}",
                            title_nl=f"Test Overzicht: {lesson.title_nl}",
                            instruction_en="This test covers all topics from this lesson. Complete all sections to review your understanding.",
                            instruction_fr="Ce test couvre tous les sujets de cette leçon. Complétez toutes les sections pour revoir votre compréhension.",
                            instruction_es="Esta prueba abarca todos los temas de esta lección. Complete todas las secciones para revisar su comprensión.",
                            instruction_nl="Deze test behandelt alle onderwerpen van deze les. Voltooi alle secties om je begrip te herzien.",
                            estimated_duration=30,
                            order=99  # High order so it appears at the end
                        )
                        self.stdout.write(f'Created content lesson for test recap: {content_lesson.id}')
                    
                    # Create or update the test recap
                    if existing_recap and force:
                        test_recap = existing_recap
                        test_recap.questions.all().delete()  # Remove old questions
                        self.stdout.write(f'Updating existing test recap: {test_recap.id}')
                    else:
                        test_recap = TestRecap.objects.create(
                            lesson=lesson,
                            title=f"Test Recap: {lesson.title_en}",
                            title_en=f"Test Recap: {lesson.title_en}",
                            title_fr=f"Test Récapitulatif: {lesson.title_fr}",
                            title_es=f"Test de Repaso: {lesson.title_es}",
                            title_nl=f"Test Overzicht: {lesson.title_nl}",
                            question=f"Test Recap for {lesson.title_en}",  # Legacy field
                            description_en="Test your knowledge of the concepts covered in this lesson.",
                            description_fr="Testez vos connaissances sur les concepts abordés dans cette leçon.",
                            description_es="Pruebe su conocimiento de los conceptos cubiertos en esta lección.",
                            description_nl="Test uw kennis van de concepten die in deze les worden behandeld.",
                            passing_score=0.7,
                            time_limit=600,  # 10 minutes
                            is_active=True
                        )
                        self.stdout.write(f'Created new test recap: {test_recap.id}')
                    
                    # Find existing exercise content to use in questions
                    content_lessons = ContentLesson.objects.filter(lesson=lesson).exclude(content_type='test_recap')
                    
                    # Create questions for multiple choice
                    multiple_choice_qs = MultipleChoiceQuestion.objects.filter(
                        content_lesson__in=content_lessons
                    ).order_by('?')[:2]
                    
                    # Create questions for fill blank
                    fill_blank_qs = FillBlankExercise.objects.filter(
                        content_lesson__in=content_lessons
                    ).order_by('?')[:2]
                    
                    # Create questions for matching
                    matching_qs = MatchingExercise.objects.filter(
                        content_lesson__in=content_lessons
                    ).order_by('?')[:1]
                    
                    # Create questions for vocabulary
                    vocab_qs = VocabularyList.objects.filter(
                        content_lesson__in=content_lessons
                    ).order_by('?')[:3]
                    
                    # Add questions to test recap
                    question_order = 1
                    
                    # Add multiple choice questions
                    for mcq in multiple_choice_qs:
                        TestRecapQuestion.objects.create(
                            test_recap=test_recap,
                            question_type='multiple_choice',
                            multiple_choice_id=mcq.id,
                            order=question_order,
                            points=10
                        )
                        question_order += 1
                    
                    # Add fill blank questions
                    for fbe in fill_blank_qs:
                        TestRecapQuestion.objects.create(
                            test_recap=test_recap,
                            question_type='fill_blank',
                            fill_blank_id=fbe.id,
                            order=question_order,
                            points=15
                        )
                        question_order += 1
                    
                    # Add matching questions
                    for me in matching_qs:
                        TestRecapQuestion.objects.create(
                            test_recap=test_recap,
                            question_type='matching',
                            matching_id=me.id,
                            order=question_order,
                            points=20
                        )
                        question_order += 1
                    
                    # Add vocabulary questions
                    for vl in vocab_qs:
                        TestRecapQuestion.objects.create(
                            test_recap=test_recap,
                            question_type='vocabulary',
                            vocabulary_id=vl.id,
                            order=question_order,
                            points=10
                        )
                        question_order += 1
                    
                    # If we didn't find any real content, create dummy questions
                    if test_recap.questions.count() == 0:
                        self.stdout.write(f'No content found for lesson {lesson.id}, creating dummy questions')
                        
                        # Create dummy multiple choice question
                        TestRecapQuestion.objects.create(
                            test_recap=test_recap,
                            question_type='multiple_choice',
                            order=1,
                            points=10
                        )
                        
                        # Create dummy fill blank question
                        TestRecapQuestion.objects.create(
                            test_recap=test_recap,
                            question_type='fill_blank',
                            order=2,
                            points=15
                        )
                        
                        # Create dummy matching question
                        TestRecapQuestion.objects.create(
                            test_recap=test_recap,
                            question_type='matching',
                            order=3,
                            points=20
                        )
                    
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully created/updated test recap for lesson {lesson.id} with {test_recap.questions.count()} questions'
                    ))
            
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'Error processing lesson {lesson.id}: {str(e)}'))
        
        # Print summary
        self.stdout.write(self.style.SUCCESS(
            f'Finished! Created/updated {created_count} test recaps, skipped {skipped_count}, encountered {error_count} errors'
        ))