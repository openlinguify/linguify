"""
Management command to generate test recaps based on vocabulary in lessons.
This command creates more comprehensive test recaps that incorporate vocabulary from lessons.

Run with: python manage.py generate_vocabulary_test_recaps [--lesson_id ID] [--limit N] [--force]
"""
import logging
import random
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, Q
from django.utils.text import slugify

from apps.course.models import (
    Lesson, 
    ContentLesson, 
    TestRecap, 
    TestRecapQuestion,
    VocabularyList,
    MultipleChoiceQuestion,
    FillBlankExercise,
    MatchingExercise,
    ExerciseGrammarReordering,
    SpeakingExercise,
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generates test recaps based on vocabulary content in lessons'

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
            # Get lessons that have vocabulary content (for better test generation)
            lessons = Lesson.objects.filter(
                content_lessons__content_type__iexact='vocabularylist'
            ).annotate(
                vocab_count=Count('content_lessons__vocabulary_lists')
            ).filter(
                vocab_count__gt=0
            ).distinct().order_by('?')[:limit]

        if not lessons:
            self.stdout.write(self.style.WARNING('No lessons found with vocabulary content'))
            return

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
                            description_en="Test your knowledge of all the vocabulary and concepts covered in this lesson.",
                            description_fr="Testez vos connaissances sur tout le vocabulaire et les concepts abordés dans cette leçon.",
                            description_es="Pruebe su conocimiento de todo el vocabulario y los conceptos cubiertos en esta lección.",
                            description_nl="Test uw kennis van alle woordenschat en concepten die in deze les worden behandeld.",
                            passing_score=0.7,
                            time_limit=600,  # 10 minutes
                            is_active=True
                        )
                        self.stdout.write(f'Created new test recap: {test_recap.id}')
                    
                    # Get all content lessons for this lesson
                    content_lessons = ContentLesson.objects.filter(lesson=lesson)
                    
                    # Get all vocabulary items for this lesson
                    vocabulary_items = VocabularyList.objects.filter(
                        content_lesson__in=content_lessons
                    )
                    
                    if not vocabulary_items.exists():
                        self.stdout.write(self.style.WARNING(f'No vocabulary found for lesson {lesson.id}, skipping'))
                        skipped_count += 1
                        continue

                    # 1. Generate vocabulary-based multiple choice questions
                    self.generate_multiple_choice_questions(
                        test_recap=test_recap, 
                        vocabulary_items=vocabulary_items, 
                        content_lessons=content_lessons
                    )
                    
                    # 2. Generate fill-in-the-blank exercises
                    self.generate_fill_blank_exercises(
                        test_recap=test_recap, 
                        vocabulary_items=vocabulary_items, 
                        content_lessons=content_lessons
                    )
                    
                    # 3. Generate or use matching exercises
                    self.generate_matching_exercises(
                        test_recap=test_recap, 
                        vocabulary_items=vocabulary_items, 
                        content_lessons=content_lessons
                    )
                    
                    # 4. Add existing reordering exercises if available
                    reordering_exercises = ExerciseGrammarReordering.objects.filter(
                        content_lesson__in=content_lessons
                    ).order_by('?')[:1]
                    
                    for reorder in reordering_exercises:
                        TestRecapQuestion.objects.create(
                            test_recap=test_recap,
                            question_type='reordering',
                            reordering_id=reorder.id,
                            order=test_recap.questions.count() + 1,
                            points=2
                        )
                    
                    # 5. Add speaking exercises if available
                    speaking_exercises = SpeakingExercise.objects.filter(
                        content_lesson__in=content_lessons
                    ).order_by('?')[:1]
                    
                    for speaking in speaking_exercises:
                        TestRecapQuestion.objects.create(
                            test_recap=test_recap,
                            question_type='speaking',
                            speaking_id=speaking.id,
                            order=test_recap.questions.count() + 1,
                            points=2
                        )
                    
                    # 6. Add direct vocabulary questions
                    self.generate_vocabulary_questions(
                        test_recap=test_recap, 
                        vocabulary_items=vocabulary_items
                    )
                    
                    # Check if we have enough questions
                    if test_recap.questions.count() < 5:
                        self.stdout.write(self.style.WARNING(
                            f'Lesson {lesson.id} test recap has only {test_recap.questions.count()} questions. Adding more...'
                        ))
                        # Add more direct vocabulary items to ensure adequate coverage
                        remaining_vocab = vocabulary_items.exclude(
                            id__in=[q.vocabulary_id for q in test_recap.questions.filter(
                                question_type='vocabulary', vocabulary_id__isnull=False
                            )]
                        )
                        
                        for vocab in remaining_vocab:
                            # Don't add too many
                            if test_recap.questions.count() >= 10:
                                break
                                
                            TestRecapQuestion.objects.create(
                                test_recap=test_recap,
                                question_type='vocabulary',
                                vocabulary_id=vocab.id,
                                order=test_recap.questions.count() + 1,
                                points=1
                            )
                    
                    # Reorder questions to ensure a logical flow from easiest to hardest
                    self.reorder_questions(test_recap)
                    
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
    
    def generate_multiple_choice_questions(self, test_recap, vocabulary_items, content_lessons):
        """Generate multiple choice questions based on vocabulary or use existing ones."""
        # First check for existing ones
        existing_mcqs = MultipleChoiceQuestion.objects.filter(
            content_lesson__in=content_lessons
        ).order_by('?')[:3]
        
        # Add existing questions first
        for mcq in existing_mcqs:
            TestRecapQuestion.objects.create(
                test_recap=test_recap,
                question_type='multiple_choice',
                multiple_choice_id=mcq.id,
                order=test_recap.questions.count() + 1,
                points=10
            )
            
        # If we have fewer than 2 MCQs, generate new ones based on vocabulary
        if existing_mcqs.count() < 2 and vocabulary_items.count() >= 4:
            # Pick random vocabulary items
            vocab_list = list(vocabulary_items.order_by('?')[:4])
            
            # Create a new MCQ for each target language
            for lang in ['en', 'fr', 'es', 'nl']:
                target_lang_name = {
                    'en': 'English',
                    'fr': 'French',
                    'es': 'Spanish',
                    'nl': 'Dutch'
                }[lang]
                
                # Use first item as correct answer
                correct_item = vocab_list[0]
                distractors = vocab_list[1:4]
                
                # Create a question about the meaning of a word
                question_templates = {
                    'en': f"What is the {target_lang_name} word for '{correct_item.get_translation('en')}'?",
                    'fr': f"Quel est le mot {target_lang_name.lower()} pour '{correct_item.get_translation('fr')}'?",
                    'es': f"¿Cuál es la palabra {target_lang_name.lower()} para '{correct_item.get_translation('es')}'?",
                    'nl': f"Wat is het {target_lang_name.lower()} woord voor '{correct_item.get_translation('nl')}'?"
                }
                
                # Create question for a parent content lesson
                parent_content_lesson = content_lessons.filter(content_type__iexact='vocabularylist').first()
                if not parent_content_lesson:
                    parent_content_lesson = content_lessons.first()
                
                if parent_content_lesson:
                    # Create the multiple choice question in the database
                    mcq = MultipleChoiceQuestion.objects.create(
                        content_lesson=parent_content_lesson,
                        question_en=question_templates['en'],
                        question_fr=question_templates['fr'],
                        question_es=question_templates['es'],
                        question_nl=question_templates['nl'],
                        correct_answer_en=getattr(correct_item, f'word_en'),
                        correct_answer_fr=getattr(correct_item, f'word_fr'),
                        correct_answer_es=getattr(correct_item, f'word_es'),
                        correct_answer_nl=getattr(correct_item, f'word_nl'),
                        fake_answer1_en=getattr(distractors[0], f'word_en'),
                        fake_answer1_fr=getattr(distractors[0], f'word_fr'),
                        fake_answer1_es=getattr(distractors[0], f'word_es'),
                        fake_answer1_nl=getattr(distractors[0], f'word_nl'),
                        fake_answer2_en=getattr(distractors[1], f'word_en'),
                        fake_answer2_fr=getattr(distractors[1], f'word_fr'),
                        fake_answer2_es=getattr(distractors[1], f'word_es'),
                        fake_answer2_nl=getattr(distractors[1], f'word_nl'),
                        fake_answer3_en=getattr(distractors[2], f'word_en'),
                        fake_answer3_fr=getattr(distractors[2], f'word_fr'),
                        fake_answer3_es=getattr(distractors[2], f'word_es'),
                        fake_answer3_nl=getattr(distractors[2], f'word_nl'),
                        fake_answer4_en=getattr(distractors[0], f'word_en'),
                        fake_answer4_fr=getattr(distractors[0], f'word_fr'),
                        fake_answer4_es=getattr(distractors[0], f'word_es'),
                        fake_answer4_nl=getattr(distractors[0], f'word_nl'),
                        hint_answer_en=f"Think about {correct_item.get_definition('en')}",
                        hint_answer_fr=f"Pensez à {correct_item.get_definition('fr')}",
                        hint_answer_es=f"Piense en {correct_item.get_definition('es')}",
                        hint_answer_nl=f"Denk aan {correct_item.get_definition('nl')}"
                    )
                    
                    # Add this new MCQ to the test recap
                    TestRecapQuestion.objects.create(
                        test_recap=test_recap,
                        question_type='multiple_choice',
                        multiple_choice_id=mcq.id,
                        order=test_recap.questions.count() + 1,
                        points=10
                    )
    
    def generate_fill_blank_exercises(self, test_recap, vocabulary_items, content_lessons):
        """Generate fill-in-the-blank exercises from vocabulary or use existing ones."""
        # Check for existing fill blank exercises
        existing_fbes = FillBlankExercise.objects.filter(
            content_lesson__in=content_lessons
        ).order_by('?')[:2]
        
        # Add existing ones first
        for fbe in existing_fbes:
            TestRecapQuestion.objects.create(
                test_recap=test_recap,
                question_type='fill_blank',
                fill_blank_id=fbe.id,
                order=test_recap.questions.count() + 1,
                points=15
            )
        
        # If fewer than 2 and we have vocabulary with example sentences, create new ones
        if existing_fbes.count() < 2 and vocabulary_items.exists():
            # Find vocabulary items with example sentences
            vocab_with_examples = vocabulary_items.filter(
                Q(example_sentence_en__isnull=False) & ~Q(example_sentence_en='')
            ).order_by('?')[:2]
            
            # Create a new fill-in-the-blank exercise for each
            for vocab in vocab_with_examples:
                # Create a parent content lesson
                parent_content_lesson = content_lessons.filter(content_type__iexact='fill_blank').first()
                if not parent_content_lesson:
                    parent_content_lesson = content_lessons.first()
                
                if parent_content_lesson and vocab.example_sentence_en:
                    # Prepare sentences with blanks by replacing the target word with ___
                    sentences = {}
                    for lang in ['en', 'fr', 'es', 'nl']:
                        example_field = f'example_sentence_{lang}'
                        word_field = f'word_{lang}'
                        
                        example = getattr(vocab, example_field, '')
                        word = getattr(vocab, word_field, '')
                        
                        if example and word:
                            # Replace word with blank, case-insensitive
                            sentence = re.sub(
                                r'\b' + re.escape(word) + r'\b', 
                                '___', 
                                example, 
                                flags=re.IGNORECASE
                            )
                            sentences[lang] = sentence
                    
                    # If we successfully created sentences with blanks
                    if sentences:
                        # Generate options (correct + 3 distractors)
                        options = {}
                        correct_answers = {}
                        
                        for lang in ['en', 'fr', 'es', 'nl']:
                            if lang in sentences:
                                # Correct answer
                                correct_answers[lang] = getattr(vocab, f'word_{lang}')
                                
                                # Options: correct answer + 3 random words from other vocab items
                                distractors = list(vocabulary_items.exclude(id=vocab.id).order_by('?')[:3])
                                option_list = [getattr(vocab, f'word_{lang}')]
                                
                                for distractor in distractors:
                                    option_list.append(getattr(distractor, f'word_{lang}'))
                                
                                # Shuffle options
                                random.shuffle(option_list)
                                options[lang] = option_list
                        
                        # Create instruction text
                        instructions = {
                            'en': "Choose the correct word to fill in the blank.",
                            'fr': "Choisissez le mot correct pour remplir le blanc.",
                            'es': "Elija la palabra correcta para completar el espacio en blanco.",
                            'nl': "Kies het juiste woord om de lege ruimte in te vullen."
                        }
                        
                        # Create hints based on word definitions
                        hints = {}
                        for lang in ['en', 'fr', 'es', 'nl']:
                            if lang in sentences:
                                hints[lang] = f"Hint: {getattr(vocab, f'definition_{lang}')}"
                        
                        # Create the fill-in-the-blank exercise
                        fbe = FillBlankExercise.objects.create(
                            content_lesson=parent_content_lesson,
                            order=FillBlankExercise.objects.filter(content_lesson=parent_content_lesson).count() + 1,
                            instructions=instructions,
                            sentences=sentences,
                            answer_options=options,
                            correct_answers=correct_answers,
                            hints=hints
                        )
                        
                        # Add to test recap
                        TestRecapQuestion.objects.create(
                            test_recap=test_recap,
                            question_type='fill_blank',
                            fill_blank_id=fbe.id,
                            order=test_recap.questions.count() + 1,
                            points=15
                        )
    
    def generate_matching_exercises(self, test_recap, vocabulary_items, content_lessons):
        """Use existing matching exercises or create new ones for the test recap."""
        # First look for existing matching exercises
        existing_matches = MatchingExercise.objects.filter(
            content_lesson__in=content_lessons
        ).order_by('?')[:1]
        
        # Add existing ones first
        for match in existing_matches:
            # Check if it has vocabulary words
            if match.vocabulary_words.exists():
                TestRecapQuestion.objects.create(
                    test_recap=test_recap,
                    question_type='matching',
                    matching_id=match.id,
                    order=test_recap.questions.count() + 1,
                    points=20
                )
            else:
                # Associate vocabulary with this matching exercise
                vocab_to_associate = vocabulary_items.order_by('?')[:match.pairs_count or 6]
                for vocab in vocab_to_associate:
                    match.vocabulary_words.add(vocab)
                
                # Now add it to the test
                TestRecapQuestion.objects.create(
                    test_recap=test_recap,
                    question_type='matching',
                    matching_id=match.id,
                    order=test_recap.questions.count() + 1,
                    points=20
                )
        
        # If no existing matching exercises, create a new one
        if not existing_matches.exists() and vocabulary_items.count() >= 4:
            # Create a parent content lesson or find matching-type one
            parent_content_lesson = content_lessons.filter(content_type__iexact='matching').first()
            if not parent_content_lesson:
                parent_content_lesson = content_lessons.first()
            
            if parent_content_lesson:
                # Create new matching exercise
                match = MatchingExercise.objects.create(
                    content_lesson=parent_content_lesson,
                    title_en="Match the words with their translations",
                    title_fr="Associez les mots avec leurs traductions",
                    title_es="Relacione las palabras con sus traducciones",
                    title_nl="Koppel de woorden aan hun vertalingen",
                    difficulty="medium",
                    pairs_count=min(8, vocabulary_items.count()),
                    order=MatchingExercise.objects.filter(content_lesson=parent_content_lesson).count() + 1
                )
                
                # Associate vocabulary with this matching exercise
                vocab_to_associate = vocabulary_items.order_by('?')[:match.pairs_count]
                for vocab in vocab_to_associate:
                    match.vocabulary_words.add(vocab)
                
                # Add to test recap
                TestRecapQuestion.objects.create(
                    test_recap=test_recap,
                    question_type='matching',
                    matching_id=match.id,
                    order=test_recap.questions.count() + 1,
                    points=20
                )
    
    def generate_vocabulary_questions(self, test_recap, vocabulary_items):
        """Add raw vocabulary questions to test recall."""
        # Select up to 3 vocabulary items not already included in other questions
        used_vocab_ids = []
        for question in test_recap.questions.all():
            if question.vocabulary_id:
                used_vocab_ids.append(question.vocabulary_id)
        
        remaining_vocab = vocabulary_items.exclude(id__in=used_vocab_ids).order_by('?')[:3]
        
        # Add each vocabulary item as a direct question
        for vocab in remaining_vocab:
            TestRecapQuestion.objects.create(
                test_recap=test_recap,
                question_type='vocabulary',
                vocabulary_id=vocab.id,
                order=test_recap.questions.count() + 1,
                points=10
            )
    
    def reorder_questions(self, test_recap):
        """Reorder questions to ensure a logical flow (easier to harder)."""
        # Determine the preferred order of question types by difficulty
        type_order = {
            'vocabulary': 1,  # Start with direct vocabulary
            'multiple_choice': 2,  # Then multiple choice
            'fill_blank': 3,  # Then fill-in-the-blank
            'matching': 4,  # Then matching
            'reordering': 5,  # Then sentence reordering  
            'speaking': 6,  # End with speaking (most interactive)
        }
        
        # Sort questions by their type order
        questions = test_recap.questions.all()
        sorted_questions = sorted(questions, key=lambda q: type_order.get(q.question_type, 99))
        
        # Update order fields
        for i, question in enumerate(sorted_questions, 1):
            question.order = i
            question.save()