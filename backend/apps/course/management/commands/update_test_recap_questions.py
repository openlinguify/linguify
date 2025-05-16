import logging
import random
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.course.models import (
    Lesson, 
    ContentLesson, 
    TestRecap, 
    TestRecapQuestion,
    MultipleChoiceQuestion,
    FillBlankExercise,
    MatchingExercise,
    VocabularyList,
    SpeakingExercise,
    ExerciseGrammarReordering
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Updates test recap questions to link them to actual content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test_recap_id',
            type=int,
            help='ID of the test recap to update'
        )
        parser.add_argument(
            '--fill_missing_content',
            action='store_true',
            help='Fill missing content IDs with actual content'
        )
        parser.add_argument(
            '--force_rebuild',
            action='store_true',
            help='Completely rebuild the test recap questions (deletes existing questions)'
        )

    def handle(self, *args, **options):
        test_recap_id = options.get('test_recap_id')
        fill_missing_content = options.get('fill_missing_content')
        force_rebuild = options.get('force_rebuild')
        
        if not test_recap_id:
            self.stdout.write(self.style.ERROR('You must provide a test_recap_id'))
            return
            
        try:
            test_recap = TestRecap.objects.get(id=test_recap_id)
            self.stdout.write(f'Found test recap: {test_recap.id} - {test_recap.title}')
            
            # Get associated lesson
            lesson = test_recap.lesson
            if not lesson:
                self.stdout.write(self.style.ERROR(f'Test recap {test_recap_id} has no associated lesson'))
                return
                
            self.stdout.write(f'Associated lesson: {lesson.id} - {lesson.title_en}')
            
            # Get existing questions
            existing_questions = list(test_recap.questions.all().order_by('order'))
            self.stdout.write(f'Test recap has {len(existing_questions)} questions')
            
            # Check if there are questions without content
            missing_content_questions = []
            for q in existing_questions:
                has_content = (
                    q.multiple_choice_id or
                    q.fill_blank_id or
                    q.matching_id or
                    q.reordering_id or
                    q.speaking_id or
                    q.vocabulary_id
                )
                if not has_content:
                    missing_content_questions.append(q)
                    
            if missing_content_questions:
                self.stdout.write(f'Found {len(missing_content_questions)} questions without content')
            else:
                self.stdout.write('All questions have content IDs assigned')
                if not force_rebuild:
                    self.stdout.write('Nothing to do. Use --force_rebuild to rebuild all questions.')
                    return
            
            # If force rebuild, delete all existing questions
            if force_rebuild:
                self.stdout.write('Force rebuilding all questions...')
                with transaction.atomic():
                    test_recap.questions.all().delete()
                    existing_questions = []
                    missing_content_questions = []
            
            # If fill_missing_content, update questions without content
            if fill_missing_content or force_rebuild:
                # Find content lessons for this lesson (excluding test_recap type)
                content_lessons = ContentLesson.objects.filter(lesson=lesson).exclude(content_type='test_recap')
                
                if not content_lessons.exists():
                    self.stdout.write(self.style.WARNING(f'No content lessons found for lesson {lesson.id}'))
                    # Find random content from other lessons to use as examples
                    self.stdout.write('Looking for content from other lessons...')
                    
                    # Find available content of each type
                    multiple_choice_qs = MultipleChoiceQuestion.objects.order_by('?')[:5]
                    fill_blank_qs = FillBlankExercise.objects.order_by('?')[:5]
                    matching_qs = MatchingExercise.objects.order_by('?')[:2]
                    vocabulary_qs = VocabularyList.objects.order_by('?')[:5]
                    speaking_qs = SpeakingExercise.objects.order_by('?')[:2]
                    reordering_qs = ExerciseGrammarReordering.objects.order_by('?')[:1]
                    
                    self.stdout.write(f'Found {multiple_choice_qs.count()} multiple choice, '
                                     f'{fill_blank_qs.count()} fill blank, '
                                     f'{matching_qs.count()} matching, '
                                     f'{vocabulary_qs.count()} vocabulary, '
                                     f'{speaking_qs.count()} speaking, '
                                     f'{reordering_qs.count()} reordering questions')
                else:
                    self.stdout.write(f'Found {content_lessons.count()} content lessons for lesson {lesson.id}')
                    
                    # Get content for each type
                    multiple_choice_qs = MultipleChoiceQuestion.objects.filter(
                        content_lesson__in=content_lessons
                    ).order_by('?')[:5]
                    
                    fill_blank_qs = FillBlankExercise.objects.filter(
                        content_lesson__in=content_lessons
                    ).order_by('?')[:5]
                    
                    matching_qs = MatchingExercise.objects.filter(
                        content_lesson__in=content_lessons
                    ).order_by('?')[:2]
                    
                    vocabulary_qs = VocabularyList.objects.filter(
                        content_lesson__in=content_lessons
                    ).order_by('?')[:5]
                    
                    speaking_qs = SpeakingExercise.objects.filter(
                        content_lesson__in=content_lessons
                    ).order_by('?')[:2]
                    
                    reordering_qs = ExerciseGrammarReordering.objects.filter(
                        content_lesson__in=content_lessons
                    ).order_by('?')[:1]
                    
                    self.stdout.write(f'Found {multiple_choice_qs.count()} multiple choice, '
                                     f'{fill_blank_qs.count()} fill blank, '
                                     f'{matching_qs.count()} matching, '
                                     f'{vocabulary_qs.count()} vocabulary, '
                                     f'{speaking_qs.count()} speaking, '
                                     f'{reordering_qs.count()} reordering questions')
                
                # Build content pools for each type
                content_pools = {
                    'multiple_choice': list(multiple_choice_qs),
                    'fill_blank': list(fill_blank_qs),
                    'matching': list(matching_qs),
                    'vocabulary': list(vocabulary_qs),
                    'speaking': list(speaking_qs),
                    'reordering': list(reordering_qs),
                }
                
                # Replace dummy questions with real content
                with transaction.atomic():
                    for question in missing_content_questions:
                        # Get content from appropriate pool based on question type
                        question_type = question.question_type
                        content_pool = content_pools.get(question_type, [])
                        
                        if not content_pool:
                            self.stdout.write(f'No content available for question type: {question_type}')
                            continue
                        
                        # Select a random item from the pool
                        content_item = content_pool.pop(0) if content_pool else None
                        
                        if not content_item:
                            self.stdout.write(f'Pool empty for question type: {question_type}')
                            continue
                        
                        # Update the question with content
                        self.stdout.write(f'Updating question {question.id} of type {question_type} with content {content_item.id}')
                        
                        if question_type == 'multiple_choice':
                            question.multiple_choice_id = content_item.id
                        elif question_type == 'fill_blank':
                            question.fill_blank_id = content_item.id
                        elif question_type == 'matching':
                            question.matching_id = content_item.id
                        elif question_type == 'vocabulary':
                            question.vocabulary_id = content_item.id
                        elif question_type == 'speaking':
                            question.speaking_id = content_item.id
                        elif question_type == 'reordering':
                            question.reordering_id = content_item.id
                        
                        question.save()
                    
                    # If force_rebuild, create a balanced set of questions
                    if force_rebuild:
                        self.create_balanced_questions(test_recap, content_pools)
                        
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated test recap questions for test recap {test_recap_id}'))
            
        except TestRecap.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Test recap with ID {test_recap_id} not found'))
    
    def create_balanced_questions(self, test_recap, content_pools):
        """Create a balanced set of questions for the test recap"""
        question_order = 1
        
        # Add multiple choice questions (30%)
        mc_pool = content_pools.get('multiple_choice', [])
        for mc in mc_pool[:3]:
            TestRecapQuestion.objects.create(
                test_recap=test_recap,
                question_type='multiple_choice',
                multiple_choice_id=mc.id,
                order=question_order,
                points=10
            )
            question_order += 1
        
        # Add fill blank questions (20%)
        fb_pool = content_pools.get('fill_blank', [])
        for fb in fb_pool[:2]:
            TestRecapQuestion.objects.create(
                test_recap=test_recap,
                question_type='fill_blank',
                fill_blank_id=fb.id,
                order=question_order,
                points=15
            )
            question_order += 1
        
        # Add matching questions (10%)
        match_pool = content_pools.get('matching', [])
        for match in match_pool[:1]:
            TestRecapQuestion.objects.create(
                test_recap=test_recap,
                question_type='matching',
                matching_id=match.id,
                order=question_order,
                points=20
            )
            question_order += 1
        
        # Add vocabulary questions (30%)
        vocab_pool = content_pools.get('vocabulary', [])
        for vocab in vocab_pool[:3]:
            TestRecapQuestion.objects.create(
                test_recap=test_recap,
                question_type='vocabulary',
                vocabulary_id=vocab.id,
                order=question_order,
                points=10
            )
            question_order += 1
        
        # Add speaking questions (5%)
        speak_pool = content_pools.get('speaking', [])
        for speak in speak_pool[:1]:
            TestRecapQuestion.objects.create(
                test_recap=test_recap,
                question_type='speaking',
                speaking_id=speak.id,
                order=question_order,
                points=15
            )
            question_order += 1
        
        # Add reordering questions (5%)
        reorder_pool = content_pools.get('reordering', [])
        for reorder in reorder_pool[:1]:
            TestRecapQuestion.objects.create(
                test_recap=test_recap,
                question_type='reordering',
                reordering_id=reorder.id,
                order=question_order,
                points=15
            )
            question_order += 1