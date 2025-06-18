"""
Management command to create a complete lesson structure with mixed content types.
This creates a single lesson with associated content lessons for vocabulary, matching,
speaking, reordering, and multiple choice exercises in one operation.

Usage:
python manage.py create_complete_lesson --unit-id 1 --title "My Complete Lesson" --vocabulary-file /path/to/vocab.csv
python manage.py create_complete_lesson --unit-id 1 --title "My Complete Lesson" --vocabulary-input "word1:definition1,word2:definition2"

Options:
--unit-id: Required. The Unit ID where to add the lesson
--title: Required. The title for the new lesson
--vocabulary-file: Path to a CSV file with vocabulary (format: word,definition,example,word_type)
--vocabulary-input: Direct input of vocabulary items in format "word:definition,word:definition"
--lesson-type: Type of lesson (vocabulary, grammar, culture, professional) [default: vocabulary]
--professional-field: Field code if lesson-type is professional
--create-matching: Create a matching exercise [default: True]
--create-speaking: Create a speaking exercise [default: True]
--create-reordering: Create a reordering exercise [default: True]
--create-multiple-choice: Create multiple choice questions [default: True]
--create-test-recap: Create a test recap [default: True]
--dry-run: Preview what would be created without making any changes
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.course.models import (
    Unit, Lesson, ContentLesson, VocabularyList, 
    MultipleChoiceQuestion, ExerciseGrammarReordering,
    MatchingExercise, SpeakingExercise, TestRecap, 
    generate_test_recap
)
import csv
import io
import random
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create a complete lesson structure with mixed content types'

    def add_arguments(self, parser):
        parser.add_argument('--unit-id', type=int, required=True, help='The Unit ID where to add the lesson')
        parser.add_argument('--title', type=str, required=True, help='Title for the new lesson')
        parser.add_argument('--vocabulary-file', type=str, help='Path to CSV file with vocabulary')
        parser.add_argument('--vocabulary-input', type=str, help='Direct input of vocabulary items (word:definition,word:definition)')
        parser.add_argument('--lesson-type', type=str, default='vocabulary', 
                            choices=['vocabulary', 'grammar', 'culture', 'professional'],
                            help='Type of lesson')
        parser.add_argument('--professional-field', type=str, help='Professional field code (required if lesson-type is professional)')
        parser.add_argument('--create-matching', action='store_true', default=True, help='Create matching exercise')
        parser.add_argument('--create-speaking', action='store_true', default=True, help='Create speaking exercise')
        parser.add_argument('--create-reordering', action='store_true', default=True, help='Create reordering exercise')
        parser.add_argument('--create-multiple-choice', action='store_true', default=True, help='Create multiple choice questions')
        parser.add_argument('--create-test-recap', action='store_true', default=True, help='Create test recap')
        parser.add_argument('--dry-run', action='store_true', help='Preview without creating')

    def handle(self, *args, **options):
        # Extract arguments
        unit_id = options['unit_id']
        title = options['title']
        vocabulary_file = options.get('vocabulary_file')
        vocabulary_input = options.get('vocabulary_input')
        lesson_type = options['lesson_type']
        professional_field = options.get('professional_field')
        create_matching = options['create_matching']
        create_speaking = options['create_speaking']
        create_reordering = options['create_reordering']
        create_multiple_choice = options['create_multiple_choice']
        create_test_recap = options['create_test_recap']
        dry_run = options['dry_run']

        # Validate arguments
        if not (vocabulary_file or vocabulary_input):
            raise CommandError('Either --vocabulary-file or --vocabulary-input must be provided')
        
        if lesson_type == 'professional' and not professional_field:
            raise CommandError('--professional-field is required when --lesson-type is professional')
        
        try:
            unit = Unit.objects.get(id=unit_id)
        except Unit.DoesNotExist:
            raise CommandError(f'Unit with ID {unit_id} does not exist')
            
        # Parse vocabulary
        try:
            vocabulary_items = self.parse_vocabulary(vocabulary_file, vocabulary_input)
        except Exception as e:
            raise CommandError(f'Error parsing vocabulary: {str(e)}')
        
        if not vocabulary_items:
            raise CommandError('No valid vocabulary items found')
            
        # Display preview header if in dry-run mode
        if dry_run:
            self.stdout.write(self.style.WARNING('\n=== DRY RUN MODE - Nothing will be created ===\n'))
        
        # Main execution in a transaction (if not dry run)
        if dry_run:
            self.preview_creation(unit, title, lesson_type, professional_field, vocabulary_items, 
                                create_matching, create_speaking, create_reordering, 
                                create_multiple_choice, create_test_recap)
        else:
            try:
                with transaction.atomic():
                    self.create_lesson_structure(unit, title, lesson_type, professional_field, vocabulary_items, 
                                               create_matching, create_speaking, create_reordering, 
                                               create_multiple_choice, create_test_recap)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating lesson structure: {str(e)}'))
                raise
    
    def parse_vocabulary(self, file_path, direct_input):
        """
        Parse vocabulary from either a CSV file or direct input
        Returns list of dictionaries with vocabulary information
        """
        vocabulary = []
        
        if file_path:
            if not os.path.exists(file_path):
                raise CommandError(f'File not found: {file_path}')
                
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip header
                
                for row in reader:
                    if len(row) >= 2:  # At least word and definition
                        item = {
                            'word_en': row[0].strip(),
                            'definition_en': row[1].strip(),
                            'example_sentence_en': row[2].strip() if len(row) > 2 else '',
                            'word_type_en': row[3].strip() if len(row) > 3 else 'noun',
                            # Default values for other languages
                            'word_fr': row[0].strip() + ' (FR)',
                            'definition_fr': row[1].strip() + ' (FR)',
                            'example_sentence_fr': (row[2].strip() if len(row) > 2 else '') + ' (FR)',
                            'word_type_fr': (row[3].strip() if len(row) > 3 else 'noun') + ' (FR)',
                            'word_es': row[0].strip() + ' (ES)',
                            'definition_es': row[1].strip() + ' (ES)',
                            'example_sentence_es': (row[2].strip() if len(row) > 2 else '') + ' (ES)',
                            'word_type_es': (row[3].strip() if len(row) > 3 else 'noun') + ' (ES)',
                            'word_nl': row[0].strip() + ' (NL)',
                            'definition_nl': row[1].strip() + ' (NL)',
                            'example_sentence_nl': (row[2].strip() if len(row) > 2 else '') + ' (NL)',
                            'word_type_nl': (row[3].strip() if len(row) > 3 else 'noun') + ' (NL)',
                        }
                        vocabulary.append(item)
        
        elif direct_input:
            items = direct_input.split(',')
            for i, item_str in enumerate(items):
                if ':' in item_str:
                    word, definition = item_str.split(':', 1)
                    item = {
                        'word_en': word.strip(),
                        'definition_en': definition.strip(),
                        'example_sentence_en': f'Example sentence for {word.strip()}',
                        'word_type_en': 'noun',
                        # Default values for other languages
                        'word_fr': word.strip() + ' (FR)',
                        'definition_fr': definition.strip() + ' (FR)',
                        'example_sentence_fr': f'Example sentence for {word.strip()} (FR)',
                        'word_type_fr': 'nom',
                        'word_es': word.strip() + ' (ES)',
                        'definition_es': definition.strip() + ' (ES)',
                        'example_sentence_es': f'Example sentence for {word.strip()} (ES)',
                        'word_type_es': 'sustantivo',
                        'word_nl': word.strip() + ' (NL)',
                        'definition_nl': definition.strip() + ' (NL)',
                        'example_sentence_nl': f'Example sentence for {word.strip()} (NL)',
                        'word_type_nl': 'zelfstandig naamwoord',
                    }
                    vocabulary.append(item)
        
        return vocabulary
    
    def preview_creation(self, unit, title, lesson_type, professional_field, vocabulary_items, 
                       create_matching, create_speaking, create_reordering, 
                       create_multiple_choice, create_test_recap):
        """
        Preview what would be created without actually creating anything
        """
        self.stdout.write(self.style.SUCCESS('=== Creation Preview ==='))
        self.stdout.write(f'Unit: {unit} (ID: {unit.id})')
        self.stdout.write(f'New Lesson: "{title}" (Type: {lesson_type})')
        
        if professional_field:
            self.stdout.write(f'Professional Field: {professional_field}')
        
        self.stdout.write(f'\nVocabulary Items: {len(vocabulary_items)}')
        for i, item in enumerate(vocabulary_items[:3], 1):
            self.stdout.write(f"  {i}. {item['word_en']} - {item['definition_en']}")
        
        if len(vocabulary_items) > 3:
            self.stdout.write(f'  ... and {len(vocabulary_items) - 3} more items')
        
        self.stdout.write('\nContent Lessons to be created:')
        self.stdout.write('  1. Vocabulary List (Main)')
        
        content_count = 1
        if create_matching:
            content_count += 1
            self.stdout.write(f'  {content_count}. Matching Exercise')
        
        if create_speaking:
            content_count += 1
            self.stdout.write(f'  {content_count}. Speaking Exercise')
        
        if create_reordering:
            content_count += 1
            self.stdout.write(f'  {content_count}. Reordering Exercise')
        
        if create_multiple_choice:
            content_count += 1
            self.stdout.write(f'  {content_count}. Multiple Choice Questions')
        
        if create_test_recap:
            self.stdout.write('\nTest Recap will be created with questions from all exercise types.')
        
        self.stdout.write(self.style.SUCCESS('\nRun without --dry-run to create this lesson structure.'))
    
    def create_lesson_structure(self, unit, title, lesson_type, professional_field, vocabulary_items, 
                              create_matching, create_speaking, create_reordering, 
                              create_multiple_choice, create_test_recap):
        """
        Create the entire lesson structure in the database
        """
        self.stdout.write(self.style.SUCCESS('=== Creating Lesson Structure ==='))
        
        # Determine next lesson order in unit
        next_order = Lesson.objects.filter(unit=unit).order_by('-order').first()
        next_order = (next_order.order + 1) if next_order else 1
        
        # Create main lesson
        lesson = Lesson.objects.create(
            unit=unit,
            lesson_type=lesson_type,
            professional_field=professional_field if lesson_type == 'professional' else None,
            title_en=title,
            title_fr=f"{title} (FR)",
            title_es=f"{title} (ES)",
            title_nl=f"{title} (NL)",
            description_en=f"Complete lesson about {title}",
            description_fr=f"Leçon complète sur {title} (FR)",
            description_es=f"Lección completa sobre {title} (ES)",
            description_nl=f"Complete les over {title} (NL)",
            order=next_order,
            estimated_duration=len(vocabulary_items) * 2  # Estimate 2 minutes per vocabulary item
        )
        
        self.stdout.write(f'Created Lesson: {lesson.title_en} (ID: {lesson.id})')
        
        # Create content lessons
        content_order = 1
        
        # 1. Vocabulary content lesson (main)
        vocab_content = ContentLesson.objects.create(
            lesson=lesson,
            content_type='VocabularyList',
            title_en=f"{title} - Vocabulary",
            title_fr=f"{title} - Vocabulaire",
            title_es=f"{title} - Vocabulario",
            title_nl=f"{title} - Woordenschat",
            instruction_en="Learn the following vocabulary items",
            instruction_fr="Apprenez les mots de vocabulaire suivants",
            instruction_es="Aprende los siguientes elementos de vocabulario",
            instruction_nl="Leer de volgende woordenschatelementen",
            estimated_duration=len(vocabulary_items),
            order=content_order
        )
        content_order += 1
        
        self.stdout.write(f'Created Content Lesson: {vocab_content.title_en} (ID: {vocab_content.id})')
        
        # Add vocabulary items
        for item in vocabulary_items:
            vocab_item = VocabularyList.objects.create(
                content_lesson=vocab_content,
                **item
            )
            self.stdout.write(f'  Added vocabulary item: {vocab_item.word_en}')
        
        # 2. Create matching exercise if requested
        matching_content = None
        if create_matching and vocabulary_items:
            matching_content = ContentLesson.objects.create(
                lesson=lesson,
                content_type='Matching',
                title_en=f"{title} - Matching Exercise",
                title_fr=f"{title} - Exercice d'association",
                title_es=f"{title} - Ejercicio de emparejamiento",
                title_nl=f"{title} - Matching oefening",
                instruction_en="Match the words with their definitions",
                instruction_fr="Associez les mots à leurs définitions",
                instruction_es="Relaciona las palabras con sus definiciones",
                instruction_nl="Koppel de woorden aan hun definities",
                estimated_duration=5,
                order=content_order
            )
            content_order += 1
            
            # Create the matching exercise
            matching_exercise = MatchingExercise.objects.create(
                content_lesson=matching_content,
                title_en=f"Match the vocabulary from {title}",
                title_fr=f"Associez le vocabulaire de {title}",
                title_es=f"Relaciona el vocabulario de {title}",
                title_nl=f"Koppel de woordenschat van {title}",
                pairs_count=min(8, len(vocabulary_items)),  # Max 8 pairs
                difficulty='medium',
                order=1
            )
            
            # Add vocabulary items to matching exercise
            vocab_objects = VocabularyList.objects.filter(content_lesson=vocab_content)
            limit = min(matching_exercise.pairs_count, vocab_objects.count())
            for vocab in vocab_objects[:limit]:
                matching_exercise.vocabulary_words.add(vocab)
                
            self.stdout.write(f'Created Matching Exercise with {limit} pairs (ID: {matching_exercise.id})')
        
        # 3. Create speaking exercise if requested
        speaking_content = None
        if create_speaking and vocabulary_items:
            speaking_content = ContentLesson.objects.create(
                lesson=lesson,
                content_type='Speaking',
                title_en=f"{title} - Speaking Practice",
                title_fr=f"{title} - Pratique orale",
                title_es=f"{title} - Práctica oral",
                title_nl=f"{title} - Spreekoefening",
                instruction_en="Practice pronouncing these words",
                instruction_fr="Entraînez-vous à prononcer ces mots",
                instruction_es="Practica la pronunciación de estas palabras",
                instruction_nl="Oefen de uitspraak van deze woorden",
                estimated_duration=5,
                order=content_order
            )
            content_order += 1
            
            # Create the speaking exercise
            speaking_exercise = SpeakingExercise.objects.create(
                content_lesson=speaking_content
            )
            
            # Add vocabulary items to speaking exercise
            vocab_objects = VocabularyList.objects.filter(content_lesson=vocab_content)
            limit = min(5, vocab_objects.count())  # Limit to 5 vocabulary items
            for vocab in vocab_objects[:limit]:
                speaking_exercise.vocabulary_items.add(vocab)
                
            self.stdout.write(f'Created Speaking Exercise with {limit} words (ID: {speaking_exercise.id})')
        
        # 4. Create reordering exercise if requested
        reordering_content = None
        if create_reordering and vocabulary_items:
            reordering_content = ContentLesson.objects.create(
                lesson=lesson,
                content_type='Reordering',
                title_en=f"{title} - Sentence Reordering",
                title_fr=f"{title} - Réorganisation de phrases",
                title_es=f"{title} - Reordenamiento de frases",
                title_nl=f"{title} - Zinnen herschikken",
                instruction_en="Rearrange the words to form correct sentences",
                instruction_fr="Réorganisez les mots pour former des phrases correctes",
                instruction_es="Reorganiza las palabras para formar oraciones correctas",
                instruction_nl="Herorden de woorden om correcte zinnen te vormen",
                estimated_duration=5,
                order=content_order
            )
            content_order += 1
            
            # Create reordering exercises (one for each of the first 3 vocabulary items)
            vocab_objects = VocabularyList.objects.filter(content_lesson=vocab_content)
            limit = min(3, vocab_objects.count())
            
            for i, vocab in enumerate(vocab_objects[:limit]):
                # Create a sentence based on the example sentence
                sentence_en = vocab.example_sentence_en or f"This is an example sentence with {vocab.word_en}"
                sentence_fr = vocab.example_sentence_fr or f"Ceci est une phrase exemple avec {vocab.word_fr}"
                sentence_es = vocab.example_sentence_es or f"Esta es una frase de ejemplo con {vocab.word_es}"
                sentence_nl = vocab.example_sentence_nl or f"Dit is een voorbeeldzin met {vocab.word_nl}"
                
                reordering = ExerciseGrammarReordering.objects.create(
                    content_lesson=reordering_content,
                    sentence_en=sentence_en,
                    sentence_fr=sentence_fr,
                    sentence_es=sentence_es,
                    sentence_nl=sentence_nl,
                    explanation=f"This sentence demonstrates the use of '{vocab.word_en}'",
                    hint=f"Focus on the correct placement of '{vocab.word_en}'"
                )
                
                self.stdout.write(f'Created Reordering Exercise {i+1}: {reordering.sentence_en[:30]}...')
                
        # 5. Create multiple choice questions if requested
        multiple_choice_content = None
        if create_multiple_choice and vocabulary_items:
            multiple_choice_content = ContentLesson.objects.create(
                lesson=lesson,
                content_type='Multiple choice',
                title_en=f"{title} - Multiple Choice Questions",
                title_fr=f"{title} - Questions à choix multiples",
                title_es=f"{title} - Preguntas de opción múltiple",
                title_nl=f"{title} - Meerkeuzevragen",
                instruction_en="Choose the correct answer for each question",
                instruction_fr="Choisissez la bonne réponse pour chaque question",
                instruction_es="Elige la respuesta correcta para cada pregunta",
                instruction_nl="Kies het juiste antwoord voor elke vraag",
                estimated_duration=5,
                order=content_order
            )
            content_order += 1
            
            # Create multiple choice questions
            vocab_objects = VocabularyList.objects.filter(content_lesson=vocab_content)
            limit = min(5, vocab_objects.count())
            
            for i, vocab in enumerate(vocab_objects[:limit]):
                # Create a question based on the definition
                question_en = f"What is the meaning of '{vocab.word_en}'?"
                question_fr = f"Quelle est la signification de '{vocab.word_fr}'?"
                question_es = f"¿Cuál es el significado de '{vocab.word_es}'?"
                question_nl = f"Wat is de betekenis van '{vocab.word_nl}'?"
                
                # Get incorrect answers (different vocabulary items)
                incorrect_vocab = list(vocab_objects.exclude(id=vocab.id))
                if len(incorrect_vocab) >= 4:
                    incorrect_samples = random.sample(incorrect_vocab, 4)
                else:
                    # Pad with made-up answers if not enough vocabulary
                    incorrect_samples = incorrect_vocab + [None] * (4 - len(incorrect_vocab))
                
                # Create multiple choice question
                mc_question = MultipleChoiceQuestion.objects.create(
                    content_lesson=multiple_choice_content,
                    question_en=question_en,
                    question_fr=question_fr,
                    question_es=question_es,
                    question_nl=question_nl,
                    correct_answer_en=vocab.definition_en,
                    correct_answer_fr=vocab.definition_fr,
                    correct_answer_es=vocab.definition_es,
                    correct_answer_nl=vocab.definition_nl,
                    fake_answer1_en=incorrect_samples[0].definition_en if incorrect_samples[0] else "Incorrect answer 1",
                    fake_answer1_fr=incorrect_samples[0].definition_fr if incorrect_samples[0] else "Réponse incorrecte 1",
                    fake_answer1_es=incorrect_samples[0].definition_es if incorrect_samples[0] else "Respuesta incorrecta 1",
                    fake_answer1_nl=incorrect_samples[0].definition_nl if incorrect_samples[0] else "Onjuist antwoord 1",
                    fake_answer2_en=incorrect_samples[1].definition_en if incorrect_samples[1] else "Incorrect answer 2",
                    fake_answer2_fr=incorrect_samples[1].definition_fr if incorrect_samples[1] else "Réponse incorrecte 2",
                    fake_answer2_es=incorrect_samples[1].definition_es if incorrect_samples[1] else "Respuesta incorrecta 2",
                    fake_answer2_nl=incorrect_samples[1].definition_nl if incorrect_samples[1] else "Onjuist antwoord 2",
                    fake_answer3_en=incorrect_samples[2].definition_en if incorrect_samples[2] else "Incorrect answer 3",
                    fake_answer3_fr=incorrect_samples[2].definition_fr if incorrect_samples[2] else "Réponse incorrecte 3",
                    fake_answer3_es=incorrect_samples[2].definition_es if incorrect_samples[2] else "Respuesta incorrecta 3",
                    fake_answer3_nl=incorrect_samples[2].definition_nl if incorrect_samples[2] else "Onjuist antwoord 3",
                    fake_answer4_en=incorrect_samples[3].definition_en if incorrect_samples[3] else "Incorrect answer 4",
                    fake_answer4_fr=incorrect_samples[3].definition_fr if incorrect_samples[3] else "Réponse incorrecte 4",
                    fake_answer4_es=incorrect_samples[3].definition_es if incorrect_samples[3] else "Respuesta incorrecta 4",
                    fake_answer4_nl=incorrect_samples[3].definition_nl if incorrect_samples[3] else "Onjuist antwoord 4",
                    hint_answer_en=f"Think about the {vocab.word_type_en} '{vocab.word_en}'",
                    hint_answer_fr=f"Pensez au {vocab.word_type_fr} '{vocab.word_fr}'",
                    hint_answer_es=f"Piensa en el {vocab.word_type_es} '{vocab.word_es}'",
                    hint_answer_nl=f"Denk aan het {vocab.word_type_nl} '{vocab.word_nl}'"
                )
                
                self.stdout.write(f'Created Multiple Choice Question {i+1}: {mc_question.question_en}')
        
        # 6. Create test recap if requested
        if create_test_recap:
            # Use the built-in function to generate a balanced test recap
            test_recap = generate_test_recap(lesson)
            self.stdout.write(f'Created Test Recap: {test_recap.title_en} (ID: {test_recap.id})')
            self.stdout.write(f'  Questions: {test_recap.questions.count()}')
        
        # Final update of lesson's estimated duration
        total_duration = sum(cl.estimated_duration for cl in ContentLesson.objects.filter(lesson=lesson))
        lesson.estimated_duration = total_duration
        lesson.save()
        
        self.stdout.write(self.style.SUCCESS(f'\nComplete lesson structure created successfully!'))
        self.stdout.write(f'Lesson ID: {lesson.id}')
        self.stdout.write(f'Total Content Lessons: {content_order-1}')
        self.stdout.write(f'Total Duration: {lesson.estimated_duration} minutes')